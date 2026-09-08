from flask import Flask, request, redirect, url_for
import os
import random
import html
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id SERIAL PRIMARY KEY,
            business_name TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            vendor_id INTEGER REFERENCES vendors(id),
            product_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            price INTEGER NOT NULL,
            commission_percent NUMERIC DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id TEXT UNIQUE NOT NULL,
            product TEXT NOT NULL,
            customer TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            vendor_id INTEGER,
            commission_amount NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS vendor_id INTEGER
    """)

    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS commission_amount NUMERIC DEFAULT 0
    """)

    conn.commit()
    cur.close()
    conn.close()


try:
    init_db()
except Exception as e:
    print("Database initialization error:", e)


def page(title, body):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>""" + title + """</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: auto;
            }
            .box {
                background: white;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ddd;
            }
            input, textarea, select {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                box-sizing: border-box;
            }
            button, .button {
                background: #111;
                color: white;
                padding: 12px 18px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                cursor: pointer;
            }
            a {
                color: #111;
            }
            .nav {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a> |
                <a href="/track">Track Order</a> |
                <a href="/vendor/register">Become a Vendor</a> |
                <a href="/admin">Admin Panel</a>
            </div>
            """ + body + """
        </div>
    </body>
    </html>
    """


@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT products.*, vendors.business_name
        FROM products
        LEFT JOIN vendors ON products.vendor_id = vendors.id
        ORDER BY products.id DESC
    """)

    products = cur.fetchall()

    cur.close()
    conn.close()

    items = ""

    if not products:
        items = """
        <div class="box">
            <h3>No products yet</h3>
            <p>Vendors can register and add products.</p>
        </div>
        """

    for product in products:
        pid = product["id"]
        name = html.escape(product["product_name"])
        description = html.escape(product["description"] or "")
        price = product["price"]
        vendor = html.escape(product["business_name"] or "JINJA")

        items += f"""
        <div class="box">
            <h2>{name}</h2>
            <p>{description}</p>
            <p><b>Price:</b> ₦{price:,}</p>
            <p><b>Supplier:</b> {vendor}</p>
            <a class="button" href="/order/{pid}">Order Now</a>
        </div>
        """

    body = """
    <h1>JINJA Marketplace</h1>
    <p>Buy products from trusted suppliers.</p>

    <div class="box">
        <h2>Track Your Order</h2>
        <a class="button" href="/track">Track Order</a>
    </div>
    """ + items

    return page("JINJA Marketplace", body)


