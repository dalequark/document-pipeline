import unittest
import sort_documents
import utils
import tag_article
import analyze_form
from unittest.mock import patch 
from io import StringIO 

class SortDocuments(unittest.TestCase):
    def test_classify_doc(self):
        bucket = "cloud-samples-data" 
        filename = "documentai/invoice.pdf"
        label = sort_documents.classify_doc(bucket, filename)
        self.assertEqual(label, "invoice", "Should be invoice")

class Utils(unittest.TestCase):
    def test_extract_text(self):
        bucket = "cloud-samples-data" 
        filename = "vision/text/screen.jpg"
        text = utils.extract_text(bucket, filename)
        self.assertIsNotNone(text)
        self.assertIsInstance(text, str)

class TagArticle(unittest.TestCase):

    TEST_TEXT = """Google, headquartered in Mountain View 
    (1600 Amphitheatre Pkwy, Mountain View, CA 940430), unveiled 
    the new Android phone for $799 at the Consumer Electronic Show. 
    Sundar Pichai said in his keynote that users love their new Android phones."""

    def test_get_tags(self):
        tags = tag_article.get_tags(self.TEST_TEXT, 0.5)
        self.assertIsNotNone(tags)
        self.assertIsInstance(tags, list)
        self.assertIsInstance(tags[0], str)
        self.assertGreater(len(tags), 0)
        self.assertGreater(len(tags[0]), 0)
    
    # TODO: Don't include this stateful function
    # def test_add_bq(self):
    #     with patch('sys.stdout', new = StringIO()) as fake_out: 
    #         tag_article._insert_tags_bigquery("myfakefile", ["some", "fake", "keys"]) 
    #         self.assertTrue('error' not in fake_out.getvalue().lower()) 

class AnalyzeForm(unittest.TestCase):
    def test_get_form_fields(self):
        bucket = "cloud-samples-data" 
        filename = "documentai/form.pdf"
        fields = analyze_form.get_form_fields(bucket, filename)
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)
        for field in fields:
            self.assertSetEqual(set(field.keys()), set(["filename", "page", "form_field_name", "form_field_value"]))
            self.assertIsInstance(field["filename"], str)
            self.assertGreater(len(field["filename"]), 0)
            self.assertIsInstance(field["page"], int)
            self.assertIsInstance(field["form_field_name"], str)
            self.assertGreater(len(field["form_field_name"]), 0)
            self.assertIsInstance(field["form_field_value"], str)
            self.assertGreater(len(field["form_field_value"]), 0)
            
    # TODO: Don't include this statful function
    # def test_analyze_form(self):
    #     analyze_form.analyze_form({"bucket": "cloud-samples-data", "name": "documentai/form.pdf"}, None)

if __name__ == '__main__':
    unittest.main()