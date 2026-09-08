from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)

DATABASE = "jinja.db"

STATUS_STEPS = [
    "Pending",
    "Confirmed",
    "Shipped",
    "Delivered"
]


# =============================
# DATABASE
# =============================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    # Create the sample order only if it doesn't already exist
    existing = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?",
        ("JINJA-8893429",)
    ).fetchone()

    if existing is None:
        conn.execute("""
            INSERT INTO orders
            (order_id, customer, product, amount, payment, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "JINJA-8893429",
            "Kingsley Samuel",
            "Tecno Camon Series",
            310000,
            "Pay on delivery",
            "Pending"
        ))

    conn.commit()
    conn.close()


# =============================
# HOME
# =============================

@app.route("/")
def home():
    return """
    <h1>JINJA Marketplace</h1>

    <p>Welcome to Jinja.</p>

    <a href="/track/JINJA-8893429">
        <button>Track your order</button>
    </a>

    <br><br>

    <a href="/admin">
        <button>Admin Order Management</button>
    </a>
    """


# =============================
# TRACK ORDER
# =============================

@app.route("/track/<order_id>")
def track_order(order_id):

    conn = get_db()

    order = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?",
        (order_id,)
    ).fetchone()

    conn.close()

    if order is None:
        return """
        <h2>Order not found</h2>
        <a href="/">Back to marketplace</a>
        """, 404

    current_index = STATUS_STEPS.index(order["status"])

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Track Your Order - JINJA</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }

            .box {
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 3px 12px rgba(0,0,0,0.1);
            }

            h1 {
                text-align: center;
            }

            .info {
                line-height: 1.8;
            }

            .step {
                padding: 12px;
                margin: 8px 0;
                border-radius: 8px;
                background: #eeeeee;
            }

            .done {
                background: #d9f7df;
                color: #14752c;
                font-weight: bold;
            }

            .back {
                display: block;
                text-align: center;
                margin-top: 20px;
            }

        </style>
    </head>

    <body>

        <div class="box">

            <h1>Track your order</h1>

            <h3>{{ order["order_id"] }}</h3>

            <div class="info">

                <b>Customer:</b>
                {{ order["customer"] }}
                <br>

                <b>Product:</b>
                {{ order["product"] }}
                <br>

                <b>Amount:</b>
                ₦{{ "{:,}".format(order["amount"]) }}
                <br>

                <b>Payment:</b>
                {{ order["payment"] }}
                <br>

                <b>Status:</b>
                {{ order["status"] }}

            </div>

            <h3>Order progress</h3>

            {% for step in steps %}

                {% if loop.index0 <= current_index %}

                    <div class="step done">
                        ✓ {{ step }}
                    </div>

                {% else %}

                    <div class="step">
                        ○ {{ step }}
                    </div>

                {% endif %}

            {% endfor %}

            <a class="back" href="/">
                ← Back to Marketplace
            </a>

        </div>

    </body>

    </html>
    """,
    order=order,
    steps=STATUS_STEPS,
    current_index=current_index
    )


# =============================
# ADMIN
# =============================

@app.route("/admin")
def admin():

    conn = get_db()

    orders = conn.execute(
        "SELECT * FROM orders ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>

    <html>

    <head>

        <title>JINJA Admin</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            .order {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 15px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }

            select {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }

            button {
                padding: 10px 15px;
                border: none;
                border-radius: 8px;
                background: #111;
                color: white;
                cursor: pointer;
            }

            .track {
                display: inline-block;
                margin-top: 15px;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>JINJA Admin</h1>

            <h2>Orders</h2>

            {% for order in orders %}

                <div class="order">

                    <h3>{{ order["order_id"] }}</h3>

                    <p>
                        <b>Customer:</b>
                        {{ order["customer"] }}
                    </p>

                    <p>
                        <b>Product:</b>
                        {{ order["product"] }}
                    </p>

                    <p>
                        <b>Amount:</b>
                        ₦{{ "{:,}".format(order["amount"]) }}
                    </p>

                    <p>
                        <b>Payment:</b>
                        {{ order["payment"] }}
                    </p>

                    <p>
                        <b>Current Status:</b>
                        {{ order["status"] }}
                    </p>

                    <form
                        method="POST"
                        action="/admin/update-status/{{ order['order_id'] }}"
                    >

                        <select name="status">

                            {% for status in steps %}

                                <option
                                    value="{{ status }}"
                                    {% if status == order["status"] %}
                                        selected
                                    {% endif %}
                                >
                                    {{ status }}
                                </option>

                            {% endfor %}

                        </select>

                        <button type="submit">
                            Update Status
                        </button>

                    </form>

                    <a
                        class="track"
                        href="/track/{{ order['order_id'] }}"
                    >
                        Track Customer Order
                    </a>

                </div>

            {% endfor %}

        </div>

    </body>

    </html>
    """,
    orders=orders,
    steps=STATUS_STEPS
    )


# =============================
# UPDATE STATUS
# =============================

@app.route(
    "/admin/update-status/<order_id>",
    methods=["POST"]
)
def update_status(order_id):

    new_status = request.form.get("status")

    if new_status not in STATUS_STEPS:
        return "Invalid status", 400

    conn = get_db()

    conn.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE order_id = ?
        """,
        (new_status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# =============================
# START DATABASE
# =============================

init_db()


# =============================
# RUN APP
# =============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