@app.route("/order/<int:product_id>", methods=["GET", "POST"])
def place_order(product_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cur.fetchone()

    if not product:
        cur.close()
        conn.close()
        return page("Product Not Found", "<h2>Product not found.</h2>")

    if request.method == "POST":
        customer = request.form.get("customer", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not customer or not phone or not address:
            cur.close()
            conn.close()
            return page(
                "Order Error",
                "<h2>Please fill in all fields.</h2><a href='/order/" +
                str(product_id) + "'>Go back</a>"
            )

        amount = product["price"]
        commission_percent = float(product["commission_percent"] or 0)
        commission = amount * commission_percent / 100

        order_id = "JINJA-" + str(random.randint(1000000, 9999999))

        cur.execute("""
            INSERT INTO orders
            (order_id, product, customer, phone, address, amount,
             status, vendor_id, commission_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            product["product_name"],
            customer,
            phone,
            address,
            amount,
            "Pending",
            product["vendor_id"],
            commission
        ))

        conn.commit()
        cur.close()
        conn.close()

        body = f"""
        <div class="box">
            <h1>Order Received!</h1>
            <p>Your order has been created successfully.</p>
            <h2>Order ID: {order_id}</h2>
            <p>Keep this Order ID to track your order.</p>
            <a class="button" href="/track">Track Order</a>
        </div>
        """

        return page("Order Received", body)

    name = html.escape(product["product_name"])
    price = product["price"]

    body = f"""
    <div class="box">
        <h1>Order {name}</h1>
        <h2>₦{price:,}</h2>

        <form method="POST">
            <label>Your Name</label>
            <input name="customer" required>

            <label>Phone Number</label>
            <input name="phone" required>

            <label>Delivery Address</label>
            <textarea name="address" required></textarea>

            <button type="submit">Place Order</button>
        </form>
    </div>
    """

    cur.close()
    conn.close()

    return page("Place Order", body)


@app.route("/track", methods=["GET", "POST"])
def track():
    order = None

    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT * FROM orders WHERE order_id = %s",
            (order_id,)
        )

        order = cur.fetchone()

        cur.close()
        conn.close()

    body = """
    <div class="box">
        <h1>Track Your Order</h1>

        <form method="POST">
            <label>Enter Order ID</label>
            <input name="order_id" placeholder="Example: JINJA-1234567" required>
            <button type="submit">Track Order</button>
        </form>
    </div>
    """

    if request.method == "POST":
        if order:
            body += f"""
            <div class="box">
                <h2>Order Found</h2>
                <p><b>Order ID:</b> {html.escape(order["order_id"])}</p>
                <p><b>Product:</b> {html.escape(order["product"])}</p>
                <p><b>Customer:</b> {html.escape(order["customer"])}</p>
                <p><b>Status:</b> {html.escape(order["status"])}</p>
            </div>
            """
        else:
            body += """
            <div class="box">
                <h3>Order not found.</h3>
                <p>Please check your Order ID and try again.</p>
            </div>
            """

    return page("Track Order", body)


@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO vendors
            (business_name, name, phone, email)
            VALUES (%s, %s, %s, %s)
        """, (business_name, name, phone, email))

        conn.commit()
        cur.close()
        conn.close()

        return page(
            "Vendor Registered",
            """
            <div class="box">
                <h1>Vendor Registration Successful!</h1>
                <p>Your supplier account has been added.</p>
                <a class="button" href="/vendor/product">Add Product</a>
            </div>
            """
        )

    body = """
    <div class="box">
        <h1>Become a Vendor</h1>

        <form method="POST">
            <label>Business Name</label>
            <input name="business_name" required>

            <label>Your Name</label>
            <input name="name" required>

            <label>Phone Number</label>
            <input name="phone" required>

            <label>Email</label>
            <input name="email">

            <button type="submit">Register</button>
        </form>
    </div>
    """

    return page("Vendor Registration", body)


@app.route("/vendor/product", methods=["GET", "POST"])
def vendor_product():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM vendors ORDER BY id DESC")
    vendors = cur.fetchall()

    if request.method == "POST":
        vendor_id = request.form.get("vendor_id")
        product_name = request.form.get("product_name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price")
        commission = request.form.get("commission", "10")

        cur.execute("""
            INSERT INTO products
            (vendor_id, product_name, description, price, commission_percent)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            vendor_id,
            product_name,
            description,
            int(price),
            float(commission)
        ))

        conn.commit()
        cur.close()
        conn.close()

        return page(
            "Product Added",
            """
            <div class="box">
                <h1>Product Added Successfully!</h1>
                <p>The product is now available on JINJA Marketplace.</p>
                <a class="button" href="/">View Marketplace</a>
            </div>
            """
        )

    options = ""

    for vendor in vendors:
        vid = vendor["id"]
        vname = html.escape(vendor["business_name"])
        options += f'<option value="{vid}">{vname}</option>'

    cur.close()
    conn.close()

    body = f"""
    <div class="box">
        <h1>Add Product</h1>

        <form method="POST">
            <label>Supplier</label>
            <select name="vendor_id" required>
                {options}
            </select>

            <label>Product Name</label>
            <input name="product_name" required>

            <label>Description</label>
            <textarea name="description"></textarea>

            <label>Price (₦)</label>
            <input type="number" name="price" required>

            <label>JINJA Commission (%)</label>
            <input type="number" name="commission" value="10" min="0" max="100">

            <button type="submit">Add Product</button>
        </form>
    </div>
    """

    return page("Add Product", body)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        order_db_id = request.form.get("order_db_id")
        status = request.form.get("status")

        cur.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (status, order_db_id)
        )

        conn.commit()

    cur.execute("""
        SELECT orders.*, vendors.business_name
        FROM orders
        LEFT JOIN vendors ON orders.vendor_id = vendors.id
        ORDER BY orders.id DESC
    """)
    orders = cur.fetchall()

    cur.execute("""
        SELECT products.*, vendors.business_name
        FROM products
        LEFT JOIN vendors ON products.vendor_id = vendors.id
        ORDER BY products.id DESC
    """)
    products = cur.fetchall()

    cur.execute("SELECT * FROM vendors ORDER BY id DESC")
    vendors = cur.fetchall()

    cur.close()
    conn.close()

    order_html = ""

    for order in orders:
        oid = order["id"]
        order_id = html.escape(order["order_id"])
        customer = html.escape(order["customer"])
        product = html.escape(order["product"])
        status = html.escape(order["status"])

        order_html += f"""
        <div class="box">
            <h3>{order_id}</h3>
            <p><b>Product:</b> {product}</p>
            <p><b>Customer:</b> {customer}</p>
            <p><b>Amount:</b> ₦{order["amount"]:,}</p>
            <p><b>Supplier:</b> {html.escape(order["business_name"] or "None")}</p>
            <p><b>Commission:</b> ₦{float(order["commission_amount"] or 0):,.2f}</p>
            <p><b>Status:</b> {status}</p>

            <form method="POST">
                <input type="hidden" name="order_db_id" value="{oid}">
                <select name="status">
                    <option>Pending</option>
                    <option>Confirmed</option>
                    <option>Shipped</option>
                    <option>Delivered</option>
                </select>
                <button type="submit">Update Status</button>
            </form>
        </div>
        """

    product_html = ""

    for product in products:
        product_html += f"""
        <div class="box">
            <h3>{html.escape(product["product_name"])}</h3>
            <p>₦{product["price"]:,}</p>
            <p>Commission: {product["commission_percent"]}%</p>
            <p>Supplier: {html.escape(product["business_name"] or "None")}</p>
        </div>
        """

    vendor_html = ""

    for vendor in vendors:
        vendor_html += f"""
        <div class="box">
            <h3>{html.escape(vendor["business_name"])}</h3>
            <p>{html.escape(vendor["name"])}</p>
            <p>{html.escape(vendor["phone"])}</p>
        </div>
        """

    body = """
    <h1>JINJA Admin Panel</h1>

    <h2>Orders</h2>
    """ + (order_html or "<p>No orders yet.</p>") + """

    <h2>Products</h2>
    """ + (product_html or "<p>No products yet.</p>") + """

    <h2>Vendors</h2>
    """ + (vendor_html or "<p>No vendors yet.</p>")

    return page("JINJA Admin Panel", body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
