from flask import Flask, render_template, request, session
from flask_session import Session
from dotenv import load_dotenv
from database import get_brand_id, get_shoe_data, return_shoes
from api_requests import sizes
import smtplib
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
load_dotenv()
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
MY_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAIL = os.getenv("EMAIL")


def send_email(name, number, email, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=GMAIL_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=GMAIL_EMAIL,
            to_addrs=EMAIL,
            msg=f"\n\nName: {name}\nPhone number: {number}\nEmail: {email}\nMessage: {message}"
        )


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html")
    else:
        name = request.form["name"]
        phone_number = request.form["phone-number"]
        email = request.form["email"]
        message = request.form["message"]
        print(f"Name: {name}\nPhone number: {phone_number}\nEmail: {email}\nMessage: {message}")
        send_email(name, phone_number, email, message)
        return render_template("message-success.html")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # Get all shoe brand names in alphabetical order
        all_shoes = return_shoes()
        if "form-submit" in request.form:
            brand = request.form["shoe"]
            size = float(request.form["size"])
            # Create session
            if "cart" not in session:
                session["cart"] = []
            cart_list = session["cart"]
            brand_id = get_brand_id(brand_name=brand)
            shoe_data = get_shoe_data(brand_id=brand_id, shoe_size=size)
            if shoe_data is not None:
                cart_list.append({
                    "name": brand,
                    "size": size,
                    "score": shoe_data.score,
                    "discount": shoe_data.discount,
                    "img_link": shoe_data.img_link,
                    "deal_link": shoe_data.deal_link,
                })
        elif "delete-btn" in request.form:
            number = int(request.form["delete-btn"])
            if len(session["cart"]) > 0:
                del session["cart"][number - 1]
        return render_template("sign-up.html", shoes=session["cart"], all_shoes=all_shoes, sizes=sizes)
    else:
        all_shoes = return_shoes()
        return render_template("sign-up.html", all_shoes=all_shoes, sizes=sizes)


if __name__ == "__main__":
    app.run(debug=True)
