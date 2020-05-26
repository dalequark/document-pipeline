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

from google.cloud import language
from google.cloud import storage
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import bigquery
import os
import utils

def get_tags(text, confidence_thresh=0.69):
    # Instantiates a client
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    try:
        res = client.classify_text(document)
    except Exception as err:
        print(err)
        return []
    return [tag.name for tag in res.categories]

def _insert_tags_bigquery(filename, tags):
    client = bigquery.Client()
    table_id = os.environ["ARTICLE_TAGS_TABLE"]
    table = client.get_table(table_id)
    rows =[{"filename" : filename, "tag": tags}]
    errors = client.insert_rows(table, rows)
    if errors:
        print("Got errors " + str(errors))

def tag_article(data, context):
    bucket = data["bucket"]
    name = data["name"]
    ext = os.path.splitext(name)[1] if len(os.path.splitext(name)[1]) > 1 else None
    text = None
    if ext in ['.tif', '.tiff', '.png', '.jpeg', '.jpg']:
        print("Extracting text from image file")
        text = utils.extract_text(bucket, name)
        if not text:
            print("Couldn't extract text from gs://%s/%s" % (bucket, name))
    elif ext in ['.txt']:
        print("Downloading text file from cloud")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket)
        blob = bucket.blob(name)
        text = blob.download_as_string()
    else:
        print(f'Unsupported file type {ext}')
    if text:
        tags = get_tags(text)
        print("Found %d tags for article %s" % (len(tags), name))
        _insert_tags_bigquery(name, tags)
