from flask import Flask, render_template, request, session
from flask_session import Session
from dotenv import load_dotenv
from database import Brand, Shoe, User, UserChoice, db_return_homepage_shoes, db_add_row, query_database
from api_requests import sizes
import smtplib
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
load_dotenv()
GMAIL_EMAIL = os.getenv("GMAIL_RR_EMAIL")
MY_PASSWORD = os.getenv("GMAIL_RR_PASSWORD")
EMAIL = os.getenv("EMAIL")


@app.route("/", methods=["GET", "POST"])
def home():
    """Homepage for Adrian's Run Club"""
    if request.method == "GET":
        return render_template("home.html", shoes=db_return_homepage_shoes())
    else:
        # Send email if user fills out and sends contact form
        name = request.form["name"]
        phone_number = request.form["phone-number"]
        email = request.form["email"]
        message = request.form["message"]
        subject = f"Adrian's Run Club - You have a new message from {name}!"
        body = f"Name: {name}\nPhone number: {phone_number}\nEmail: {email}\nMessage: {message}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=GMAIL_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
                from_addr=GMAIL_EMAIL,
                to_addrs=EMAIL,
                msg=f"Subject: {subject}\n\n{body}"
            )
        return render_template("message-success.html")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Sign up page for user to chose shoes and get alerts vid email"""
    # Get all shoe brand names in alphabetical order
    shoe_brand_data = query_database(table=Brand, query="all")
    all_shoes = sorted([shoe.name for shoe in shoe_brand_data])
    if request.method == "POST":
        # Check if user is adding shoe to cart or if deleting a shoe
        if "form-submit" in request.form:
            brand = request.form["shoe"]
            size = float(request.form["size"])
            # Create flask session
            if "cart" not in session:
                session["cart"] = []
            cart_list = session["cart"]
            brand_id = query_database(table=Brand, query="first", name=brand).id
            shoe_data = query_database(table=Shoe, query="first", brand_id=brand_id, size=size)
            # Check if shoe is in database, otherwise throw up error message
            exist = query_database(table=Shoe, query="first", size=size, brand_id=brand_id) is not None
            if shoe_data is not None:
                cart_list.append({
                    "name": brand,
                    "size": size,
                    "score": shoe_data.score,
                    "discount": shoe_data.discount,
                    "img_link": shoe_data.img_link,
                    "deal_link": shoe_data.deal_link,
                })
            return render_template("sign-up.html", shoes=session["cart"], all_shoes=all_shoes, sizes=sizes,
                                   exist=exist)
        elif "delete-btn" in request.form:
            number = int(request.form["delete-btn"])
            if len(session["cart"]) > 0:
                del session["cart"][number - 1]
        return render_template("sign-up.html", shoes=session["cart"], all_shoes=all_shoes, sizes=sizes, exist=True)
    else:
        return render_template("sign-up.html", all_shoes=all_shoes, sizes=sizes, exist=True)


@app.route("/signup/success", methods=["GET", "POST"])
def sign_up_success():
    """Add user email and shoe choices to database"""
    if request.method == "POST":
        email = request.form["email"]
        user_shoes = [[shoe["name"], shoe["size"], shoe["discount"]] for shoe in session["cart"]]
        user = User(email=email)
        # Check if user exists
        exists = query_database(table=User, query="first", email=email) is not None
        if not exists:
            db_add_row(user)
            # Email user welcoming them to Adrian's Run Club
            subject = "Welcome to Adrian's Run Club!"
            body = "You have successfully signed up to Adrian's run club with the following shoes:\n\n"
            for shoe in user_shoes:
                body += f"{shoe[0]} in size {shoe[1]}\n"
            body += "\nPlease don't forget to mark this address as safe to receive future emails!"
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=GMAIL_EMAIL, password=MY_PASSWORD)
                connection.sendmail(
                    from_addr=GMAIL_EMAIL,
                    to_addrs=email,
                    msg=f"Subject: {subject}\n\n{body.encode('ascii', 'ignore').decode('ascii')}"
                )
        user_id = query_database(table=User, query="first", email=email).id
        for shoe in user_shoes:
            user_choice = UserChoice(shoe_name=shoe[0], size=shoe[1], discount=shoe[2], user_id=user_id)
            db_add_row(user_choice)
        return render_template("sign-up-success.html")
    else:
        return render_template("sign-up-success.html")


if __name__ == "__main__":
    app.run(debug=True)
