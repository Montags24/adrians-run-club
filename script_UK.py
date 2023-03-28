from database import db_update_database, db_check_for_deals


def daily_update():
    db_update_database("GB")
    db_check_for_deals()


if __name__ == "__main__":
    daily_update()

