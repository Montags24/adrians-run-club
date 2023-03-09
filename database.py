from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api_requests import retrieve_data
from random import choice

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


def create_table():
    """Takes class instance as argument, creates table"""
    with app.app_context():
        db.create_all()


def add_row(entry):
    """Takes a class instance as argument, adds row entry"""
    with app.app_context():
        db.session.add(entry)
        db.session.commit()


def get_brand_id(brand_name):
    """Returns the id linked to Brand id"""
    with app.app_context():
        brand = Brand.query.filter_by(name=brand_name).first()
        return brand.id


def get_shoe_id(size, brand_id):
    with app.app_context():
        shoe = Shoe.query.filter(
            Shoe.brand_id.like(brand_id),
            Shoe.size.like(size)
        ).first()
        return shoe.id


def get_shoe_data(brand_id, shoe_size):
    with app.app_context():
        shoe = Shoe.query.filter(
            Shoe.brand_id.like(brand_id),
            Shoe.size.like(shoe_size)
        ).first()
        return shoe


def does_model_exist(shoe_model):
    """Checks if parent class exists"""
    with app.app_context():
        exist = Brand.query.filter_by(name=shoe_model).first() is not None
        return exist


def return_shoe_names():
    with app.app_context():
        shoe_brand_data = Brand.query.all()
        all_shoes = sorted([shoe.name for shoe in shoe_brand_data])
        return all_shoes


def return_shoes():
    """Return 6 random shoes with data for home page"""
    with app.app_context():
        shoe_data = Shoe.query.filter_by(size=10.0).all()
        shoe_list = [choice(shoe_data) for _ in range(6)]
        shoe_names = [Brand.query.filter(Brand.id.like(shoe.brand_id)).first() for shoe in shoe_list]
        zipped_list = list(zip(shoe_names, shoe_list))
        return zipped_list


def does_shoe_exist(size, brand_id):
    """Checks if child class exists"""
    with app.app_context():
        exist = Shoe.query.filter(
            Shoe.brand_id.like(brand_id),
            Shoe.size.like(size)
        ).first() is not None
        return exist


def update_database():
    # Get data from api_requests module
    shoe_list = retrieve_data()
    with app.app_context():
        # Loop through data and store variable names
        for shoe in shoe_list:
            name = shoe[0]
            size = float(shoe[1])
            price = shoe[2]["price"]
            discount = shoe[2]["discount"]
            score = shoe[2]["score"]
            img_link = shoe[2]["img_link"]
            deal_link = shoe[2]["deal_link"]
            # Check if shoe model exists in brand table
            if does_model_exist(name):
                # Check if shoe data exists in shoe table
                brand_id = get_brand_id(name)
                shoe = Shoe(size=size, price=price, discount=discount, score=score, img_link=img_link,
                            deal_link=deal_link, brand_id=brand_id)
                if does_shoe_exist(size, brand_id):
                    # Get shoe id
                    shoe_id = get_shoe_id(size=size, brand_id=brand_id)
                    # Find shoe entry based off unique id
                    shoe_update = Shoe.query.filter(Shoe.id.like(shoe_id)).first()
                    # shoe_update = Shoe.query.filter(Shoe.id.like(shoe_id).first())
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
                    add_row(shoe)
            else:
                # If brand does not exist, add row
                brand = Brand(name=name)
                add_row(brand)
                brand_id = get_brand_id(name)
                shoe = Shoe(size=size, price=price, discount=discount, score=score, img_link=img_link,
                            deal_link=deal_link,
                            brand_id=brand_id)
                add_row(shoe)


# create_table()
# update_database()
# return_shoes()