import unittest
import sort_documents


class SortDocuments(unittest.TestCase):
    def test_classify_doc(self):
        bucket = "cloud-samples-data" 
        filename = "documentai/invoice.pdf"
        label = sort_documents.classify_doc(bucket, filename)
        self.assertEqual(label, "invoice", "Should be invoice")

    def test_extract_text(self):
        bucket = "cloud-samples-data" 
        filename = "vision/text/screen.jpg"
        text = sort_documents.extract_text(bucket, filename)
        self.assertIsNotNone(text)
        self.assertIsInstance(text, str)

if __name__ == '__main__':
    unittest.main()