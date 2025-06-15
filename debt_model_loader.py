import os
import pandas as pd

def fetch_csv():
    csv_path=os.getenv('BOOKING_CSV_PATH','./sample-bookings.csv')
    print(f'Training new model from {csv_path}')
    df = pd.read_csv(csv_path)
    df = df[df['status']!='UNPAID'].copy()
    df['amount_paid']=pd.to_numeric(df['amount_paid'],errors='coerce')
    df['amount_due']=pd.to_numeric(df['amount_due'],errors='coerce')
    df['delay_days']=(pd.to_datetime(df['payment_date'])-pd.to_datetime(df['due_date'])).dt.days.fillna(0).astype(int)
    df['paid_to_due_ratio'] = df.apply(
        lambda row: row['amount_paid'] / row['amount_due'] if row['amount_due'] > 0 else 999.0,
        axis=1
    )
    df['label']=0
    x=df[['amount_due','amount_paid','delay_days','paid_to_due_ratio','label']].dropna()
    return x