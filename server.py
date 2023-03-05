from flask import Flask, render_template, request
from dotenv import load_dotenv
import smtplib
import os

app = Flask(__name__)
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


shoes = []


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    global shoes
    if request.method == "POST":
        if "form-submit" in request.form:
            shoe = request.form["shoe"]
            size = request.form["size"]
            shoes.append([shoe, size])
        elif "delete-btn" in request.form:
            number = int(request.form["delete-btn"])
            print(number)
            if len(shoes) > 0:
                del shoes[number - 1]
        return render_template("sign-up.html", shoes=shoes)
    else:
        return render_template("sign-up.html")


if __name__ == "__main__":
    app.run(debug=True)
