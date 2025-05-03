from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


# TABLE TO STORE USERS AND THEIR ASSOCIATED INFORMATION
class Salesperson(UserMixin, db.Model):
    __tablename__ = 'salespeople'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Singapore")), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    quotes = db.relationship('Quote', back_populates='salesperson')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




# TABLE TO STORE QUOTES (ONE TO MANY RELATIONSHIP)
class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('salespeople.id'), nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    customer_contact = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    retail_price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, default=0, nullable=False)
    addons = db.Column(db.Integer, default=0, nullable=False)    
    net_price = db.Column(db.Integer, nullable=False)
    package = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Singapore")), nullable=False)

    salesperson = db.relationship('Salesperson', back_populates='quotes')
    trade_ins = db.relationship('TradeIn', uselist=False, back_populates='quote', cascade='all, delete')
    finance = db.relationship('Finance', uselist=False, back_populates='quote', cascade='all, delete')




# TABLE TO STORE TRADE-IN VEHICLE DETAILS (ONE TO ONE RELATIONSHIP)
class TradeIn(db.Model):
    __tablename__ = 'trade_ins'
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(8), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    trade_in_value = db.Column(db.Integer, nullable=False)
    outstanding_loan = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)

    quote = db.relationship('Quote', back_populates='trade_ins', uselist=False)





# TABLE TO STORE FINANCE DETAILS (ONE TO ONE RELATIONSHIP)
class Finance(db.Model):
    __tablename__ = 'finance'
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    bank = db.Column(db.String(100), nullable=False)
    loan_amount = db.Column(db.Integer, nullable=False)
    tenure_months = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    monthly_installment = db.Column(db.Integer, nullable=False)

    quote = db.relationship('Quote', back_populates='finance')