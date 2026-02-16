"""
Odoo MCP Server - Continuous Monitoring Mode
Runs as a background service monitoring for approved Odoo tasks
"""
import os
import time
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from odoo_mcp import OdooMCP

load_dotenv()

class OdooInvoiceProcessor:
    def __init__(self, odoo_mcp):
        self.odoo = odoo_mcp

    def parse_invoice_approval(self, file_path):
        """Parse invoice approval markdown file"""
        content = Path(file_path).read_text(encoding='utf-8')

        invoice_data = {
            'customer': {},
            'items': [],
            'total': 0,
            'date': None,
            'payment_terms': None
        }

        # Extract customer info
        name_match = re.search(r'-\s*Name:\s*(.+)', content)
        if name_match:
            invoice_data['customer']['name'] = name_match.group(1).strip()

        email_match = re.search(r'-\s*Email:\s*(.+)', content)
        if email_match:
            invoice_data['customer']['email'] = email_match.group(1).strip()

        phone_match = re.search(r'-\s*Phone:\s*(.+)', content)
        if phone_match:
            invoice_data['customer']['phone'] = phone_match.group(1).strip()

        # Extract invoice date
        date_match = re.search(r'\*\*Invoice Date:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            invoice_data['date'] = date_match.group(1).strip()

        # Extract payment terms
        terms_match = re.search(r'\*\*Payment Terms:\*\*\s*(.+)', content)
        if terms_match:
            invoice_data['payment_terms'] = terms_match.group(1).strip()

        # Extract invoice items
        item_pattern = r'\d+\.\s*\*\*(.+?)\*\*\s*\n\s*-\s*Quantity:\s*([\d.]+)\s*(\w+)?\s*\n\s*-\s*(?:Rate|Amount):\s*\$?([\d,]+(?:\.\d{2})?)'

        for match in re.finditer(item_pattern, content):
            item_name = match.group(1).strip()
            quantity = float(match.group(2))
            price_str = match.group(4).replace(',', '')
            price = float(price_str)

            invoice_data['items'].append({
                'name': item_name,
                'quantity': quantity,
                'price_unit': price
            })

        # Extract total
        total_match = re.search(r'\*\*Invoice Total:\*\*\s*\$?([\d,]+(?:\.\d{2})?)', content)
        if total_match:
            invoice_data['total'] = float(total_match.group(1).replace(',', ''))

        return invoice_data

    def process_invoice_approval(self, file_path):
        """Process a single invoice approval file"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing: {Path(file_path).name}")

        try:
            # Parse the approval file
            invoice_data = self.parse_invoice_approval(file_path)

            print(f"  Customer: {invoice_data['customer'].get('name', 'N/A')}")
            print(f"  Items: {len(invoice_data['items'])}")
            print(f"  Total: ${invoice_data['total']:,.2f}")

            # Find or create partner
            partner_id = None
            customer_email = invoice_data['customer'].get('email')

            if customer_email:
                partners = self.odoo.search_partner([['email', '=', customer_email]])
                if partners and len(partners) > 0:
                    partner_id = partners[0]['id']
                    print(f"  Found partner: {partners[0]['name']} (ID: {partner_id})")
                else:
                    partner_id = self.odoo.create_partner(
                        name=invoice_data['customer']['name'],
                        email=invoice_data['customer'].get('email'),
                        phone=invoice_data['customer'].get('phone')
                    )
                    print(f"  Created partner (ID: {partner_id})")

            if not partner_id:
                print("  [ERROR] Could not create/find partner")
                return None

            # Prepare invoice lines
            invoice_lines = []
            for item in invoice_data['items']:
                invoice_lines.append({
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price_unit': item['price_unit']
                })

            # Create invoice
            invoice_id = self.odoo.create_invoice(
                partner_id=partner_id,
                lines=invoice_lines,
                date_invoice=invoice_data['date'] or datetime.now().strftime('%Y-%m-%d')
            )

            if invoice_id:
                print(f"  [SUCCESS] Invoice #{invoice_id} created - ${invoice_data['total']:,.2f}")
                return {
                    'status': 'success',
                    'invoice_id': invoice_id,
                    'partner_id': partner_id,
                    'total': invoice_data['total'],
                    'file': Path(file_path).name
                }
            else:
                print(f"  [FAIL] Failed to create invoice")
                return None

        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            return None

def main():
    """Main MCP server loop"""
    print("=" * 70)
    print("ODOO MCP SERVER - CONTINUOUS MONITORING MODE")
    print("=" * 70)

    # Initialize Odoo MCP
    config = {
        'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
        'database': os.getenv('ODOO_DB', 'gold_tier_db'),
        'username': os.getenv('ODOO_USERNAME'),
        'password': os.getenv('ODOO_PASSWORD'),
    }

    print(f"\nConnecting to Odoo at {config['url']}...")
    odoo_mcp = OdooMCP(config)

    if not odoo_mcp.authenticate():
        print("[ERROR] Failed to authenticate with Odoo")
        return

    print(f"[OK] Connected to Odoo (UID: {odoo_mcp.uid})")

    # Initialize processor
    processor = OdooInvoiceProcessor(odoo_mcp)

    # Setup paths
    vault_path = Path("E:/Hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault")
    approved_dir = vault_path / "Approved"
    done_dir = vault_path / "Done"

    print(f"\nMonitoring: {approved_dir}")
    print("Checking every 30 seconds for new invoice approvals...")
    print("Press Ctrl+C to stop\n")
    print("-" * 70)

    processed_files = set()
    check_count = 0

    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')

            # Find all invoice approval files
            invoice_files = list(approved_dir.glob("*invoice*.md"))

            # Filter out already processed files
            new_files = [f for f in invoice_files if str(f) not in processed_files]

            if new_files:
                print(f"\n[{current_time}] Found {len(new_files)} new invoice(s) to process")

                for invoice_file in new_files:
                    result = processor.process_invoice_approval(invoice_file)

                    if result:
                        # Move to Done folder
                        done_file = done_dir / invoice_file.name
                        invoice_file.rename(done_file)
                        print(f"  Moved to Done: {invoice_file.name}")

                        # Mark as processed
                        processed_files.add(str(invoice_file))

                print("-" * 70)
            else:
                # Periodic status update every 10 checks (5 minutes)
                if check_count % 10 == 0:
                    print(f"[{current_time}] Monitoring... (checked {check_count} times)")

            # Wait 30 seconds before next check
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Odoo MCP Server stopped by user")
        print(f"Total files processed: {len(processed_files)}")
        print("=" * 70)

if __name__ == "__main__":
    main()
