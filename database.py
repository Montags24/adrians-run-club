from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api_requests import retrieve_data
from random import sample

app = Flask(__name__)

# Create database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shoes.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    shoes = db.relationship("Shoe", backref="brand")

    def __repr__(self):
        return f'<Shoe {self.name}>'


class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
        shoe_data = query_database(table=Shoe, query="all", size=10.0)
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


def check_for_deal():
    """Returns True if price of specific shoe and size is more than what's recorded in database"""
    with app.app_context():
        # all_user_shoes = UserChoice.query.all()
        all_user_shoes = query_database(table=UserChoice, query="all")
        for shoe in all_user_shoes:
            name = shoe.shoe_name
            size = shoe.size
            price = shoe.discount
            brand_id = query_database(table=Brand, query="first", name=name).id
            db_shoe = query_database(table=Shoe, query="first", size=size, brand_id=brand_id)
            print(price, db_shoe.discount)
            if db_shoe.discount < price:
                print("It is on sale!")
                print(f"{name} is on discount for {db_shoe.discount} at {db_shoe.deal_link}")


def db_update_database():
    # Get data from api_requests module
    shoe_list = retrieve_data()
    with app.app_context():
        # Loop through data and store variable names
        for shoe in shoe_list:
            name = shoe["name"]
            size = float(shoe["size"])
            price = shoe["price"]
            discount = shoe["discount"]
            score = shoe["score"]
            img_link = shoe["img_link"]
            deal_link = shoe["deal_link"]
            # Check if shoe model exists in brand table
            # if db_does_model_exist(name):
            if query_database(table=Brand, query="first", name=name) is not None:
                # Check if shoe data exists in shoe table
                # brand_id = db_get_brand_id(name)
                brand_id = query_database(table=Brand, query="first", name=name).id
                shoe = Shoe(size=size,
                            price=price,
                            discount=discount,
                            score=score,
                            img_link=img_link,
                            deal_link=deal_link,
                            brand_id=brand_id)
                # if db_does_shoe_exist(size, brand_id):
                if query_database(table=Shoe, query="first", size=size, brand_id=brand_id) is not None:
                    # Get shoe id
                    # shoe_id = db_get_shoe_id(size=size, brand_id=brand_id)
                    shoe_id = query_database(table=Shoe, query="first", size=size, brand_id=brand_id).id
                    # Find shoe entry based off unique id
                    # shoe_update = Shoe.query.filter(Shoe.id.like(shoe_id)).first()
                    shoe_update = query_database(table=Shoe, query="first", id=shoe_id)
                    # Update shoe entry based off unique id
                    shoe_update.size = size
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
                # brand_id = db_get_brand_id(name)
                brand_id = query_database(table=Brand, query="first", name=name).id
                shoe = Shoe(size=size,
                            price=price,
                            discount=discount,
                            score=score,
                            img_link=img_link,
                            deal_link=deal_link,
                            brand_id=brand_id)
                db_add_row(shoe)


# create_table()
# db_update_database()
# db_return_shoes()
