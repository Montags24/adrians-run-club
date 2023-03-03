from flask import Flask, render_template, request
import smtplib
import requests


app = Flask(__name__)
MY_EMAIL = "adrianmontagu24@gmail.com"
MY_PASSWORD = "lppcaedlozkfaebz"


def send_email(name, number, email, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs="adrianmontagu@hotmail.co.uk",
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


@app.route("/signup")
def sign_up():
    return ""


if __name__ == "__main__":
    app.run(debug=True)