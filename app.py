Yes. Now that you have given me the entire app.py, I can give you the complete replacement. You were right to insist on this.
I found the actual problem:
Your init_db() has incorrect indentation around the ALTER TABLE statements.
Your existing database has a vendor_name column that can still require a value.
Your registration code inserts only business_name, name, phone, email, so vendor_name can become NULL.
The replacement below repairs old vendor records and explicitly supplies vendor_name when registering a new vendor.
I also made the database setup work with both your existing database and a fresh database.
Replace the ENTIRE contents of app.py
Do not edit individual sections. Delete everything currently inside app.py, then paste this entire code:
from flask import Flask, request
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


# ============================================================
# DATABASE SETUP
# ============================================================

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # --------------------------------------------------------
    # VENDORS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id SERIAL PRIMARY KEY,
            business_name TEXT NOT NULL DEFAULT '',
            vendor_name TEXT NOT NULL DEFAULT '',
            name TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT ''
        )
    """)

    # Make sure older JINJA databases have these columns.
    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS business_name TEXT DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS vendor_name TEXT DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS name TEXT DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS phone TEXT DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS email TEXT DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS address TEXT DEFAULT ''
    """)

    # --------------------------------------------------------
    # REPAIR OLD VENDOR RECORDS
    # --------------------------------------------------------

    cur.execute("""
        UPDATE vendors
        SET vendor_name = COALESCE(
            NULLIF(TRIM(vendor_name), ''),
            NULLIF(TRIM(name), ''),
            NULLIF(TRIM(business_name), ''),
            'Vendor'
        )
        WHERE vendor_name IS NULL
           OR TRIM(vendor_name) = ''
    """)

    cur.execute("""
        UPDATE vendors
        SET business_name = COALESCE(
            NULLIF(TRIM(business_name), ''),
            NULLIF(TRIM(vendor_name), ''),
            NULLIF(TRIM(name), ''),
            'JINJA Vendor'
        )
        WHERE business_name IS NULL
           OR TRIM(business_name) = ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ALTER COLUMN vendor_name SET DEFAULT ''
    """)

    cur.execute("""
        ALTER TABLE vendors
        ALTER COLUMN vendor_name SET NOT NULL
    """)

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

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
            vendor_id INTEGER REFERENCES vendors(id),
            commission_amount NUMERIC DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Make sure older order tables have these columns.
    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS vendor_id INTEGER
    """)

    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS commission_amount NUMERIC DEFAULT 0
    """)

    cur.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS created_at
        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """)

    conn.commit()

    cur.close()
    conn.close()


# Initialize database when application starts.
try:
    init_db()
    print("JINJA database initialized successfully.")
except Exception as e:
    print("Database initialization error:", e)


# ============================================================
# GENERAL PAGE DESIGN
# ============================================================

def page(title, body):

    return """
    <!DOCTYPE html>
    <html>
    <head>

        <title>""" + html.escape(title) + """ - JINJA</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
                color: #222;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            .nav {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                line-height: 2;
                box-shadow: 0 2px 8px #ddd;
            }

            .nav a {
                margin-right: 7px;
            }

            .box {
                background: white;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ddd;
            }

            input,
            textarea,
            select {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 16px;
            }

            textarea {
                min-height: 100px;
            }

            button,
            .button {
                background: #111;
                color: white;
                padding: 12px 18px;
                border: none;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                cursor: pointer;
                font-size: 15px;
            }

            button:hover,
            .button:hover {
                opacity: 0.85;
            }

            .price {
                font-size: 21px;
                font-weight: bold;
            }

            .success {
                color: green;
                font-weight: bold;
            }

            .error {
                color: #b00020;
                font-weight: bold;
            }

            .status {
                font-size: 20px;
                font-weight: bold;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="nav">

                <a href="/">Home</a> |

                <a href="/track">Track Order</a> |

                <a href="/vendor/register">
                    Become a Vendor
                </a> |

                <a href="/vendor/product">
                    Add Product
                </a> |

                <a href="/admin">
                    Admin Panel
                </a>

            </div>

            """ + body + """

        </div>

    </body>
    </html>
    """


# ============================================================
# HOME / MARKETPLACE
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    cur = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cur.execute("""
        SELECT
            products.*,
            vendors.business_name
        FROM products
        LEFT JOIN vendors
            ON products.vendor_id = vendors.id
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

            <p>
                Vendors can register and add products.
            </p>

            <a class="button"
               href="/vendor/register">
                Become a Vendor
            </a>

        </div>
        """

    for product in products:

        product_id = product["id"]

        name = html.escape(
            product["product_name"]
        )

        description = html.escape(
            product["description"] or ""
        )

        price = int(
            product["price"] or 0
        )

        vendor = html.escape(
            product["business_name"]
            or "JINJA"
        )

        items += f"""
        <div class="box">

            <h2>{name}</h2>

            <p>
                {description}
            </p>

            <p class="price">
                ₦{price:,}
            </p>

            <p>
                <b>Supplier:</b>
                {vendor}
            </p>

            <a class="button"
               href="/order/{product_id}">
                Order Now
            </a>

        </div>
        """

    body = """

    <div class="box">

        <h1>JINJA Marketplace</h1>

        <p>
            Buy products from trusted suppliers.
        </p>

        <a class="button"
           href="/vendor/register">
            Become a Vendor
        </a>

    </div>

    <div class="box">

        <h2>Track Your Order</h2>

        <a class="button"
           href="/track">
            Track Order
        </a>

    </div>

    """ + items

    return page(
        "JINJA Marketplace",
        body
    )


# ============================================================
# PLACE ORDER
# ============================================================

@app.route(
    "/order/<int:product_id>",
    methods=["GET", "POST"]
)
def place_order(product_id):

    conn = get_db()

    cur = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cur.execute(
        """
        SELECT *
        FROM products
        WHERE id = %s
        """,
        (product_id,)
    )

    product = cur.fetchone()

    if not product:

        cur.close()
        conn.close()

        return page(
            "Product Not Found",
            """
            <div class="box">

                <h2>
                    Product not found.
                </h2>

                <a class="button"
                   href="/">
                    Back to Marketplace
                </a>

            </div>
            """
        )

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    if request.method == "POST":

        customer = request.form.get(
            "customer",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        if not customer or not phone or not address:

            cur.close()
            conn.close()

            return page(
                "Order Error",
                f"""
                <div class="box">

                    <h2 class="error">
                        Please fill in all fields.
                    </h2>

                    <a class="button"
                       href="/order/{product_id}">
                        Go Back
                    </a>

                </div>
                """
            )

        amount = int(
            product["price"]
        )

        commission_percent = float(
            product["commission_percent"] or 0
        )

        commission = (
            amount *
            commission_percent /
            100
        )

        order_id = (
            "JINJA-" +
            str(
                random.randint(
                    1000000,
                    9999999
                )
            )
        )

        # Prevent accidental duplicate order ID.
        while True:

            cur.execute(
                """
                SELECT id
                FROM orders
                WHERE order_id = %s
                """,
                (order_id,)
            )

            existing = cur.fetchone()

            if not existing:
                break

            order_id = (
                "JINJA-" +
                str(
                    random.randint(
                        1000000,
                        9999999
                    )
                )
            )

        cur.execute(
            """
            INSERT INTO orders
            (
                order_id,
                product,
                customer,
                phone,
                address,
                amount,
                status,
                vendor_id,
                commission_amount
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                order_id,
                product["product_name"],
                customer,
                phone,
                address,
                amount,
                "Pending",
                product["vendor_id"],
                commission
            )
        )

        conn.commit()

        cur.close()
        conn.close()

        body = f"""

        <div class="box">

            <h1>
                Order Received!
            </h1>

            <p class="success">
                Your order has been created successfully.
            </p>

            <h2>
                Order ID:
                {html.escape(order_id)}
            </h2>

            <p>
                Keep this Order ID to track your order.
            </p>

            <a class="button"
               href="/track">
                Track Order
            </a>

        </div>

        """

        return page(
            "Order Received",
            body
        )

    # --------------------------------------------------------
    # ORDER FORM
    # --------------------------------------------------------

    name = html.escape(
        product["product_name"]
    )

    price = int(
        product["price"]
    )

    body = f"""

    <div class="box">

        <h1>
            Order {name}
        </h1>

        <h2>
            ₦{price:,}
        </h2>

        <form method="POST">

            <label>
                Your Name
            </label>

            <input
                name="customer"
                required
            >

            <label>
                Phone Number
            </label>

            <input
                name="phone"
                required
            >

            <label>
                Delivery Address
            </label>

            <textarea
                name="address"
                required
            ></textarea>

            <button type="submit">
                Place Order
            </button>

        </form>

    </div>

    """

    cur.close()
    conn.close()

    return page(
        "Place Order",
        body
    )


