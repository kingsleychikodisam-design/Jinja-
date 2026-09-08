from flask import Flask, request, redirect, url_for, render_template_string
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id TEXT UNIQUE NOT NULL,
            product TEXT NOT NULL,
            customer TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id SERIAL PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            business_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    cur.execute("""
        INSERT INTO orders
        (order_id, product, customer, phone, address, amount, payment, status)
        VALUES
        ('JINJA-8893429', 'Tecno Camon Series', 'Kingsley Samuel',
         '08000000000', 'Lagos', 310000, 'Pay on delivery', 'Pending')
        ON CONFLICT (order_id) DO NOTHING
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JINJA Marketplace</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>JINJA Marketplace</h1>

        <h2>Track Your Order</h2>

        <form action="/track" method="get">
            <input
                type="text"
                name="order_id"
                placeholder="Enter Order ID"
                required
            >
            <button type="submit">Track Order</button>
        </form>

        <br>

        <a href="/vendor/register">Become a Vendor</a>
        <br><br>
        <a href="/admin">Admin Panel</a>
    </body>
    </html>
    """


@app.route("/track")
def track():
    order_id = request.args.get("order_id")

    if not order_id:
        return redirect(url_for("home"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM orders WHERE order_id = %s",
        (order_id,)
    )

    order = cur.fetchone()

    cur.close()
    conn.close()

    if not order:
        return "<h2>Order not found</h2><a href='/'>Go back</a>"

    statuses = ["Pending", "Confirmed", "Shipped", "Delivered"]

    progress = ""

    for status in statuses:
        if statuses.index(status) <= statuses.index(order["status"]):
            progress += f"<li><b>✓ {status}</b></li>"
        else:
            progress += f"<li>{status}</li>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Track Order</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>

        <h1>Order Tracking</h1>

        <h2>{order["order_id"]}</h2>

        <p><b>Product:</b> {order["product"]}</p>
        <p><b>Customer:</b> {order["customer"]}</p>
        <p><b>Amount:</b> ₦{order["amount"]:,}</p>
        <p><b>Payment:</b> {order["payment"]}</p>
        <p><b>Address:</b> {order["address"]}</p>

        <h3>Status: {order["status"]}</h3>

        <ol>
            {progress}
        </ol>

        <a href="/">Back Home</a>

    </body>
    </html>
    """


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":
        order_id = request.form["order_id"]
        status = request.form["status"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "UPDATE orders SET status = %s WHERE order_id = %s",
            (status, order_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()

    cur.execute("SELECT * FROM vendors ORDER BY id DESC")
    vendors = cur.fetchall()

    cur.close()
    conn.close()

    order_html = ""

    for order in orders:
        order_html += f"""
        <div>
            <h3>{order["order_id"]}</h3>
            <p>{order["product"]}</p>
            <p>Current Status: <b>{order["status"]}</b></p>

            <form method="POST">
                <input type="hidden"
                       name="order_id"
                       value="{order["order_id"]}">

                <select name="status">
                    <option>Pending</option>
                    <option>Confirmed</option>
                    <option>Shipped</option>
                    <option>Delivered</option>
                </select>

                <button type="submit">Update Status</button>
            </form>
        </div>
        <hr>
        """

    vendor_html = ""

    for vendor in vendors:
        vendor_html += f"""
        <div>
            <h3>{vendor["business_name"]}</h3>
            <p>Vendor: {vendor["vendor_name"]}</p>
            <p>Phone: {vendor["phone"]}</p>
            <p>Email: {vendor["email"]}</p>
            <p>Category: {vendor["category"]}</p>
            <p>Address: {vendor["address"]}</p>
        </div>
        <hr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JINJA Admin</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>

        <h1>JINJA Admin Panel</h1>

        <h2>Orders</h2>

        {order_html}

        <h2>Registered Vendors</h2>

        {vendor_html}

        <a href="/">Back Home</a>

    </body>
    </html>
    """


@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():

    if request.method == "POST":

        vendor_name = request.form["vendor_name"]
        business_name = request.form["business_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]
        category = request.form["category"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO vendors
            (vendor_name, business_name, phone, email, address, category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            vendor_name,
            business_name,
            phone,
            email,
            address,
            category
        ))

        conn.commit()
        cur.close()
        conn.close()

        return """
        <h2>Vendor registration successful!</h2>
        <a href="/">Back to JINJA</a>
        """

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Become a Vendor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>

        <h1>Become a JINJA Vendor</h1>

        <form method="POST">

            <input name="vendor_name"
                   placeholder="Your Name"
                   required><br><br>

            <input name="business_name"
                   placeholder="Business Name"
                   required><br><br>

            <input name="phone"
                   placeholder="Phone Number"
                   required><br><br>

            <input name="email"
                   type="email"
                   placeholder="Email"
                   required><br><br>

            <input name="address"
                   placeholder="Business Address"
                   required><br><br>

            <select name="category" required>
                <option value="">Select Category</option>
                <option>Phones & Electronics</option>
                <option>Fashion</option>
                <option>Beauty</option>
                <option>Health</option>
                <option>Home & Living</option>
                <option>Food</option>
                <option>Other</option>
            </select>

            <br><br>

            <button type="submit">Register as Vendor</button>

        </form>

        <br>

        <a href="/">Back Home</a>

    </body>
    </html>
    """


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
