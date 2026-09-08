from flask import Flask, request, redirect, url_for
import os
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

    # EXISTING ORDERS TABLE
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

    # EXISTING VENDORS / SUPPLIERS TABLE
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

    # NEW PRODUCTS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            vendor_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            commission_percent INTEGER NOT NULL DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add supplier information to orders if it does not already exist
    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS vendor_id INTEGER
    """)

    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS commission_amount INTEGER DEFAULT 0
    """)

    # Sample order from your existing system
    cur.execute("""
        INSERT INTO orders
        (order_id, product, customer, phone, address, amount, payment, status)
        VALUES
        (
            'JINJA-8893429',
            'Tecno Camon Series',
            'Kingsley Samuel',
            '08000000000',
            'Lagos',
            310000,
            'Pay on delivery',
            'Pending'
        )
        ON CONFLICT (order_id) DO NOTHING
    """)

    conn.commit()
    cur.close()
    conn.close()


try:
    init_db()
except Exception as e:
    print("Database initialization error:", e)


# =========================
# HOME / MARKETPLACE
# =========================

@app.route("/")
def home():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            products.*,
            vendors.business_name
        FROM products
        JOIN vendors
        ON products.vendor_id = vendors.id
        ORDER BY products.id DESC
    """)

    products = cur.fetchall()

    cur.close()
    conn.close()

    product_html = ""

    for product in products:

        product_html += f"""
        <div style="
            border:1px solid #ddd;
            padding:15px;
            margin:15px 0;
            border-radius:10px;
        ">

            <h3>{product["product_name"]}</h3>

            <p>
                {product["description"] or ""}
            </p>

            <p>
                <b>Price:</b>
                ₦{product["price"]:,}
            </p>

            <p>
                <b>Supplier:</b>
                {product["business_name"]}
            </p>

            <a href="/order/{product["id"]}">
                <button>
                    Order Now
                </button>
            </a>

        </div>
        """

    if not product_html:
        product_html = """
        <p>
            No products have been added yet.
        </p>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>JINJA Marketplace</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >
    </head>

    <body>

        <h1>JINJA Marketplace</h1>

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

            <button type="submit">
                Track Order
            </button>

        </form>

        <br>

        <a href="/vendor/register">
            Become a Supplier
        </a>

        <br><br>

        <a href="/vendor/product">
            Add Product
        </a>

        <br><br>

        <a href="/admin">
            Admin Panel
        </a>

    </body>

    </html>
    """


# =========================
# CUSTOMER ORDER
# =========================

@app.route("/order/<int:product_id>", methods=["GET", "POST"])
def place_order(product_id):

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            products.*,
            vendors.business_name
        FROM products
        JOIN vendors
        ON products.vendor_id = vendors.id
        WHERE products.id = %s
    """, (product_id,))

    product = cur.fetchone()

    cur.close()
    conn.close()

    if not product:
        return """
        <h2>Product not found</h2>
        <a href="/">Back to JINJA</a>
        """

    if request.method == "POST":

        customer = request.form["customer"]
        phone = request.form["phone"]
        address = request.form["address"]
        payment = request.form["payment"]

        amount = product["price"]

        commission_amount = int(
            amount * product["commission_percent"] / 100
        )

        order_id = "JINJA-" + str(os.urandom(4).hex()).upper()

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

        return f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>Order Successful</title>

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
            >
        </head>

        <body>

            <h1>Order Received!</h1>

            <p>
                Your order has been successfully sent
                through JINJA.
            </p>

            <h2>Order ID</h2>

            <h2>{order_id}</h2>

            <p>
                <b>Product:</b>
                {product["product_name"]}
            </p>

            <p>
                <b>Amount:</b>
                ₦{amount:,}
            </p>

            <p>
                <b>Supplier:</b>
                {product["business_name"]}
            </p>

            <p>
                The supplier will handle delivery.
            </p>

            <a href="/track?order_id={order_id}">
                Track Your Order
            </a>

            <br><br>

            <a href="/">
                Back to JINJA
            </a>

        </body>

        </html>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Order Product</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >
    </head>

    <body>

        <h1>Order Product</h1>

        <h2>{product["product_name"]}</h2>

        <p>
            {product["description"] or ""}
        </p>

        <p>
            <b>Price:</b>
            ₦{product["price"]:,}
        </p>

        <p>
            <b>Supplier:</b>
            {product["business_name"]}
        </p>

        <hr>

        <form method="POST">

            <input
                name="customer"
                placeholder="Your Name"
                required
            >

            <br><br>

            <input
                name="phone"
                placeholder="Phone Number"
                required
            >

            <br><br>

            <textarea
                name="address"
                placeholder="Delivery Address"
                required
            ></textarea>

            <br><br>

            <select name="payment" required>

                <option value="">
                    Select Payment
                </option>

                <option value="Pay on delivery">
                    Pay on delivery
                </option>

                <option value="Online payment">
                    Online payment
                </option>

            </select>

            <br><br>

            <button type="submit">
                Place Order
            </button>

        </form>

        <br>

        <a href="/">
            Back to Marketplace
        </a>

    </body>

    </html>
    """


# =========================
# ORDER TRACKING
# =========================

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
        return """
        <h2>Order not found</h2>
        <a href="/">Go back</a>
        """

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

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Track Order</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >
    </head>

    <body>

        <h1>Order Tracking</h1>

        <h2>{order["order_id"]}</h2>

        <p>
            <b>Product:</b>
            {order["product"]}
        </p>

        <p>
            <b>Customer:</b>
            {order["customer"]}
        </p>

        <p>
            <b>Amount:</b>
            ₦{order["amount"]:,}
        </p>

        <p>
            <b>Payment:</b>
            {order["payment"]}
        </p>

        <p>
            <b>Address:</b>
            {order["address"]}
        </p>

        <h3>
            Status:
            {order["status"]}
        </h3>

        <ol>
            {progress}
        </ol>

        <a href="/">
            Back Home
        </a>

    </body>

    </html>
    """


