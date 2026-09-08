from flask import Flask, send_from_directory, request, render_template_string
import os

app = Flask(__name__)

# Temporary storage for testing
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
            vendors.append({
                "name": name,
                "email": email,
                "phone": phone,
                "password": password
            })

            message = "Vendor registration successful! 🎉"

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

            .message {
                text-align: center;
                margin-bottom: 15px;
                color: green;
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
                <div class="message">{{ message }}</div>
            {% endif %}

            <form method="POST">
                <label>Business/Vendor Name</label>
                <input type="text" name="name" required>

                <label>Email</label>
                <input type="email" name="email" required>

                <label>Phone Number</label>
                <input type="tel" name="phone" required>

                <label>Password</label>
                <input type="password" name="password" required>

                <button type="submit">Register as Vendor</button>
            </form>

            <a href="/">← Back to Jinja Marketplace</a>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
