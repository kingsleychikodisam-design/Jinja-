from flask import Flask, request, redirect, url_for
import os
import html
import random
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
            vendor_name TEXT NOT NULL,
            business_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            category TEXT NOT NULL
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
            payment TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
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
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{html.escape(title)}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 20px auto;
                padding: 15px;
            }}
            input, select, textarea {{
                width: 100%;
                padding: 10px;
                margin: 6px 0 12px;
                box-sizing: border-box;
            }}
            button {{
                padding: 10px 18px;
            }}
            .box {{
                border: 1px solid #ddd;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """


@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT p.*, v.business_name
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        ORDER BY p.id DESC
    """)

    products = cur.fetchall()

    cur.close()
    conn.close()

    product_html = ""

    for product in products:
        product_html += f"""
        <div class="box">
            <h2>{html.escape(product["product_name"])}</h2>
            <p>{html.escape(product["description"] or "")}</p>
            <p><b>Price:</b> ₦{int(product["price"]):,}</p>
            <p><b>Supplier:</b>
                {html.escape(product["business_name"] or "JINJA")}
            </p>
            <a href="/order/{product["id"]}">
                <button>Order Now</button>
            </a>
        </div>
        """

    if not product_html:
        product_html = """
        <div class="box">
            <p>No products have been added yet.</p>
        </div>
        """

    body = f"""
        <h1>JINJA Marketplace</h1>

        <p>Shop products from our suppliers.</p>

        <h2>Products</h2>

        {product_html}

        <hr>

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
    """

    return page("JINJA Marketplace", body)
    @app.route("/order/<int:product_id>", methods=["GET", "POST"])
def place_order(product_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT p.*, v.business_name
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        WHERE p.id = %s
    """, (product_id,))

    product = cur.fetchone()

    cur.close()
    conn.close()

    if not product:
        return page(
            "Product Not Found",
            "<h2>Product not found.</h2><a href='/'>Back Home</a>"
        )

    if request.method == "POST":
        customer = request.form["customer"]
        phone = request.form["phone"]
        address = request.form["address"]
        payment = request.form["payment"]

        order_id = "JINJA-" + str(random.randint(1000000, 9999999))
        amount = int(product["price"])

        commission_percent = float(
            product["commission_percent"] or 0
        )

        commission_amount = amount * commission_percent / 100

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO orders
            (
                order_id,
                product,
                customer,
                phone,
                address,
                amount,
                payment,
                status,
                vendor_id,
                commission_amount
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            product["product_name"],
            customer,
            phone,
            address,
            amount,
            payment,
            "Pending",
            product["vendor_id"],
            commission_amount
        ))

        conn.commit()
        cur.close()
        conn.close()

        return page(
            "Order Successful",
            f"""
            <h1>Order Received!</h1>

            <p>Your order has been submitted to JINJA.</p>

            <h2>Order ID: {order_id}</h2>

            <p>Please save this Order ID.</p>

            <a href="/track?order_id={order_id}">
                <button>Track Order</button>
            </a>

            <br><br>

            <a href="/">Back to Marketplace</a>
            """
        )

    body = f"""
        <h1>Order Product</h1>

        <div class="box">
            <h2>{html.escape(product["product_name"])}</h2>

            <p>{html.escape(product["description"] or "")}</p>

            <p>
                <b>Price:</b>
                ₦{int(product["price"]):,}
            </p>

            <p>
                <b>Supplier:</b>
                {html.escape(product["business_name"] or "JINJA")}
            </p>
        </div>

        <form method="POST">

            <label>Your Name</label>
            <input
                name="customer"
                placeholder="Enter your name"
                required
            >

            <label>Phone Number</label>
            <input
                name="phone"
                placeholder="Enter your phone number"
                required
            >

            <label>Delivery Address</label>
            <textarea
                name="address"
                placeholder="Enter your delivery address"
                required
            ></textarea>

            <label>Payment</label>
            <select name="payment" required>
                <option value="Pay on delivery">
                    Pay on delivery
                </option>
            </select>

            <button type="submit">
                Place Order
            </button>

        </form>

        <br>

        <a href="/">Back to Marketplace</a>
    """

    return page("Order Product", body)


