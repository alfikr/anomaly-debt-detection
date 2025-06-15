import grpc
import argparse
import anomaly_pb2
import anomaly_pb2_grpc

def init_parser():
    parser = argparse.ArgumentParser(
        usage="%(prog)s",
        description="Client Anomaly GRPC Server"
    )
    parser.add_argument('--due', type=float, required=True, help='Amount due')
    parser.add_argument('--paid', type=float, required=True, help='Amount paid')
    parser.add_argument('--delay', type=int, required=True, help='Days of payment delay')
    parser.add_argument('--paid_ratio', type=float,help='Paid ratio')
    parser.add_argument('--feedback', type=int, choices=[0, 1], help='Optional: Send feedback (0 = normal, 1 = anomaly)')
    return parser

def main():
    parser = init_parser()
    args = parser.parse_args()
    print(f'Start using args {args}')

    channel = grpc.insecure_channel('localhost:50051')
    stub = anomaly_pb2_grpc.AnomalyServiceStub(channel)

    if args.feedback is not None:
        request = anomaly_pb2.FeedbackRequest(
            amount_due=args.due,
            amount_paid=args.paid,
            delay_days=args.delay,
            user_label=args.feedback
        )
        response = stub.SubmitFeedback(request)
        print(f"✅ Feedback submitted: {response.message}")
    else:
        ratio = args.paid_ratio if args.paid_ratio is not None else (
            args.paid / args.due if args.due > 0 else 999.0
        )
        request = anomaly_pb2.AnomalyRequest(
            amount_due=args.due,
            amount_paid=args.paid,
            delay_days=args.delay,
            paid_to_due_ratio=ratio
        )
        response = stub.Detect(request)
        print(f'🔍 Anomaly Score : {response.anomaly_score: .4f}')
        print(f"🚨 isAnomaly ? : {'YES' if response.is_anomaly else 'NO'}")

if __name__ == "__main__":
    main()
