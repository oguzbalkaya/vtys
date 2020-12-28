from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/kargo'
db = SQLAlchemy(app)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    district = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    manager = db.Column(db.Integer, nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    adress = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    isdriver = db.Column(db.Integer,nullable=False)

class Packages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivered_to = db.Column(db.String(200), nullable=False)
    delivered_date = db.Column(db.String(200), nullable=False)
    employee = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum("Accepted","On The Way","On The Destination","Distribution","Delivered"),nullable=False)
    takenbranch = db.Column(db.Integer, nullable=False)
    takendate = db.Column(db.TIMESTAMP, nullable=False)
    deliveredbranch = db.Column(db.Integer, nullable=False)
    customername = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)

class Transportdetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    explanation = db.Column(db.String(5000), nullable=False)
    status = db.Column(db.String(200), nullable=False)
    date = db.Column(db.TIMESTAMP, nullable=False)
    package = db.Column(db.Integer, nullable=False)