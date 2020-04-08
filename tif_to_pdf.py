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