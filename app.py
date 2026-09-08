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
        "address": "Lagos, Nigeria",
        "amount": "₦850,000",
        "status": "Pending"
    },
    {
        "order_id": "JINJA-1002",
        "product": "HP Core i5 Laptop",
        "customer": "David",
        "phone": "08123456789",
        "address": "Abuja, Nigeria",
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


# =========================
# VENDOR REGISTRATION
# =========================

@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        if not name or not email or not phone or not password:
            return "Please fill in all fields."

        vendors.append({
            "name": name,
            "email": email,
            "phone": phone
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
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .box {
                max-width: 450px;
                margin: 40px auto;
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

            button {
                width: 100%;
                padding: 13px;
                background: #111;
                color: white;
                border: none;
                border-radius: 6px;
            }
        </style>
    </head>

    <body>

        <div class="box">

            <h1>🏪 Jinja Vendor Registration</h1>

            <form method="POST">

                <label>Business/Vendor Name</label>
                <input type="text" name="name" required>

                <label>Email</label>
                <input type="email" name="email" required>

                <label>Phone Number</label>
                <input type="tel" name="phone" required>

                <label>Password</label>
                <input type="password" name="password" required>

                <button type="submit">
                    Register as Vendor
                </button>

            </form>

            <br>

            <a href="/">← Back to Jinja</a>

        </div>

    </body>
    </html>
    """)


# =========================
# VENDOR DASHBOARD
# =========================

@app.route("/vendor/dashboard")
def vendor_dashboard():

    name = request.args.get("name", "Vendor")
    email = request.args.get("email", "")
    phone = request.args.get("phone", "")

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Jinja Vendor Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            body {
                font-family: Arial;
                margin: 0;
                background: #f5f5f5;
            }

            header {
                background: #111;
                color: white;
                padding: 18px;
            }

            .container {
                max-width: 900px;
                margin: auto;
                padding: 20px;
            }

            .welcome {
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
            }

            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 15px;
            }

            .card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
            }

            button {
                padding: 12px 18px;
                background: #111;
                color: white;
                border: none;
                border-radius: 6px;
            }

            a {
                text-decoration: none;
                color: inherit;
            }

        </style>
    </head>

    <body>

        <header>
            <strong>Jinja Vendor Dashboard</strong>
        </header>

        <div class="container">

            <div class="welcome">

                <h1>Welcome, {{ name }}! 🎉</h1>

                <p><strong>Email:</strong> {{ email }}</p>

                <p><strong>Phone:</strong> {{ phone }}</p>

            </div>

            <div class="cards">

                <div class="card">
                    <h2>➕</h2>
                    <h3>Add Product</h3>
                    <p>Add a product to Jinja.</p>

                    <a href="/vendor/add-product">
                        <button>Add Product</button>
                    </a>
                </div>


                <div class="card">
                    <h2>🛍️</h2>
                    <h3>My Products</h3>
                    <p>View your products.</p>

                    <a href="/vendor/products">
                        <button>View Products</button>
                    </a>
                </div>


                <div class="card">
                    <h2>📦</h2>
                    <h3>Customer Orders</h3>
                    <p>Manage customer orders.</p>

                    <a href="/vendor/orders">
                        <button>Manage Orders</button>
                    </a>
                </div>

            </div>

            <br>

            <a href="/">← Back to Jinja Marketplace</a>

        </div>

    </body>
    </html>
    """)


# =========================
# ADD PRODUCT
# =========================

@app.route("/vendor/add-product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        description = request.form.get("description")
        image = request.form.get("image")

        if not name or not price or not category:
            return "Please fill in the required fields."

        products.append({
            "name": name,
            "price": price,
            "category": category,
            "description": description,
            "image": image
        })

        return redirect("/vendor/products")

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Add Product - Jinja</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .box {
                max-width: 500px;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }

            input, textarea, select {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                box-sizing: border-box;
                border: 1px solid #ccc;
                border-radius: 6px;
            }

            textarea {
                height: 100px;
            }

            button {
                width: 100%;
                padding: 13px;
                background: #111;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h1>➕ Add Product</h1>

            <form method="POST">

                <label>Product Name *</label>
                <input type="text" name="name" required>

                <label>Price (₦) *</label>
                <input type="number" name="price" required>

                <label>Category *</label>

                <select name="category" required>

                    <option value="">Select category</option>
                    <option value="Phones">Phones</option>
                    <option value="Laptops">Laptops</option>
                    <option value="Accessories">Accessories</option>

                </select>

                <label>Description</label>

                <textarea name="description"></textarea>

                <label>Product Image URL</label>

                <input type="url" name="image">

                <button type="submit">
                    💾 Save Product
                </button>

            </form>

            <br>

            <a href="/vendor/dashboard">
                ← Back to Dashboard
            </a>

        </div>

    </body>

    </html>
    """)


# =========================
# MY PRODUCTS
# =========================

@app.route("/vendor/products")
def vendor_products():

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>

        <title>My Products - Jinja</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 20px;
            }

            .container {
                max-width: 900px;
                margin: auto;
            }

            .product {
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 12px;
            }

            img {
                width: 150px;
                height: 150px;
                object-fit: cover;
                border-radius: 8px;
            }

            .price {
                font-size: 20px;
                font-weight: bold;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>🛍️ My Products</h1>

            {% if products %}

                {% for product in products %}

                    <div class="product">

                        {% if product.image %}
                            <img src="{{ product.image }}">
                        {% endif %}

                        <h2>{{ product.name }}</h2>

                        <div class="price">
                            ₦{{ product.price }}
                        </div>

                        <p>
                            <strong>{{ product.category }}</strong>
                        </p>

                        <p>{{ product.description }}</p>

                    </div>

                {% endfor %}

            {% else %}

                <p>You haven't added any products yet.</p>

            {% endif %}

            <br>

            <a href="/vendor/add-product">
                ➕ Add Another Product
            </a>

            <br><br>

            <a href="/vendor/dashboard">
                ← Back to Dashboard
            </a>

        </div>

    </body>

    </html>
    """, products=products)


# =========================
# CUSTOMER ORDERS
# =========================

@app.route("/vendor/orders")
def vendor_orders():

    return render_template_string("""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Customer Orders - Jinja</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            body {
                font-family: Arial;
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
                margin-bottom: 15px;
                border-radius: 12px;
            }

            .status {
                font-weight: bold;
            }

            button {
                padding: 10px 15px;
                background: #111;
                color: white;
                border: none;
                border-radius: 6px;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>📦 Customer Orders</h1>

            {% for order in orders %}

            <div class="order">

                <h2>{{ order.order_id }}</h2>

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
                    <strong>Delivery Address:</strong>
                    {{ order.address }}
                </p>

                <p>
                    <strong>Amount:</strong>
                    {{ order.amount }}
                </p>

                <p class="status">
                    Status: {{ order.status }}
                </p>

                <button>
                    Update Order
                </button>

            </div>

            {% endfor %}

            <br>

            <a href="/vendor/dashboard">
                ← Back to Dashboard
            </a>

        </div>

    </body>

    </html>
    """, orders=sample_orders)


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
