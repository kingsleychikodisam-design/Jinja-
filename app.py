from flask import Flask, request, redirect, url_for, render_template_string, jsonify

app = Flask(__name__)

# -----------------------------
# ORDERS
# -----------------------------
orders = [
    {
        "order_id": "JINJA-8893429",
        "customer": "Kingsley Samuel",
        "product": "Tecno Camon Series",
        "amount": 310000,
        "payment": "Pay on delivery",
        "status": "Pending"
    }
]

# -----------------------------
# STATUS ORDER
# -----------------------------
STATUS_STEPS = [
    "Pending",
    "Confirmed",
    "Shipped",
    "Delivered"
]


# -----------------------------
# HOME PAGE
# -----------------------------
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


# -----------------------------
# TRACK ORDER
# -----------------------------
@app.route("/track/<order_id>")
def track_order(order_id):

    order = next(
        (o for o in orders if o["order_id"] == order_id),
        None
    )

    if not order:
        return """
        <h2>Order not found</h2>
        <a href="/">Back to marketplace</a>
        """, 404

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Track your order</title>

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

            .order-info {
                line-height: 1.8;
            }

            .status {
                margin-top: 25px;
            }

            .step {
                padding: 12px;
                margin: 8px 0;
                border-radius: 8px;
                background: #eee;
            }

            .done {
                background: #d9f7df;
                color: #14752c;
                font-weight: bold;
            }

            .current {
                border: 2px solid #14752c;
                font-weight: bold;
            }

            .back {
                display: block;
                margin-top: 20px;
                text-align: center;
            }
        </style>
    </head>

    <body>

    <div class="box">

        <h1>Track your order</h1>

        <h3>{{ order.order_id }}</h3>

        <div class="order-info">
            <b>Customer:</b> {{ order.customer }}<br>
            <b>Product:</b> {{ order.product }}<br>
            <b>Amount:</b> ₦{{ "{:,}".format(order.amount) }}<br>
            <b>Payment:</b> {{ order.payment }}<br>
            <b>Status:</b> {{ order.status }}
        </div>

        <div class="status">

            <h3>Order progress</h3>

            {% for step in steps %}

                {% if steps.index(step) <= current_index %}

                    <div class="step done">
                        ✓ {{ step }}
                    </div>

                {% else %}

                    <div class="step">
                        ○ {{ step }}
                    </div>

                {% endif %}

            {% endfor %}

        </div>

        <a class="back" href="/">
            ← Back to Marketplace
        </a>

    </div>

    </body>
    </html>
    """,
    order=order,
    steps=STATUS_STEPS,
    current_index=STATUS_STEPS.index(order["status"])
    )


# -----------------------------
# ADMIN PAGE
# -----------------------------
@app.route("/admin")
def admin():

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
                margin-top: 10px;
            }

            button {
                padding: 10px 15px;
                border: none;
                border-radius: 8px;
                background: #111;
                color: white;
                cursor: pointer;
                margin-left: 5px;
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

            <h3>{{ order.order_id }}</h3>

            <p>
                <b>Customer:</b> {{ order.customer }}
            </p>

            <p>
                <b>Product:</b> {{ order.product }}
            </p>

            <p>
                <b>Amount:</b>
                ₦{{ "{:,}".format(order.amount) }}
            </p>

            <p>
                <b>Payment:</b> {{ order.payment }}
            </p>

            <p>
                <b>Current Status:</b> {{ order.status }}
            </p>

            <form method="POST"
                  action="/admin/update-status/{{ order.order_id }}">

                <label>
                    Change status:
                </label>

                <select name="status">

                    {% for status in steps %}

                    <option value="{{ status }}"
                        {% if status == order.status %}
                            selected
                        {% endif %}>
                        {{ status }}
                    </option>

                    {% endfor %}

                </select>

                <button type="submit">
                    Update Status
                </button>

            </form>

            <a class="track"
               href="/track/{{ order.order_id }}">
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


# -----------------------------
# UPDATE ORDER STATUS
# -----------------------------
@app.route("/admin/update-status/<order_id>", methods=["POST"])
def update_status(order_id):

    new_status = request.form.get("status")

    if new_status not in STATUS_STEPS:
        return "Invalid status", 400

    for order in orders:

        if order["order_id"] == order_id:

            order["status"] = new_status

            break

    return redirect(url_for("admin"))


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