@app.route("/track")
def track():
    order_id = request.args.get("order_id")

    if not order_id:
        return redirect(url_for("home"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT o.*, v.business_name
        FROM orders o
        LEFT JOIN vendors v ON o.vendor_id = v.id
        WHERE o.order_id = %s
    """, (order_id,))

    order = cur.fetchone()

    cur.close()
    conn.close()

    if not order:
        return page(
            "Order Not Found",
            """
            <h2>Order not found.</h2>
            <p>Please check your Order ID.</p>
            <a href="/">Go Back</a>
            """
        )

    statuses = [
        "Pending",
        "Confirmed",
        "Shipped",
        "Delivered"
    ]

    current_status = order["status"]

    if current_status not in statuses:
        current_status = "Pending"

    current_index = statuses.index(current_status)

    progress = ""

    for index, status in enumerate(statuses):
        if index <= current_index:
            progress += f"<li><b>✓ {status}</b></li>"
        else:
            progress += f"<li>{status}</li>"

    body = f"""
        <h1>Order Tracking</h1>

        <h2>{html.escape(order["order_id"])}</h2>

        <p>
            <b>Product:</b>
            {html.escape(order["product"])}
        </p>

        <p>
            <b>Customer:</b>
            {html.escape(order["customer"])}
        </p>

        <p>
            <b>Amount:</b>
            ₦{int(order["amount"]):,}
        </p>

        <p>
            <b>Payment:</b>
            {html.escape(order["payment"])}
        </p>

        <p>
            <b>Supplier:</b>
            {html.escape(order["business_name"] or "JINJA")}
        </p>

        <h3>Status: {html.escape(order["status"])}</h3>

        <ol>
            {progress}
        </ol>

        <a href="/">Back Home</a>
    """

    return page("Track Order", body)
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

        return page(
            "Registration Successful",
            """
            <h2>Vendor registration successful!</h2>
            <p>Your business has been registered with JINJA.</p>
            <a href="/">Back to JINJA</a>
            """
        )

    body = """
        <h1>Become a JINJA Vendor</h1>

        <form method="POST">

            <label>Your Name</label>
            <input
                name="vendor_name"
                placeholder="Your Name"
                required
            >

            <label>Business Name</label>
            <input
                name="business_name"
                placeholder="Business Name"
                required
            >

            <label>Phone Number</label>
            <input
                name="phone"
                placeholder="Phone Number"
                required
            >

            <label>Email</label>
            <input
                name="email"
                type="email"
                placeholder="Email"
                required
            >

            <label>Business Address</label>
            <input
                name="address"
                placeholder="Business Address"
                required
            >

            <label>Category</label>

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

            <button type="submit">
                Register as Vendor
            </button>

        </form>

        <br>

        <a href="/">Back Home</a>
    """

    return page("Become a Vendor", body)


@app.route("/vendor/product", methods=["GET", "POST"])
def vendor_product():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM vendors
        ORDER BY business_name
    """)

    vendors = cur.fetchall()

    cur.close()
    conn.close()

    if request.method == "POST":
        vendor_id = request.form["vendor_id"]
        product_name = request.form["product_name"]
        description = request.form["description"]
        price = int(request.form["price"])
        commission = float(request.form["commission"])

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO products
            (
                vendor_id,
                product_name,
                description,
                price,
                commission_percent
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            vendor_id,
            product_name,
            description,
            price,
            commission
        ))

        conn.commit()
        cur.close()
        conn.close()

        return page(
            "Product Added",
            """
            <h2>Product added successfully!</h2>

            <a href="/vendor/product">
                Add another product
            </a>

            <br><br>

            <a href="/">
                View Marketplace
            </a>
            """
        )

    vendor_options = ""

    for vendor in vendors:
        vendor_options += f"""
        <option value="{vendor["id"]}">
            {html.escape(vendor["business_name"])}
        </option>
        """

    body = f"""
        <h1>Add Product</h1>

        <form method="POST">

            <label>Supplier</label>

            <select name="vendor_id" required>
                <option value="">
                    Select Supplier
                </option>

                {vendor_options}
            </select>

            <label>Product Name</label>

            <input
                name="product_name"
                placeholder="Product Name"
                required
            >

            <label>Description</label>

            <textarea
                name="description"
                placeholder="Product Description"
            ></textarea>

            <label>Price</label>

            <input
                name="price"
                type="number"
                placeholder="Product Price"
                required
            >

            <label>JINJA Commission (%)</label>

            <input
                name="commission"
                type="number"
                step="0.01"
                value="10"
                required
            >

            <button type="submit">
                Add Product
            </button>

        </form>

        <br>

        <a href="/admin">Admin Panel</a>

        <br><br>

        <a href="/">Marketplace</a>
    """

    return page("Add Product", body)
    @app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        order_id = request.form["order_id"]
        status = request.form["status"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE orders
            SET status = %s
            WHERE order_id = %s
        """, (status, order_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("admin"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT o.*, v.business_name
        FROM orders o
        LEFT JOIN vendors v ON o.vendor_id = v.id
        ORDER BY o.id DESC
    """)
    orders = cur.fetchall()

    cur.execute("""
        SELECT p.*, v.business_name
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        ORDER BY p.id DESC
    """)
    products = cur.fetchall()

    cur.execute("""
        SELECT * FROM vendors
        ORDER BY id DESC
    """)
    vendors = cur.fetchall()

    cur.close()
    conn.close()

    order_html = ""

    for order in orders:
        order_html += f"""
        <div class="box">
            <h3>{html.escape(order["order_id"])}</h3>

            <p>
                <b>Product:</b>
                {html.escape(order["product"])}
            </p>

            <p>
                <b>Customer:</b>
                {html.escape(order["customer"])}
            </p>

            <p>
                <b>Phone:</b>
                {html.escape(order["phone"])}
            </p>

            <p>
                <b>Address:</b>
                {html.escape(order["address"])}
            </p>

            <p>
                <b>Amount:</b>
                ₦{int(order["amount"]):,}
            </p>

            <p>
                <b>Supplier:</b>
                {html.escape(order["business_name"] or "Not assigned")}
            </p>

            <p>
                <b>JINJA Commission:</b>
                ₦{float(order["commission_amount"] or 0):,.2f}
            </p>

            <p>
                <b>Status:</b>
                {html.escape(order["status"])}
            </p>

            <form method="POST">
                <input
                    type="hidden"
                    name="order_id"
                    value="{html.escape(order["order_id"])}"
                >

                <select name="status">
                    <option>Pending</option>
                    <option>Confirmed</option>
                    <option>Shipped</option>
                    <option>Delivered</option>
                </select>

                <button type="submit">
                    Update Status
                </button>
            </form>
        </div>
        """

    product_html = ""

    for product in products:
        product_html += f"""
        <div class="box">
            <h3>{html.escape(product["product_name"])}</h3>

            <p>
                Price:
                ₦{int(product["price"]):,}
            </p>

            <p>
                Supplier:
                {html.escape(product["business_name"] or "Not assigned")}
            </p>

            <p>
                Commission:
                {float(product["commission_percent"] or 0):.2f}%
            </p>
        </div>
        """

    vendor_html = ""

    for vendor in vendors:
        vendor_html += f"""
        <div class="box">
            <h3>{html.escape(vendor["business_name"])}</h3>

            <p>
                Vendor:
                {html.escape(vendor["vendor_name"])}
            </p>

            <p>
                Phone:
                {html.escape(vendor["phone"])}
            </p>

            <p>
                Email:
                {html.escape(vendor["email"])}
            </p>

            <p>
                Category:
                {html.escape(vendor["category"])}
            </p>
        </div>
        """

    body = f"""
        <h1>JINJA Admin Panel</h1>

        <p>
            <a href="/vendor/product">
                Add Supplier Product
            </a>
        </p>

        <hr>

        <h2>Orders</h2>
        {order_html or "<p>No orders yet.</p>"}

        <hr>

        <h2>Products</h2>
        {product_html or "<p>No products yet.</p>"}

        <hr>

        <h2>Registered Suppliers</h2>
        {vendor_html or "<p>No suppliers yet.</p>"}

        <br>

        <a href="/">Back Home</a>
    """

    return page("JINJA Admin", body)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
        )