# ============================================================
# TRACK ORDER
# ============================================================

@app.route(
    "/track",
    methods=["GET", "POST"]
)
def track():

    order = None
    searched = False

    if request.method == "POST":

        searched = True

        order_id = request.form.get(
            "order_id",
            ""
        ).strip()

        conn = get_db()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute(
            """
            SELECT *
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,)
        )

        order = cur.fetchone()

        cur.close()
        conn.close()

    body = """

    <div class="box">

        <h1>
            Track Your Order
        </h1>

        <form method="POST">

            <label>
                Enter Order ID
            </label>

            <input
                name="order_id"
                placeholder="Example: JINJA-1234567"
                required
            >

            <button type="submit">
                Track Order
            </button>

        </form>

    </div>

    """

    if searched:

        if order:

            body += f"""

            <div class="box">

                <h2>
                    Order Found
                </h2>

                <p>
                    <b>Order ID:</b>
                    {html.escape(order["order_id"])}
                </p>

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

                <p class="status">
                    Status:
                    {html.escape(order["status"])}
                </p>

            </div>

            """

        else:

            body += """

            <div class="box">

                <h3 class="error">
                    Order not found.
                </h3>

                <p>
                    Please check your Order ID
                    and try again.
                </p>

            </div>

            """

    return page(
        "Track Order",
        body
    )


# ============================================================
# VENDOR REGISTRATION
# ============================================================

@app.route(
    "/vendor/register",
    methods=["GET", "POST"]
)
def vendor_register():

    error_message = ""

    if request.method == "POST":

        business_name = request.form.get(
            "business_name",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        if (
            not business_name
            or not name
            or not phone
        ):

            error_message = (
                "Business name, name and "
                "phone number are required."
            )

        else:

            conn = None
           
