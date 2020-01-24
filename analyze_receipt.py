from google.cloud import vision
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def _extract_entities(text):
    """ Given a string of text, returns extracted."""

    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    response = client.analyze_entities(document=document)

    return [{"name": entity.name, "type": entity.type} for entity in   response.entities]

def _analyze_receipt(bucket_name, filename):
    """ Given a gc location of a receipt file, extracts (when found)
    the restaurant name, address, phone number, bill total (greatest
    price listed on bill), and date.
    """

    result = {"filename" : filename}

    receipt_loc = f"gs://{bucket_name}/{filename}"
    client = vision.ImageAnnotatorClient()
    text = client.document_text_detection({'source': {'image_uri': receipt_loc}}).full_text_annotation
    print(text)
    try:
        text = text.full_text_annotation
    except Exception as e:
        print(f"Error with OCR annotations: {e}")
        return result

    entities = _extract_entities(text)

    # Extract the restaurant address.
    try:
        addrs = [x for x in entities if x['type'] == 'ADDRESS']
        result['address'] = addrs[0]['name']
    except:
        pass

    # Extract the meal total.
    try:
        prices = [x for x in entities if x['type'] == 'PRICE']
        # Assume the highest listed price is the total. This may not always be true
        total = max(prices, key=lambda x: float(x['metadata']['value']))['name']
        result['total'] = total
    except:
        pass

    # Extract restaurant phone number.
    try:
        phone_number = [x for x in entities if x['type'] == 'PHONE_NUMBER'][0]['name']
        result['phone_number'] = phone_number
    except:
        pass

    # Extract transaction date.
    try:
        date = [x for x in entities if x['type'] == 'DATE'][0]
        result['date'] = date['name']
        result['year'] = date['metadata']['year']
        result['day'] = date['metadata']['day']
        result['month'] = date['metadata']['month']
    except:
        pass

    return result

def analyze_receipt(data, context):
    results = _analyze_receipt(data['bucket'], data['name'])
    print(results)

data = {
    "bucket" : "pdfs-out",
    "name" : "invoice100.pdf"
}
analyze_receipt(data, "")