from google.cloud import documentai_v1beta2 as documentai
from google.cloud import bigquery
import os

def _insert_tags_bigquery(rows):
    client = bigquery.Client()
    table_id = os.environ["FORMS_TABLE"]
    table = client.get_table(table_id)
    errors = client.insert_rows(table, rows)
    if errors:
        print("Got errors " + str(errors))

def get_form_fields(bucket, filename):
    """Parse a form"""

    client = documentai.DocumentUnderstandingServiceClient()

    gcs_source = documentai.types.GcsSource(uri=f"gs://{bucket}/{filename}")

    # mime_type can be application/pdf, image/tiff,
    # and image/gif, or application/json
    input_config = documentai.types.InputConfig(
        gcs_source=gcs_source, mime_type='application/pdf')

    # Improve form parsing results by providing key-value pair hints.
    # For each key hint, key is text that is likely to appear in the
    # document as a form field name (i.e. "DOB").
    # Value types are optional, but can be one or more of:
    # ADDRESS, LOCATION, ORGANIZATION, PERSON, PHONE_NUMBER, ID,
    # NUMBER, EMAIL, PRICE, TERMS, DATE, NAME
    key_value_pair_hints = [
        documentai.types.KeyValuePairHint(key='Emergency Contact',
                                          value_types=['NAME']),
        documentai.types.KeyValuePairHint(
            key='Referred By')
    ]

    # Setting enabled=True enables form extraction
    form_extraction_params = documentai.types.FormExtractionParams(
        enabled=True, key_value_pair_hints=key_value_pair_hints)

    # Location can be 'us' or 'eu'
    parent = 'projects/{}/locations/us'.format(os.environ["PROJECT_ID"])
    request = documentai.types.ProcessDocumentRequest(
        parent=parent,
        input_config=input_config,
        form_extraction_params=form_extraction_params)

    document = client.process_document(request=request)

    def _get_text(el):
        """Doc AI identifies form fields by their offsets
        in document text. This function converts offsets
        to text snippets.
        """
        response = ''
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += document.text[start_index:end_index]
        return response

    # Return an array of form fields
    return [
        {
            "filename": filename,
            "page": page.page_number,
            "form_field_name": _get_text(form_field.field_name),
            "form_field_value": _get_text(form_field.field_value)
        }
        for page in document.pages for form_field in page.form_fields
    ]

def analyze_form(data, context):
    bucket = data["bucket"]
    name = data["name"]
    rows = get_form_fields(bucket, name)
    if rows:
        print("Inserting form gs://%s/%s into bigquery" % (bucket, name))
        _insert_tags_bigquery(rows) 