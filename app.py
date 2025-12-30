from flask import Flask, render_template, request, redirect, url_for
from db.workshop import create_workshop_if_not_exists
from db.customer import add_customer
from db.invoice import create_invoice
from db.invoice_services import add_service
from db.payments import add_payment
from db.update_invoice_totals import update_invoice_totals
from db.fetch_invoice import fetch_invoice_full
from db.connection import get_db

app = Flask(__name__)
create_workshop_if_not_exists()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/history")
def history():
    conn = get_db()
    # Joining tables to display customer names in the history list
    invoices = conn.execute("""
        SELECT i.*, c.name as customer_name 
        FROM invoice i 
        JOIN customer c ON i.customer_id = c.id 
        ORDER BY i.id DESC
    """).fetchall()
    conn.close()
    return render_template("all_invoices.html", invoices=invoices)

@app.route("/create-invoice", methods=["POST"])
def create_invoice_route():
    try:
        # Create customer and capture the ID
        customer_id = add_customer(
            request.form.get("customer_name"), 
            "", 
            request.form.get("phone")
        )
        
        # Create the invoice record
        invoice_id = create_invoice(customer_id, request.form.get("delivery_date"))

        # Process dynamic services list
        names = request.form.getlist("service_name[]")
        prices = request.form.getlist("price[]")
        gsts = request.form.getlist("gst_percent[]")
        
        for n, p, g in zip(names, prices, gsts):
            if n and p:
                add_service(invoice_id, n, float(p), float(g))

        # Update totals before processing payment
        update_invoice_totals(invoice_id)
        _, invoice, _, _ = fetch_invoice_full(invoice_id)
        
        # Add initial payment
        add_payment(
            invoice_id, 
            invoice["total_amount"], 
            request.form.get("payment_mode"), 
            request.form.get("payment_type")
        )

        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Error", 500

@app.route("/invoice/<int:invoice_id>")
def view_invoice(invoice_id):
    workshop, invoice, services, payments = fetch_invoice_full(invoice_id)
    if not invoice:
        return "Invoice not found", 404
        
    total_paid = sum(p['amount'] for p in payments)
    payment_due = invoice['total_amount'] - total_paid
    
    return render_template(
        "invoice.html", 
        workshop=workshop, 
        invoice=invoice, 
        services=services, 
        payments=payments, 
        payment_due=payment_due
    )

if __name__ == "__main__":
    app.run(debug=True)