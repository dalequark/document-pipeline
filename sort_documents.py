import os
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2
from google.cloud import storage
from google.cloud import vision

def _gcs_payload(bucket, filename):
    uri = "gs://{bucket}/{filename}"
    return {'document': {'input_config': {'gcs_source': {'input_uris': [uri] } } } }

def _extract_text(bucket, filename):
    uri = f"gs://{bucket}/{filename}"
    client = vision.ImageAnnotatorClient()
    res = client.document_text_detection({'source': {'image_uri': uri}})
    text = res.full_text_annotation.text
    if not text:
        print("OCR error " + str(res))
    return text

def _img_payload(bucket, filename):
    print(f"Converting file gs://{bucket}/{filename} to text")
    text = _extract_text(bucket, filename)
    if not text:
        return None
    return {'text_snippet': {'content': text, 'mime_type': 'text/plain'} }

def _classify_doc(bucket, filename):
    uri = "gs://%s/%s" % (bucket, filename)
    options = ClientOptions(api_endpoint='automl.googleapis.com')
    prediction_client = automl_v1.PredictionServiceClient(client_options=options)

    _, ext = os.path.splitext(filename)
    if ext in [".pdf", "txt", "html"]:
        payload = _gcs_payload(bucket, filename)
    elif ext in ['.tif', '.tiff', '.png', '.jpeg', '.jpg']:
        payload = _img_payload(bucket, filename)
    else:
        print(f"Could not sort document gs://{bucket}/{filename}, unsupported file type {ext}")
        return None
    if not payload:
        print(f"Missing document gs://{bucket}/{filename} payload, cannot sort")
        return None
    request = prediction_client.predict(os.environ["SORT_MODEL_NAME"], payload, {})
    label = max(request.payload, key = lambda x: x.classification.score)
    if label.classification.score < 0.7:
        print(f"Not sorting document but classification score {label.classification.score} is too low")
    return label.display_name if label.classification.score >= 0.6 else None

def sort_docs(data, context):
    bucket = data["bucket"]
    name = data["name"]
    doc_type = _classify_doc(bucket, name)
    print(f"Labeled document gs://{bucket}/{name} as {doc_type}")
    return
    # Move the file to the appropriate bucket based on file type
    # TODO: add support for more document types
    storage_client = storage.Client()
    source_bucket = storage_client.bucket(bucket)
    source_blob = source_bucket.blob(name)
    if doc_type in ["invoice", "receipt", "budget"]:
        dest_bucket_name = os.environ["RECEIPTS_BUCKET"]
    elif doc_type == "article":
        dest_bucket_name = os.environ["ARTICLES_BUCKET"]
    else:
        dest_bucket_name = os.environ["UNSORTED_BUCKET"]
    dest_bucket = storage_client.bucket(dest_bucket_name)

    blob_copy = source_bucket.copy_blob(source_blob, dest_bucket, name)
    source_blob.delete()
    print(f"Moved file gs://{bucket}/{name} to gs://{dest_bucket_name}/{blob_copy.name}")

data = {
    "bucket": "pdfs-out",
    "name": "nyt_drug_prices.jpg"
}

sort_docs(data, None)