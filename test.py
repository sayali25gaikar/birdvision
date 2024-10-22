import unittest
import json
from app import app

class ProductTestCase(unittest.TestCase):
    def test_response_code(self):   # test case to check response code 200 or not
        tester = app.test_client(self)
        response = tester.get("/products")   # we can replace our routes here
        self.assertEqual(response.status_code, 200)

    def test_response_content(self): # test case to check response content_type
        tester = app.test_client(self)
        response = tester.post("/add-products")
        self.assertNotEqual(response.content_type, "application/json")

    def test_check_message(self): # to check message is present or not in response
        tester = app.test_client(self)
        response = tester.delete("/delete-product/2")
        self.assertIn(b'Product is deleted successfully', response.data)

if __name__ == "__main__":
    unittest.main()