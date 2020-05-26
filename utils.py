from google.cloud import vision

def extract_text(bucket_name, filename):
    uri = f"gs://{bucket_name}/{filename}"
    client = vision.ImageAnnotatorClient()
    res = client.document_text_detection({'source': {'image_uri': uri}})
    text = res.full_text_annotation.text
    if not text:
        print("OCR error " + str(res))
    return text