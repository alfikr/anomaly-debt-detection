# Anomaly Detection gRPC Service

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Compile the .proto:
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. anomaly.proto
   ```

3. Run the gRPC server:
   ```bash
   python anomaly_grpc_service.py
   ```

## gRPC Service

- Endpoint: `Detect(AnomalyRequest)`
- Input:
  - amount_due (double)
  - amount_paid (double)
  - delay_days (int)
- Output:
  - anomaly_score (double)
  - is_anomaly (bool)
