from flask import Flask, send_from_directory, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# Temporary vendor storage for testing
vendors = []


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")


@app.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():
    message = ""

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        if not name or not email or not phone or not password:
            message = "Please fill in all fields."
        else:
            vendor = {
                "name": name,
                "email": email,
                "phone": phone
            }

            vendors.append(vendor)

            # Send the vendor to the dashboard
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
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }

            .container {
                max-width: 450px;
                margin: 40px auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                text-align: center;
            }

            input {
                width: 100%;
                padding: 12px;
                margin: 8px 0 15px;
                box-sizing: border-box;
                border: 1px solid #ccc;
                border-radius: 6px;
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

            .error {
                color: red;
                text-align: center;
            }

            a {
                display: block;
                text-align: center;
                margin-top: 20px;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>🏪 Jinja Vendor Registration</h1>

            {% if message %}
                <div class="error">{{ message }}</div>
            {% endif %}

            <form method="POST">

                <label>Business/Vendor Name</label>
                <input
                    type="text"
                    name="name"
                    placeholder="Enter business name"
                    required
                >

                <label>Email</label>
                <input
                    type="email"
                    name="email"
                    placeholder="Enter email"
                    required
                >

                <label>Phone Number</label>
                <input
                    type="tel"
                    name="phone"
                    placeholder="Enter phone number"
                    required
                >

                <label>Password</label>
                <input
                    type="password"
                    name="password"
                    placeholder="Create password"
                    required
                >

                <button type="submit">
                    Register as Vendor
                </button>

            </form>

            <a href="/">← Back to Jinja Marketplace</a>

        </div>
    </body>
    </html>
    """)


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
                font-family: Arial, sans-serif;
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
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .card h2 {
                margin-top: 0;
            }

            button {
                padding: 12px 18px;
                border: none;
                border-radius: 6px;
                background: #111;
                color: white;
                font-size: 15px;
            }

            a {
                color: white;
                text-decoration: none;
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

                <p>Your vendor account has been created successfully.</p>

            </div>

            <div class="cards">

                <div class="card">
                    <h2>➕</h2>
                    <h3>Add Product</h3>
                    <p>Add your products to Jinja.</p>
                    <button>Add Product</button>
                </div>

                <div class="card">
                    <h2>📦</h2>
                    <h3>Orders</h3>
                    <p>Manage your customer orders.</p>
                    <button>Manage Orders</button>
                </div>

                <div class="card">
                    <h2>🛍️</h2>
                    <h3>My Products</h3>
                    <p>View your products.</p>
                    <button>View Products</button>
                </div>

            </div>

            <br>

            <a href="/" style="color:#111;">← Back to Jinja Marketplace</a>

        </div>

    </body>
    </html>
    """)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
)
