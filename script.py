from database import db_update_database, db_check_for_deals


def daily_update():
    db_update_database()
    db_check_for_deals()


daily_update()

