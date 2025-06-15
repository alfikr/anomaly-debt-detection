
from concurrent import futures
import grpc
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import anomaly_pb2
import anomaly_pb2_grpc
import debt_model_loader as dml
from redis_util import RedisUtil as ru



class AnomalyDetector(anomaly_pb2_grpc.AnomalyServiceServicer):
    def __init__(self):
        try:
            self.model = joblib.load("anomaly_model.joblib")
            print("Model loaded successfully.")
        except Exception:
            print("Training new model...")
            x = dml.fetch_csv()
            print(x.columns)

            self.model = IsolationForest(contamination=0.01, random_state=42)
            self.model.fit(x[['amount_due', 'amount_paid', 'delay_days', 'paid_to_due_ratio']])
            joblib.dump(self.model, "anomaly_model.joblib")

    def Detect(self, request, context):
        redis_key = f"anomaly:feedback:{request.amount_due}:{request.amount_paid}:{request.delay_days}"
        label_key = f"anomaly:feedback-labeled:{request.amount_due}:{request.amount_paid}:{request.delay_days}"

        user_feedback = ru.get_data_redis(label_key)

        if user_feedback and 'user_label' in user_feedback:
            return anomaly_pb2.AnomalyResponse(
                anomaly_score=-99.99,
                is_anomaly=bool(user_feedback['user_label'])
            )
        
        cached_result = ru.get_data_redis(redis_key)
        if cached_result and 'model_score' in cached_result and 'model_anomaly' in cached_result:
            return anomaly_pb2.AnomalyResponse(
                anomaly_score=cached_result['model_score'],
                is_anomaly=bool(cached_result['model_anomaly'])
            )
        
        try:
            if request.paid_to_due_ratio > 0:
                ratio = request.paid_to_due_ratio
            elif request.amount_due > 0:
                ratio = request.amount_paid / request.amount_due
            else:
                ratio = 999.0
        except Exception as e:
            context.set_details(f"ratio computation failed: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return anomaly_pb2.AnomalyResponse(anomaly_score=-1, is_anomaly=False)

        data = pd.DataFrame([{
            "amount_due": request.amount_due,
            "amount_paid": request.amount_paid,
            "delay_days": request.delay_days,
            "paid_to_due_ratio": ratio
        }])

        score = self.model.decision_function(data)[0]
        is_anomaly = self.model.predict(data)[0] == -1

        
        ru.set_data_redis(redis_key,{
            "amount_due" : request.amount_due,
            "amount_paid": request.amount_paid,
            "delay_days": request.delay_days,
            "paid_to_due_ratio": request.paid_to_due_ratio,
            "model_score":float(score),
            "model_anomaly":bool(is_anomaly)
        })

        return anomaly_pb2.AnomalyResponse(
            anomaly_score=score,
            is_anomaly=is_anomaly
        )
    
    def SubmitFeedback(self,request,context):
        redis_key=f"anomaly:feedback-labeled:{request.amount_due}:{request.amount_paid}:{request.delay_days}"
        ru.set_data_redis(redis_key,{
            "amount_due":request.amount_due,
            "amount_paid":request.amount_paid,
            "delay_days":request.delay_days,
            "user_label": request.user_label 
        })
        return anomaly_pb2.FeedbackResponse(message="Feedback received")
        

def serve(redis_host='localhost', redis_port=6379):
    ru.init_redis(host=redis_host,port=redis_port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    anomaly_pb2_grpc.add_AnomalyServiceServicer_to_server(AnomalyDetector(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Anomaly GRPC Server")
    parser.add_argument('--redis_host', type=str, default='localhost', help='Redis host')
    parser.add_argument('--redis_port', type=int, default=6379, help='Redis port')
    args = parser.parse_args()
    serve(redis_host=args.redis_host, redis_port=args.redis_port)
