from google.cloud import vision
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import bigquery
import os
import json
import requests

def _get_name_from_phone(phone_number):
    """ Given a phone number as a string, returns Google's
    guess at the place name
    """
    api_key = os.environ["GOOGLE_API_KEY"]
    digit_phone = phone_number.replace('-', '').replace('+', '')
    places_endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=%2B1{digit_phone}&inputtype=phonenumber&fields=name,formatted_address,geometry,photos&key={api_key}"
    body = json.loads(requests.get(places_endpoint).text)
    response = {}
    if 'candidates' in body and len(body['candidates']) > 0:
        place_info = body['candidates'][0]
        return place_info["name"] if "name" in place_info else ""
    return ""

def _extract_entities(text):
    """ Given a string of text, returns extracted."""

    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    response = client.analyze_entities(document=document)

    return [{"name": entity.name, "type": enums.Entity.Type(entity.type).name, "metadata": entity.metadata} for entity in   response.entities]

def _extract_text(bucket_name, filename):
    uri = f"gs://{bucket_name}/{filename}"
    client = vision.ImageAnnotatorClient()
    res = client.document_text_detection({'source': {'image_uri': uri}})
    text = res.full_text_annotation.text
    if not text:
        print("OCR error " + str(res))
    return text


def _analyze_receipt(bucket_name, filename):
    """ Given a gc location of a receipt file, extracts (when found)
    the restaurant name, address, phone number, bill total (greatest
    price listed on bill), and date.
    """

    text = _extract_text(bucket_name, filename)

    entities = _extract_entities(text)

    result = {}

    # Extract the restaurant address.
    addrs = [x for x in entities if x['type'] == 'ADDRESS']
    result['address'] = addrs[0]['name'] if 'name' in addrs[0] else ""

    prices = [x for x in entities if x['type'] == 'PRICE']
    # Assume the highest listed price is the total. This may not always be true
    if len(prices):
        total = max([float(x['metadata']['value']) for x in prices])
        result['total'] = total
    else:
        result['total'] = None

    # Extract restaurant phone number.
    phone_numbers = [x for x in entities if x['type'] == 'PHONE_NUMBER']
    if len(phone_numbers) and 'name' in phone_numbers[0]:
        result['phone_number'] = phone_numbers[0]['name']
        name = _get_name_from_phone(result['phone_number'])
        if name:
            result["name"] = name
        else:
            result["name"] = ""
    else:
        result['phone_number'] = ""

    # Extract transaction date.
    dates = [x for x in entities if x['type'] == 'DATE']
    if len(dates):
        result['date'] = dates[0]['name']
    else:
        result['date'] = None

    return result

def _insert_receipt_bigquery(filename, name, date, total, address, phone_number):
    client = bigquery.Client()
    table_id = os.environ["RECEIPTS_TABLE"]
    table = client.get_table(table_id)
    rows =[{"filename": filename, "name": name, "date_str": date,
    "total": total, "address": address, "phone_number": phone_number}]
    errors = client.insert_rows(table, rows)
    if errors:
        print("Got errors " + str(errors))

def analyze_receipt(data, context):
    bucket = data["bucket"]
    name = data["name"]
    result = _analyze_receipt(bucket, name)
    if result:
        print("Inserting receipt gs://%s/%s into bigquery" % (bucket, name))
        _insert_receipt_bigquery(name, result["name"], result["date"], result["total"], result["address"], result["phone_number"])

data = {
    "bucket" : "receipts-123",
    "name" : "receipt.jpg"
}
analyze_receipt(data, "")