# =========================
# ADMIN PANEL
# =========================

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
        SELECT
            orders.*,
            vendors.business_name
        FROM orders
        LEFT JOIN vendors
        ON orders.vendor_id = vendors.id
        ORDER BY orders.id DESC
    """)

    orders = cur.fetchall()

    cur.execute(
        "SELECT * FROM vendors ORDER BY id DESC"
    )

    vendors = cur.fetchall()

    cur.execute("""
        SELECT
            products.*,
            vendors.business_name
        FROM products
        JOIN vendors
        ON products.vendor_id = vendors.id
        ORDER BY products.id DESC
    """)

    products = cur.fetchall()

    cur.close()
    conn.close()

    order_html = ""

    for order in orders:

        commission = order["commission_amount"] or 0

        order_html += f"""
        <div>

            <h3>{order["order_id"]}</h3>

            <p>
                Product: {order["product"]}
            </p>

            <p>
                Customer: {order["customer"]}
            </p>

            <p>
                Phone: {order["phone"]}
            </p>

            <p>
                Address: {order["address"]}
            </p>

            <p>
                Amount:
                ₦{order["amount"]:,}
            </p>

            <p>
                Supplier:
                {order["business_name"] or "Not assigned"}
            </p>

            <p>
                JINJA Commission:
                ₦{commission:,}
            </p>

            <p>
                Current Status:
                <b>{order["status"]}</b>
            </p>

            <form method="POST">

                <input
                    type="hidden"
                    name="order_id"
                    value="{order["order_id"]}"
                >

                <select name="status">

                    <option value="Pending">
                        Pending
                    </option>

                    <option value="Confirmed">
                        Confirmed
                    </option>

                    <option value="Shipped">
                        Shipped
                    </option>

                    <option value="Delivered">
                        Delivered
                    </option>

                </select>

                <button type="submit">
                    Update Status
                </button>

            </form>

        </div>

        <hr>
        """

    vendor_html = ""

    for vendor in vendors:

        vendor_html += f"""
        <div>

            <h3>{vendor["business_name"]}</h3>

            <p>
                Vendor:
                {vendor["vendor_name"]}
            </p>

            <p>
                Phone:
                {vendor["phone"]}
            </p>

            <p>
                Email:
                {vendor["email"]}
            </p>

            <p>
                Category:
                {vendor["category"]}
            </p>

            <p>
                Address:
                {vendor["address"]}
            </p>

        </div>

        <hr>
        """

    product_html = ""

    for product in products:

        product_html += f"""
        <div>

            <h3>{product["product_name"]}</h3>

            <p>
                Supplier:
                {product["business_name"]}
            </p>

            <p>
                Price:
                ₦{product["price"]:,}
            </p>

            <p>
                JINJA Commission:
                {product["commission_percent"]}%
            </p>

        </div>

        <hr>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>JINJA Admin</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

    </head>

    <body>

        <h1>JINJA Admin Panel</h1>

        <h2>Orders</h2>

        {order_html}

        <h2>Registered Suppliers</h2>

        {vendor_html}

        <h2>Products</h2>

        {product_html}

        <br>

        <a href="/">
            Back Home
        </a>

    </body>

    </html>
    """


# =========================
# SUPPLIER REGISTRATION
# =========================

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
            (
                vendor_name,
                business_name,
                phone,
                email,
                address,
                category
            )
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
        <h2>Supplier registration successful!</h2>

        <p>
            Your company can now add products to JINJA.
        </p>

        <a href="/vendor/product">
            Add Your Product
        </a>

        <br><br>

        <a href="/">
            Back to JINJA
        </a>
        """

    return """
    <!DOCTYPE html>
    <html>

    <head>

        <title>Become a Supplier</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

    </head>

    <body>

        <h1>Become a JINJA Supplier</h1>

        <form method="POST">

            <input
                name="vendor_name"
                placeholder="Your Name"
                required
            >

            <br><br>

            <input
                name="business_name"
                placeholder="Company / Business Name"
                required
            >

            <br><br>

            <input
                name="phone"
                placeholder="Phone Number"
                required
            >

            <br><br>

            <input
                name="email"
                type="email"
                placeholder="Email"
                required
            >

            <br><br>

            <input
                name="address"
                placeholder="Business Address"
                required
            >

            <br><br>

            <select name="category" required>

                <option value="">
                    Select Category
                </option>

                <option>
                    Phones & Electronics
                </option>

                <option>
                    Fashion
                </option>

                <option>
                    Beauty
                </option>

                <option>
                    Health
                </option>

                <option>
                    Home & Living
                </option>

                <option>
                    Food
                </option>

                <option>
                    Other
                </option>

            </select>

            <br><br>

            <button type="submit">
                Register Company
            </button>

        </form>

        <br>

        <a href="/">
            Back Home
        </a>

    </body>

    </html>
    """


# =========================
# ADD PRODUCT
# =========================

@app.route("/vendor/product", methods=["GET", "POST"])
def vendor_product():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDi
