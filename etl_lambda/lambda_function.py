# D:\cognito_ai_assistant\etl_lambda\lambda_function.py
import json
import os
import psycopg2 # Needs to be packaged with Lambda deployment
# import boto3 # Used for S3 ingestion (omitted for brevity, assume data is pre-processed)

# Database connection details are passed via Lambda Environment Variables
DB_HOST = os.environ.get('RDS_HOST')
DB_NAME = os.environ.get('RDS_DBNAME')
DB_USER = os.environ.get('RDS_USER')
DB_PASS = os.environ.get('RDS_PASSWORD') # Pulled from Secrets Manager by Lambda

def lambda_handler(event, context):
    """
    Serverless ETL: Connects to RDS and updates a table.
    Triggered by: CloudWatch Event (Scheduled)
    """
    print("Starting scheduled ETL job...")
    conn = None
    try:
        # 1. Connect to RDS PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # 2. Simple Transformation/Load (Example: Update a counter or status)
        # In a real scenario, this would read from S3, clean, and insert
        update_query = """
        INSERT INTO "ai_core_taskupdate" (update_time, message)
        VALUES (NOW(), 'ETL job completed successfully, new data available.');
        """
        # This assumes you create a model ai_core_taskupdate in Django and run migrations
        cur.execute(update_query)
        conn.commit()

        print("Data update successful.")
        return {
            'statusCode': 200,
            'body': json.dumps('ETL job finished.')
        }

    except Exception as e:
        print(f"ETL Error: {e}")
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps(f"ETL failed: {str(e)}")
        }
    finally:
        if conn:
            conn.close()

# You must package this Python code with its dependencies (psycopg2-binary) as a ZIP file
# and upload it to the Lambda function.