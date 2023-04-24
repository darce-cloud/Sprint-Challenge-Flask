"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq
import random

APP = Flask(__name__)


# PART 2

def get_results(city, parameter):
    api = openaq.OpenAQ()
    status, body = api.measurements(city=city, parameter=parameter)
    utc_value_list = []
    for result in body['results']:
        value = result['value']
        utc_datetime = result['date']['utc']
        utc_value_list.append((utc_datetime, value))
    return utc_value_list


@APP.route('/')
def root():
    utc_value_list = get_results('Los Angeles', 'pm25')
    risky_pm = Record.query.filter(Record.value >= 18).all() # PART 4
    return str(risky_pm)


# PART 3

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '< Time %s --- Value %s>' % (self.datetime, self.value)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    results = get_results()
    for result in results:
        record = Record(datetime=str(result[0]), value=result[1])
        DB.session.add(record)
    DB.session.commit()
    records = Record.query.all()
    return str(records)