import os
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2

def _pdf_payload(uri):
  return {'document': {'input_config': {'gcs_source': {'input_uris': [uri] } } } }

def _classify_doc(bucket, filename):
    uri = "gs://%s/%s" % (bucket, filename)
    options = ClientOptions(api_endpoint='automl.googleapis.com')
    prediction_client = automl_v1.PredictionServiceClient(client_options=options)

    payload = _pdf_payload(uri)

    request = prediction_client.predict(os.environ["SORT_MODEL_NAME"], payload, {})
    label = max(request.payload, key = lambda x: x.classification.score)
    return label.display_name if label.classification.score >= 0.7 else None

def sort_docs(data, context):
    bucket = data["bucket"]
    name = data["name"]
    return _classify_doc(bucket, name)


data = {
    "bucket" : "pdfs-out",
    "name" : "invoice104.pdf"
}
print(sort_docs(data, ""))