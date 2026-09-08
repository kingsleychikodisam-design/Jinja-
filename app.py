from flask import Flask, send_from_directory, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

vendors = []
products = []

sample_orders = [
    {
        "order_id": "JINJA-1001",
        "product": "iPhone 15 128GB",
        "customer": "John",
        "phone": "08012345678",
        "address": "Lagos",
        "amount": "₦850,000",
        "status": "Pending"
    },
    {
        "order_id": "JINJA-1002",
        "product": "HP Core i5 Laptop",
        "customer": "David",
        "phone": "08123456789",
        "address": "Abuja",
        "amount": "₦690,000",
        "status": "Shipped"
    }
]


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")


# ---------------- VENDOR REGISTRATION ----------------

@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        vendors.append({
            "name": name,
            "email": email,
            "phone": phone,
            "password": password
        })

        return redirect(
            url_for(
                "vendor_dashboard",
                name=name,
                email=email,
                phone=phone
            )
        )

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jinja Vendor Registration</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 30px;
            }
            .box {
                max-width: 450px;
                margin: auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: black;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Become a Jinja Vendor</h2>

            <form method="POST">
                <input type="text" name="name" placeholder="Business Name" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="text" name="phone" placeholder="Phone Number" required>
                <input type="password" name="password" placeholder="Password" required>

                <button type="submit">Register</button>
            </form>
        </div>
    </body>
    </html>
    """)


# ---------------- VENDOR DASHBOARD ----------------

@app.route("/vendor/dashboard")
def vendor_dashboard():
    name = request.args.get("name", "Vendor")
    email = request.args.get("email", "")
    phone = request.args.get("phone", "")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vendor Dashboard</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }
            .header {
                background: black;
                color: white;
                padding: 20px;
                border-radius: 10px;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 25px;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
            }
            a {
                display: inline-block;
                padding: 12px 20px;
                background: black;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <div class="header">
            <h1>Jinja Vendor Dashboard</h1>
            <p>Welcome, {{ name }}</p>
            <p>{{ email }}</p>
            <p>{{ phone }}</p>
        </div>

        <div class="cards">

            <div class="card">
                <h2>📦 Add Product</h2>
                <p>Add a new product to Jinja.</p>
                <a href="/vendor/add-product">Add Product</a>
            </div>

            <div class="card">
                <h2>🛍️ My Products</h2>
                <p>View your products.</p>
                <a href="/vendor/products">My Products</a>
            </div>

            <div class="card">
                <h2>📋 Customer Orders</h2>
                <p>View and manage customer orders.</p>
                <a href="/vendor/orders">Customer Orders</a>
            </div>

        </div>

    </body>
    </html>
    """, name=name, email=email, phone=phone)


# ---------------- ADD PRODUCT ----------------

@app.route("/vendor/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        product = {
            "name": request.form.get("name"),
            "price": request.form.get("price"),
            "category": request.form.get("category"),
            "description": request.form.get("description"),
            "image": request.form.get("image")
        }

        products.append(product)

        return redirect(url_for("vendor_products"))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Product</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 30px;
            }

            .box {
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }

            input, textarea, select {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                box-sizing: border-box;
            }

            button {
                width: 100%;
                padding: 12px;
                background: black;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <h2>Add Product</h2>

            <form method="POST">

                <input
                    type="text"
                    name="name"
                    placeholder="Product Name"
                    required
                >

                <input
                    type="text"
                    name="price"
                    placeholder="Price"
                    required
                >

                <select name="category" required>
                    <option value="">Select Category</option>
                    <option value="Phones">Phones</option>
                    <option value="Laptops">Laptops</option>
                    <option value="Accessories">Accessories</option>
                </select>

                <textarea
                    name="description"
                    placeholder="Product Description"
                    rows="5"
                ></textarea>

                <input
                    type="text"
                    name="image"
                    placeholder="Product Image URL"
                >

                <button type="submit">Save Product</button>

            </form>

        </div>

    </body>
    </html>
    """)


# ---------------- MY PRODUCTS ----------------

@app.route("/vendor/products")
def vendor_products():

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Products</title>

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .product {
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 10px;
            }

            img {
                max-width: 150px;
                border-radius: 8px;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 15px;
                background: black;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <h1>My Products</h1>

        {% if products %}

            {% for product in products %}

            <div class="product">

                {% if product.image %}
                    <img src="{{ product.image }}">
                {% endif %}

                <h2>{{ product.name }}</h2>

                <p><strong>Price:</strong> {{ product.price }}</p>

                <p><strong>Category:</strong> {{ product.category }}</p>

                <p>{{ product.description }}</p>

            </div>

            {% endfor %}

        {% else %}

            <p>You have not added any products yet.</p>

        {% endif %}

        <a href="/vendor/dashboard">Back to Dashboard</a>

    </body>
    </html>
    """, products=products)


# ---------------- CUSTOMER ORDERS ----------------

@app.route("/vendor/orders")
def vendor_orders():

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Customer Orders</title>

        <style>

            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .order {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
            }

            .status {
                font-weight: bold;
                margin: 10px 0;
            }

            select {
                padding: 10px;
                margin-right: 5px;
            }

            button {
                padding: 10px 15px;
                background: black;
                color: white;
                border: none;
                border-radius: 6px;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 15px;
                background: black;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }

        </style>

    </head>

    <body>

        <h1>Customer Orders</h1>

        {% for order in orders %}

        <div class="order">

            <h2>Order {{ order.order_id }}</h2>

            <p><strong>Product:</strong> {{ order.product }}</p>

            <p><strong>Customer:</strong> {{ order.customer }}</p>

            <p><strong>Phone:</strong> {{ order.phone }}</p>

            <p><strong>Address:</strong> {{ order.address }}</p>

            <p><strong>Amount:</strong> {{ order.amount }}</p>

            <p class="status">
                Current Status: {{ order.status }}
            </p>

            <form
                method="POST"
                action="/vendor/orders/update/{{ order.order_id }}"
            >

                <select name="status">

                    <option value="Pending"
                        {% if order.status == "Pending" %}selected{% endif %}>
                        Pending
                    </option>

                    <option value="Confirmed"
                        {% if order.status == "Confirmed" %}selected{% endif %}>
                        Confirmed
                    </option>

                    <option value="Shipped"
                        {% if order.status == "Shipped" %}selected{% endif %}>
                        Shipped
                    </option>

                    <option value="Delivered"
                        {% if order.status == "Delivered" %}selected{% endif %}>
                        Delivered
                    </option>

                </select>

                <button type="submit">
                    Update Order
                </button>

            </form>

        </div>

        {% endfor %}

        <a href="/vendor/dashboard">
            Back to Dashboard
        </a>

    </body>

    </html>
    """, orders=sample_orders)


# ---------------- UPDATE ORDER STATUS ----------------

@app.route("/vendor/orders/update/<order_id>", methods=["POST"])
def update_order(order_id):

    new_status = request.form.get("status")

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Shipped",
        "Delivered"
    ]

    if new_status not in allowed_statuses:
        return "Invalid order status", 400

    for order in sample_orders:

        if order["order_id"] == order_id:

            order["status"] = new_status

            return redirect(url_for("vendor_orders"))

    return "Order not found", 404


# ---------------- START APP ----------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
)
