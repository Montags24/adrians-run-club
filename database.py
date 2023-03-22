from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api_requests import retrieve_data
from random import sample
from dotenv import load_dotenv
import smtplib
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://montags24:database123@montags24.eu.mysql.pythonanywhere-services.com/montags24$shoe_data"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shoes.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
load_dotenv()
GMAIL_EMAIL = os.getenv("GMAIL_RR_EMAIL")
MY_PASSWORD = os.getenv("GMAIL_RR_PASSWORD")


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    shoes = db.relationship("Shoe", backref="brand")

    def __repr__(self):
        return f'<Shoe {self.name}>'


class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    colour = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    img_link = db.Column(db.String(200), nullable=False)
    deal_link = db.Column(db.String(200), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    key = db.Column(db.String(200), unique=True, nullable=False)
    shoe_alerts = db.relationship("UserChoice", backref="user")

    def __repr__(self):
        return f'<Email {self.email}>'


class UserChoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shoe_name = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


def create_table():
    """Takes class instance as argument, creates table"""
    with app.app_context():
        db.create_all()


def db_add_row(entry):
    """Takes a class instance as argument, adds row entry"""
    with app.app_context():
        db.session.add(entry)
        db.session.commit()


def db_return_homepage_shoes():
    """Return 6 random shoes with data for home page"""
    with app.app_context():
        # shoe_data = query_database(table=Shoe, query="all", Shoe.discount < Shoe.price)
        shoe_data = db.session.query(Shoe).filter(Shoe.discount < Shoe.price).filter(Shoe.size == 10.0).all()
        shoe_list = sample(shoe_data, 6)
        shoe_names = [query_database(table=Brand, query="first", id=shoe.brand_id) for shoe in shoe_list]
        zipped_list = list(zip(shoe_names, shoe_list))
        return zipped_list


def query_database(table, query, **kwargs):
    if query == "all":
        with app.app_context():
            results = table.query.filter_by(**kwargs).all()
            return results
    else:
        with app.app_context():
            result = table.query.filter_by(**kwargs).first()
            return result


def db_check_for_deals():
    """Emails users if shoe is on sale"""
    with app.app_context():
        # loop through email in user table
        users = query_database(table=User, query="all")
        for user in users:
            deals = []
            email = user.email
            user_id = user.id
            # loop through shoes in user_choice with user_id = id
            shoes = query_database(table=UserChoice, query="all", user_id=user_id)
            for shoe in shoes:
                name = shoe.shoe_name
                size = shoe.size
                price = shoe.discount
                shoe_id = query_database(table=Brand, query="first", name=name).id
                db_shoe = query_database(table=Shoe, query="first", brand_id=shoe_id, size=size)
                if db_shoe.discount < price:
                    deals.append([name, size, db_shoe.discount, db_shoe.deal_link])
                    # Update user shoe price to reflect new price, so they do not get emailed every day
                    shoe_id = query_database(table=UserChoice, query="first", user_id=user_id, size=size,
                                             shoe_name=name).id
                    shoe_update = db.session.query(UserChoice).filter_by(id=shoe_id).first()
                    shoe_update.discount = db_shoe.discount
                    db.session.commit()
            if len(deals) > 0:
                key = query_database(table=User, query="first", email=email).key
                subject = "Adrian's Run Club - Deal Alert!"
                body = "The following shoes are on sale now!\n\n"
                for deal in deals:
                    body += f"{deal[0]} size {deal[1]} is on discount for {deal[2]} GBP. Get it now at {deal[3]}\n"
                body += f"\nUnsubscribe at the following link: www.adriansrunclub.co.uk/unsubscribe/{key}"
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(user=GMAIL_EMAIL, password=MY_PASSWORD)
                    connection.sendmail(
                        from_addr=GMAIL_EMAIL,
                        to_addrs=email,
                        msg=f"Subject: {subject}\n\n{body}"
                    )


def db_update_database():
    # Get data from api_requests module
    shoe_list = retrieve_data()
    with app.app_context():
        # Loop through data and store variable names
        for shoe in shoe_list:
            name = shoe["name"]
            colour = shoe["colour"]
            size = float(shoe["size"])
            price = shoe["price"]
            discount = shoe["discount"]
            score = shoe["score"]
            img_link = shoe["img_link"]
            deal_link = shoe["deal_link"]
            # Check if shoe model exists in brand table
            if query_database(table=Brand, query="first", name=name) is not None:
                # Check if shoe data exists in shoe table
                brand_id = query_database(table=Brand, query="first", name=name).id
                shoe = Shoe(size=size,
                            colour=colour,
                            price=price,
                            discount=discount,
                            score=score,
                            img_link=img_link,
                            deal_link=deal_link,
                            brand_id=brand_id)
                if query_database(table=Shoe, query="first", size=size, colour=colour, brand_id=brand_id) is not None:
                    # Get shoe id
                    shoe_id = query_database(table=Shoe, query="first", size=size, brand_id=brand_id).id
                    # Find shoe entry based off unique id to update
                    shoe_update = db.session.query(Shoe).filter_by(id=shoe_id).first()
                    # Update shoe entry based off unique id
                    shoe_update.size = size
                    shoe_update.colour = colour
                    shoe_update.price = price
                    shoe_update.discount = discount
                    shoe_update.score = score
                    shoe_update.img_link = img_link
                    shoe_update.deal_link = deal_link
                    db.session.commit()
                else:
                    # if shoe does not exist, add row
                    db_add_row(shoe)
            else:
                # If brand does not exist, add row
                brand = Brand(name=name)
                db_add_row(brand)
                brand_id = query_database(table=Brand, query="first", name=name).id
                shoe = Shoe(size=size,
                            colour=colour,
                            price=price,
                            discount=discount,
                            score=score,
                            img_link=img_link,
                            deal_link=deal_link,
                            brand_id=brand_id)
                db_add_row(shoe)
