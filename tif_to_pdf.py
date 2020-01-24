import img2pdf
from google.cloud import storage
import os

def convert_to_pdf(data, context):
    assert(os.environ["PDF_DIR"])
    # Download the file from cloud storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(data["bucket"])
    blob = bucket.blob(data["name"])
    print(f"Got file from bucket {data['bucket']} with name {data['name']}")
    img_data = blob.download_as_string()
    pdf = img2pdf.convert(img_data)
    print("Converted to pdf")
    pdf_bucket = storage_client.bucket(os.environ["PDF_DIR"])
    pdf_name = ".".join(data["name"].split(".")[:-1]) + ".pdf"
    print(f"Uploading file with name {pdf_name} to bucket {os.environ['PDF_DIR']}")
    pdf_blob = pdf_bucket.blob(pdf_name)
    pdf_blob.upload_from_string(pdf, content_type="application/pdf")

    ^([0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-2][0-9][0-9][0-9])$