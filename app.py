from flask import Flask, request, redirect, url_for, render_template_string
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            business TEXT
        )
    """)
    cur.execute("""
        ALTER TABLE vendors
        ADD COLUMN IF NOT EXISTS business TEXT
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC NOT NULL,
            vendor TEXT,
            description TEXT
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
            status TEXT NOT NULL DEFAULT 'Order received'
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JINJA Marketplace</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                background: #f5f5f5;
                color: #222;
            }

            header {
                background: #111;
                color: white;
                padding: 20px;
                text-align: center;
            }

            .container {
                max-width: 900px;
                margin: 30px auto;
                padding: 20px;
            }

            .card {
                background: white;
                padding: 25px;
                margin-bottom: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            a, button {
                display: inline-block;
                padding: 12px 18px;
                margin: 5px;
                border: none;
                border-radius: 8px;
                background: #111;
                color: white;
                text-decoration: none;
                cursor: pointer;
            }

            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                box-sizing: border-box;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        </style>
    </head>

    <body>
        <header>
            <h1>JINJA Marketplace</h1>
            <p>Buy. Sell. Track your order.</p>
        </header>

        <div class="container">

            <div class="card">
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
            </div>

            <div class="card">
                <h2>Become a Vendor</h2>
                <p>Register your business and start selling on JINJA.</p>
                <a href="/vendor">Vendor Registration</a>
            </div>

            <div class="card">
                <h2>Admin</h2>
                <a href="/admin">Admin Panel</a>
            </div>

        </div>
    </body>
    </html>
    """)


@app.route("/vendor", methods=["GET", "POST"])
def vendor():
    message = ""

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        business = request.form.get("business")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO vendors (name, phone, email, business)
            VALUES (%s, %s, %s, %s)
        """, (name, phone, email, business))

        conn.commit()
        cur.close()
        conn.close()

        message = "Vendor registration successful!"

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vendor Registration - JINJA</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .box {
                max-width: 600px;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }

            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                box-sizing: border-box;
            }

            button, a {
                background: #111;
                color: white;
                padding: 12px 18px;
                border: none;
                text-decoration: none;
                border-radius: 8px;
            }

            .success {
                color: green;
                font-weight: bold;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <h1>Become a Vendor</h1>

            {% if message %}
                <p class="success">{{ message }}</p>
            {% endif %}

            <form method="post">

                <label>Name</label>
                <input type="text" name="name" required>

                <label>Phone</label>
                <input type="text" name="phone" required>

                <label>Email</label>
                <input type="email" name="email">

                <label>Business Name</label>
                <input type="text" name="business">

                <button type="submit">
                    Register
                </button>

            </form>

            <br><br>

            <a href="/">Back to Marketplace</a>

        </div>

    </body>
    </html>
    """, message=message)


@app.route("/track")
def track():
    order_id = request.args.get("order_id")

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM orders
        WHERE order_id = %s
    """, (order_id,))

    order = cur.fetchone()

    cur.close()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Track Order - JINJA</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .box {
                max-width: 650px;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }

            .status {
                font-size: 22px;
                font-weight: bold;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 18px;
                background: #111;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <h1>Track Your Order</h1>

            {% if order %}

                <h2>Order: {{ order.order_id }}</h2>

                <p>
                    <strong>Product:</strong>
                    {{ order.product }}
                </p>

                <p>
                    <strong>Customer:</strong>
                    {{ order.customer }}
                </p>

                <p>
                    <strong>Phone:</strong>
                    {{ order.phone }}
                </p>

                <p>
                    <strong>Address:</strong>
                    {{ order.address }}
                </p>

                <p class="status">
                    Status: {{ order.status }}
                </p>

            {% else %}

                <p>
                    ❌ Order not found.
                </p>

                <p>
                    Please check your Order ID and try again.
                </p>

            {% endif %}

            <a href="/">Back to Marketplace</a>

        </div>

    </body>
    </html>
    """, order=order)


@app.route("/admin")
def admin():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM vendors
        ORDER BY id DESC
    """)
    vendors = cur.fetchall()

    cur.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
    """)
    products = cur.fetchall()

    cur.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
    """)
    orders = cur.fetchall()

    cur.close()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel - JINJA</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .container {
                max-width: 1000px;
                margin: auto;
            }

            .card {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
                overflow-x: auto;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }

            th {
                background: #eee;
            }

            a {
                display: inline-block;
                background: #111;
                color: white;
                padding: 12px 18px;
                text-decoration: none;
                border-radius: 8px;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>JINJA Admin Panel</h1>

            <div class="card">

                <h2>Vendors</h2>

                {% if vendors %}

                <table>

                    <tr>
                        <th>Name</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Business</th>
                    </tr>

                    {% for vendor in vendors %}

                    <tr>
                        <td>{{ vendor.name }}</td>
                        <td>{{ vendor.phone }}</td>
                        <td>{{ vendor.email }}</td>
                        <td>{{ vendor.business }}</td>
                    </tr>

                    {% endfor %}

                </table>

                {% else %}

                <p>No vendors registered yet.</p>

                {% endif %}

            </div>


            <div class="card">

                <h2>Products</h2>

                {% if products %}

                <table>

                    <tr>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Vendor</th>
                        <th>Description</th>
                    </tr>

                    {% for product in products %}

                    <tr>
                        <td>{{ product.name }}</td>
                        <td>{{ product.price }}</td>
                        <td>{{ product.vendor }}</td>
                        <td>{{ product.description }}</td>
                    </tr>

                    {% endfor %}

                </table>

                {% else %}

                <p>No products yet.</p>

                {% endif %}

            </div>


            <div class="card">

                <h2>Orders</h2>

                {% if orders %}

                <table>

                    <tr>
                        <th>Order ID</th>
                        <th>Product</th>
                        <th>Customer</th>
                        <th>Phone</th>
                        <th>Address</th>
                        <th>Status</th>
                    </tr>

                    {% for order in orders %}

                    <tr>
                        <td>{{ order.order_id }}</td>
                        <td>{{ order.product }}</td>
                        <td>{{ order.customer }}</td>
                        <td>{{ order.phone }}</td>
                        <td>{{ order.address }}</td>
                        <td>{{ order.status }}</td>
                    </tr>

                    {% endfor %}

                </table>

                {% else %}

                <p>No orders yet.</p>

                {% endif %}

            </div>

            <a href="/">Back to Marketplace</a>

        </div>

    </body>
    </html>
    """)


@app.route("/health")
def health():
    return "JINJA is running successfully!"


try:
    init_db()
except Exception as e:
    print("Database initialization error:", e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
