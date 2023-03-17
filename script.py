from database import db_update_database, db_check_for_deals, db, User, UserChoice, Shoe, Brand, app
from sqlalchemy import delete


def daily_update():
    db_update_database()
    db_check_for_deals()


daily_update()

