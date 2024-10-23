import os
import requests
from fpdf import FPDF
import boto3

def get_uf(event, context):
    
    uf_url = 'https://mindicador.cl/api/uf'
    response = requests.get(uf_url)
    uf = response.json()
    uf_value = uf['serie'][0]['valor']
    
    # Create a PDF file
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = f"El valor de la UF es: {uf_value}", ln = True, align = 'C')
    pdf_filename = './uf.pdf'
    pdf.output(pdf_filename)
    
    session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=os.environ["AWS_SESSION_TOKEN"],
    )
    
    # Upload the PDF file to S3 local
    s3 = session.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
    )
    
    # Bucket name
    bucket_name = os.getenv('S3_BUCKET', 'test-bucket')
    
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        s3.create_bucket(Bucket=bucket_name)
        
    for bucket in s3.list_buckets()['Buckets']:
        print(bucket['Name'])
        
    s3.upload_file(pdf_filename, bucket_name, 'uf.pdf')
    
    return {
        'statusCode': 200,
        'body': f'PDF generated and UF value: {uf_value}'
    }