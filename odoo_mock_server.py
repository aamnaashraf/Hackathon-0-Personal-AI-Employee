"""
Odoo Mock Server - For Demo/Testing Without Full Odoo Installation
Simulates Odoo JSON-RPC responses for hackathon demo
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class OdooMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request = json.loads(post_data.decode('utf-8'))

        # Simulate Odoo JSON-RPC responses
        method = request.get('params', {}).get('method', '')
        model = request.get('params', {}).get('args', [None])[0]

        response = {
            'jsonrpc': '2.0',
            'id': request.get('id', 1),
            'result': None
        }

        # Simulate authentication
        if 'authenticate' in str(request):
            response['result'] = 1  # User ID

        # Simulate invoice creation
        elif model == 'account.move' and method == 'create':
            response['result'] = 12345  # Mock invoice ID
            print(f"[ODOO_MOCK] Created invoice: ID=12345")

        # Simulate partner search
        elif model == 'res.partner' and method == 'search':
            response['result'] = [1, 2, 3]  # Mock partner IDs

        # Simulate partner creation
        elif model == 'res.partner' and method == 'create':
            response['result'] = 999  # Mock partner ID
            print(f"[ODOO_MOCK] Created partner: ID=999")

        # Simulate read operations
        elif method == 'read':
            response['result'] = [{
                'id': 1,
                'name': 'Mock Data',
                'create_date': datetime.now().isoformat()
            }]

        else:
            response['result'] = True

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def log_message(self, format, *args):
        print(f"[ODOO_MOCK] {format % args}")

def run_mock_server(port=8069):
    server = HTTPServer(('localhost', port), OdooMockHandler)
    print(f"[ODOO_MOCK] Mock Odoo server running on http://localhost:{port}")
    print("[ODOO_MOCK] Simulating Odoo Community JSON-RPC API")
    print("[ODOO_MOCK] Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ODOO_MOCK] Server stopped")

if __name__ == '__main__':
    run_mock_server()
