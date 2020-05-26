# Copyright 2020 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2
from google.cloud import storage
from google.cloud import vision
import utils


def _gcs_payload(bucket, filename):
    uri = f"gs://{bucket}/{filename}"
    return {'document': {'input_config': {'gcs_source': {'input_uris': [uri]}}}}

def _img_payload(bucket, filename):
    print(f"Converting file gs://{bucket}/{filename} to text")
    text = utils.extract_text(bucket, filename)
    if not text:
        return None
    return {'text_snippet': {'content': text, 'mime_type': 'text/plain'}}


def classify_doc(bucket, filename):
    options = ClientOptions(api_endpoint='automl.googleapis.com')
    prediction_client = automl_v1.PredictionServiceClient(
        client_options=options)

    _, ext = os.path.splitext(filename)
    if ext in [".pdf", "txt", "html"]:
        payload = _gcs_payload(bucket, filename)
    elif ext in ['.tif', '.tiff', '.png', '.jpeg', '.jpg']:
        payload = _img_payload(bucket, filename)
    else:
        print(
            f"Could not sort document gs://{bucket}/{filename}, unsupported file type {ext}")
        return None
    if not payload:
        print(
            f"Missing document gs://{bucket}/{filename} payload, cannot sort")
        return None
    request = prediction_client.predict(
        os.environ["SORT_MODEL_NAME"], payload, {})
    label = max(request.payload, key=lambda x: x.classification.score)
    threshold = float(os.environ.get('SORT_MODEL_THRESHOLD')) or 0.7
    displayName = label.display_name if label.classification.score > threshold else None
    print(f"Labeled document gs://{bucket}/{filename} as {displayName}")
    return displayName


def sort_documents(data, context):
    print("Hello from sort documenets")
    bucket = data["bucket"]
    name = data["name"]
    print("Classifying doc")
    doc_type = classify_doc(bucket, name)
    print(f"Labeled document gs://{bucket}/{name} as {doc_type}")
    storage_client = storage.Client()
    source_bucket = storage_client.bucket(bucket)
    source_blob = source_bucket.blob(name)
    if doc_type in ["invoice", "invoice", "budget"]:
        dest_bucket_name = os.environ["INVOICES_BUCKET"]
    elif doc_type == "article":
        dest_bucket_name = os.environ["ARTICLES_BUCKET"]
    elif doc_type == "form":
        dest_bucket_name = os.environ["FORMS_BUCKET"]
    else:
        dest_bucket_name = os.environ["UNSORTED_BUCKET"]
    dest_bucket = storage_client.bucket(dest_bucket_name)

    blob_copy = source_bucket.copy_blob(source_blob, dest_bucket, name)
    source_blob.delete()
    print(
        f"Moved file gs://{bucket}/{name} to gs://{dest_bucket_name}/{blob_copy.name}")
