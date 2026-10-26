import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from backend.app import CartHandler, CartStore


class CartApiTests(unittest.TestCase):
    def setUp(self):
        self.cart_patch = patch("backend.app.cart", CartStore())
        self.cart_patch.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), CartHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join()
        self.cart_patch.stop()

    def request_json(self, path, method="GET", payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_endpoint(self):
        status, body = self.request_json("/health")

        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_add_item_and_get_cart(self):
        status, body = self.request_json(
            "/api/cart", method="POST", payload={"name": "Notebook", "quantity": 2}
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["item"], {"name": "Notebook", "quantity": 2})

        status, body = self.request_json("/api/cart")
        self.assertEqual(status, 200)
        self.assertEqual(body["totalItems"], 2)
        self.assertEqual(body["items"], [{"name": "Notebook", "quantity": 2}])

    def test_invalid_item_is_rejected(self):
        status, body = self.request_json(
            "/api/cart", method="POST", payload={"name": "", "quantity": 1}
        )

        self.assertEqual(status, 400)
        self.assertIn("error", body)


class CartStoreTests(unittest.TestCase):
    def setUp(self):
        self.cart = CartStore()

    def test_rejects_non_positive_or_non_integer_quantity(self):
        for quantity in (0, -1, 1.5, True):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    self.cart.add_item("Notebook", quantity)


if __name__ == "__main__":
    unittest.main()
