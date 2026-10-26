import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class CartStore:
    def __init__(self):
        self.items = []

    def add_item(self, name, quantity):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("quantity must be a positive integer")

        item = {"name": name.strip(), "quantity": quantity}
        self.items.append(item)
        return item

    def get_items(self):
        return list(self.items)


cart = CartStore()


class CartHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "service": "cart-backend"})
        elif self.path == "/api/cart":
            items = cart.get_items()
            self.send_json(200, {"items": items, "totalItems": sum(item["quantity"] for item in items)})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/cart":
            self.send_json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            item = cart.add_item(payload.get("name"), payload.get("quantity"))
        except (ValueError, json.JSONDecodeError, AttributeError) as error:
            self.send_json(400, {"error": str(error)})
            return

        self.send_json(201, {"item": item})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 5000), CartHandler)
    print("Cart backend listening on port 5000", flush=True)
    server.serve_forever()
