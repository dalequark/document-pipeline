import unittest
import sort_documents

class TestClassifyDoc(unittest.TestCase):
    # Test data publicly hosted by Google
    bucket = "cloud-samples-data" 
    filename = "documentai/invoice.pdf"
    label = sort_documents.classify_doc(bucket, filename)
    def test_label(self):
        self.assertEqual(self.label, "invoice", "Should be invoice")

if __name__ == '__main__':
    unittest.main()