from flask import render_template, request, session, jsonify
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import SelectField
from dotenv import load_dotenv
from database import Brand, Shoe, User, UserChoice, db_return_homepage_shoes, db_add_row, query_database, db, app
# app as app
from key_generator.key_generator import generate
from sqlalchemy import delete, asc
import smtplib
import os

# app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
load_dotenv()
GMAIL_EMAIL = os.getenv("GMAIL_RR_EMAIL")
MY_PASSWORD = os.getenv("GMAIL_RR_PASSWORD")
EMAIL = os.getenv("EMAIL")


class Form(FlaskForm):
    size = SelectField("size", choices=[(x / 2, x / 2) for x in range(6 * 2, 13 * 2)],
                       render_kw={'class': 'form-select'})
    brand = SelectField("brand", choices=[], render_kw={'class': 'form-select'})
    colour = SelectField("colour", choices=[], render_kw={'class': 'form-select'})


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
    """Sign up page for user to choose shoes and get alerts via email"""
    with app.app_context():
        form = Form()
        form.brand.choices = [(brand_form.id, brand_form.name) for brand_form in Brand.query.distinct(Brand.name).where(
            Shoe.size == 6.0).where(Brand.id == Shoe.brand_id).order_by(asc(Brand.name))]
        first_brand_id = Brand.query.order_by(Brand.name.asc()).first().id

        form.colour.choices = [(shoe.id, shoe.colour) for shoe in Shoe.query.distinct(Shoe.colour).where(
            Shoe.size == 6.0).where(Shoe.brand_id == first_brand_id).order_by(asc(Shoe.colour))]
        if request.method == "POST":
            # Check if user is adding shoe to cart
            if "form-submit" in request.form:
                brand_id = request.form["brand"]
                size = request.form["size"]
                shoe_id = request.form["colour"]
                # Create flask session
                if "cart" not in session:
                    session["cart"] = []
                cart_list = session["cart"]
                shoe_data = query_database(table=Shoe, query="first", id=shoe_id)
                cart_list.append({
                    "name": Brand.query.filter_by(id=brand_id).first().name,
                    "size": size,
                    "colour": shoe_data.colour,
                    "score": shoe_data.score,
                    "discount": shoe_data.discount,
                    "img_link": shoe_data.img_link,
                    "deal_link": shoe_data.deal_link,
                    "id": shoe_data.id
                })
                form.colour.choices = [(shoe.id, shoe.colour) for shoe in Shoe.query.distinct(Shoe.colour).where(
                    Shoe.size == size).where(Shoe.brand_id == brand_id).order_by(asc(Shoe.colour))]
                return render_template("sign-up.html", shoes=session["cart"], form=form)
            elif "delete-btn" in request.form:
                number = int(request.form["delete-btn"])
                if len(session["cart"]) > 0:
                    del session["cart"][number - 1]
                return render_template("sign-up.html", shoes=session["cart"], form=form)
        return render_template("sign-up.html", form=form)


@app.route("/brand/<size>")
def brand(size):
    with app.app_context():
        brands = Brand.query.where(Shoe.size == size).where(Brand.id == Shoe.brand_id).order_by(
            asc(Brand.name)).distinct()

        brand_array = []

        for brand in brands:
            brand_obj = {"id": brand.id, "name": brand.name}
            brand_array.append(brand_obj)

        return jsonify({"brands": brand_array})


@app.route("/colour/<brand>/<size>")
def colour(brand, size):
    with app.app_context():
        colours = Shoe.query.filter_by(size=size, brand_id=brand).group_by(Shoe.colour).order_by(
            asc(Shoe.colour)).distinct()

        colour_array = []

        for colour in colours:
            colour_obj = {"id": colour.id, "colour": colour.colour}
            colour_array.append(colour_obj)

        return jsonify({"colours": colour_array})


@app.route("/signup/success", methods=["GET", "POST"])
def sign_up_success():
    """Add user email and shoe choices to database"""
    if request.method == "POST":
        email = request.form["email"]
        print(email)
        # Generate random token to allow user to unsubscribe
        key = generate(5, '-', 3, 3, type_of_value='hex', capital='none').get_key()
        # Generate data from user cart to put into database
        user_shoes = [{"name": shoe["name"],
                       "size": shoe["size"],
                       "colour": shoe["colour"],
                       "discount": shoe["discount"],
                       "shoe_id": shoe["id"]} for shoe in session["cart"]]
        user = User(email=email, key=key)
        # Check if user exists
        exists = query_database(table=User, query="first", email=email) is not None
        if not exists:
            db_add_row(user)
            # Email user welcoming them to Adrian's Run Club
            subject = "Welcome to Adrian's Run Club!"
            body = "You have successfully signed up to Adrian's run club with the following shoes:\n\n"
            for shoe in user_shoes:
                body += f"{shoe['name']} in size {shoe['size']} with colourway {shoe['colour']}\n"
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
            user_choice = UserChoice(discount=shoe['discount'],
                                     user_id=user_id,
                                     shoe_id=shoe['shoe_id'])
            db_add_row(user_choice)
        return render_template("sign-up-success.html")
    else:
        return render_template("sign-up-success.html")


@app.route("/unsubscribe/<token>", methods=["GET", "POST"])
def unsubscribe(token):
    if request.method == "GET":
        with app.app_context():
            user_id = db.session.query(User).filter_by(key=token).first().id
            stmt = (
                delete(UserChoice).where(UserChoice.user_id == user_id)
            )
            stmt2 = (
                delete(User).where(User.key == token)
            )
            db.session.execute(stmt)
            db.session.execute(stmt2)
            db.session.commit()
    return render_template("unsubscribe.html")


if __name__ == "__main__":
    app.run(debug=True)
