import anomaly_pb2
import anomaly_pb2_grpc
import os
import debt_model_loader as dml
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from redis_util import RedisUtil as ru
import grpc
from concurrent import futures


class AnomalyDetectorRf(anomaly_pb2_grpc.AnomalyServiceServicer):
    def __init__(self):
        self.model_path="anomaly_model_rf_joblib"
        self.csv_feedback_path="./feedback-labeled.csv"
        self._train_model()
    
    def _train_model(self):
        base_data = dml.fetch_csv()
        base_data['label']=0

        if os.path.exists(self.csv_feedback_path):
            feedback_data=pd.read_csv(self.csv_feedback_path)
            all_data= pd.concat([base_data,feedback_data],ignore_index=True)
        else:
            all_data = base_data

        self.model=RandomForestClassifier(n_estimators=100,random_state=42)
        self.model.fit(all_data[['amount_due','amount_paid','delay_days','paid_to_due_ratio']],all_data['label'])
        joblib.dump(self.model,self.model_path)
        print("Random Forest model trained and saved")

    def Detect(self, request, context):
        redis_key = f"anomaly:feedback:{request.amount_due}:{request.amount_paid}:{request.delay_days}"
        label_key = f"anomaly:feedback-labeled:{request.amount_due}:{request.amount_paid}:{request.delay_days}"

        user_feedback = ru.get_data_redis(label_key)
        if user_feedback and 'user_label' in user_feedback:
            return anomaly_pb2.AnomalyResponse(
                anomaly_score=1.0,
                is_anomaly=bool(user_feedback['user_label'])
            )
        
        cached_result = ru.get_data_redis(redis_key)
        if cached_result and 'model_score' in cached_result and 'model_anomlay' in cached_result:
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
                ratio=999.0
        except Exception as e:
            context.set_details(f'ratio computation failed :{e}')
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return anomaly_pb2.Anomalyresponse(anomaly_score=-1, is_anomaly=False)
        
        data = pd.DataFrame([{
            "amount_due": request.amount_due,
            "amount_paid": request.amount_paid,
            "delay_days": request.delay_days,
            "paid_to_due_ratio": ratio
        }])
        if len(self.model.classes_) < 2 :
            probas=0.0
            prediction=False
        else:
            proba_all = self.model.predict_proba(data)[0]
            class_index=list(self.model.classes_).index(1)
            probas = proba_all[class_index]
            prediction = self.model.predict(data)[0]==1
        ru.set_data_redis(redis_key,{
            "amount_due": request.amount_due,
            "amount_paid": request.amount_paid,
            "delay_days": request.delay_days,
            "paid_to_due_ratio": ratio,
            "model_score":probas,
            "model_anomaly": prediction
        })

        return anomaly_pb2.AnomalyResponse(
            anomaly_score=probas,
            is_anomaly=prediction
        )
    
    def SubmitFeedback(self,request,context):
        redis_key=f"anomaly:feedback-labeled:{request.amount_due}:{request.amount_paid}:{request.delay_days}"
        ru.set_data_redis(redis_key,{
            "amount_due":request.amount_due,
            "amount_paid": request.amount_paid,
            "delay_days": request.delay_days,
            "user_label": request.user_label
        })

        try:
            ratio = request.amount_paid/request.amount_due if request.amount_due > 0 else 999.0
            new_data = pd.DataFrame([{
                "amount_due": request.amount_due,
                "amount_paid": request.amount_paid,
                "delay_days": request.delay_days,
                "paid_to_due_ratio": ratio,
                "label": request.user_label
            }])

            if os.path.exists(self.csv_feedback_path):
                all_data = pd.read_csv(self.csv_feedback_path)
                all_data=pd.concat([all_data,new_data],ignore_index=True)
            else:
                all_data=new_data
            
            all_data.to_csv(self.csv_feedback_path,index=False)

            self.model.fit(all_data[['amount_due','amount_paid','delay_days','paid_to_due_ratio']],all_data['label'])
            joblib.dump(self.model,self.model_path)
            print('Model re trained with new feedback')
        except Exception as e:
            context.set_details(f"Retrain failed : {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
        
        return anomaly_pb2.FeedbackResponse(message="Feedback received and model retrained")
    

def serve(redis_host='localhost', redis_port=6379):
    ru.init_redis(host=redis_host,port=redis_port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    anomaly_pb2_grpc.add_AnomalyServiceServicer_to_server(AnomalyDetectorRf(),server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("grpc server running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="RF Anomaly GRPC Detection Server")
    parser.add_argument('--redis_host',type=str,default='localhost',help='Redis host')
    parser.add_argument('--redis_port',type=int,default=6379, help='Redis port')
    args = parser.parse_args()
    serve(redis_host=args.redis_host,redis_port=args.redis_port)
        