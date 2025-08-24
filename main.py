from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, send_file, render_template, redirect, url_for, flash, session, abort, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, Salesperson, Quote, TradeIn, Finance
from pdf_utils import generate_quote_pdf
import io

# ADMIN IMPORTS
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

# INITIALIZE FLASK AND SET ITS CONFIGURATIONS
app = Flask(__name__)
app.config.from_object(Config)


# INITIALIZE DATABASE
db.init_app(app)
with app.app_context():
    db.create_all()


# INITIALIZING FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Salesperson, int(user_id))




# AUTHENTICATION CHECKS FOR ADMIN
class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminIndex(AdminIndexView):
    def is_accessible(self):
        return (
            current_user.is_authenticated
            and getattr(current_user, 'is_admin', False)
        )

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

admin = Admin(app, name="Sales Admin", template_mode="bootstrap3", index_view=MyAdminIndex())

class QuoteAdmin(AuthenticatedModelView):
    # show salesperson as a dropdown, and inline-edit child objects
    form_ajax_refs = {
        'salesperson': {
            'fields': ['name', 'phone_number']
        }
    }
    inline_models = (TradeIn, Finance)

    # Enable searching on these columns
    column_searchable_list = [
        'customer_name',
        'customer_contact',
        'model',
        'salesperson.name',
        'salesperson.phone_number'
    ]

    # pull trade-in fields off the trade_ins attribute
    column_formatters = {
        'trade_in_value': 
            lambda view, context, model, name: (
                model.trade_ins.trade_in_value if model.trade_ins else None
            ),
        'balance': 
            lambda view, context, model, name: (
                model.trade_ins.balance if model.trade_ins else None
            ),
    }

    column_list = (
        'id',
        'salesperson.name',
        'customer_name',
        'model',
        'net_price',
        'discount',
        'addons',
        'trade_in_value',
        'balance',
        'finance.bank',
        'finance.loan_amount',
        'finance.tenure_months',
        'finance.interest_rate',
        'finance.monthly_installment',
        'date_created',
    )

    column_labels = {
        'salesperson.name':      'Salesperson',
        'trade_in_value':        'Trade-in Value',
        'balance':               'Trade-in Balance',
        'finance.bank':          'Bank',
        'finance.loan_amount':   'Loan Amount',
        'finance.tenure_months': 'Tenure (months)',
        'finance.interest_rate': 'Interest Rate (%)',
        'finance.monthly_installment': 'Monthly Installment',
        'date_created':          'Date Created',
    }

# register your models with the admin
admin.add_view(AuthenticatedModelView(Salesperson, db.session, name="Salespeople"))
admin.add_view(QuoteAdmin(Quote,       db.session, name="Quotes"))
admin.add_view(AuthenticatedModelView(TradeIn,     db.session, name="Trade-Ins"))
admin.add_view(AuthenticatedModelView(Finance,     db.session, name="Financing"))





# REGISTER AUTHENTICATION ROUTE
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone_number = request.form.get('phone_number')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not name or not phone_number or not password or not confirm_password:
                return redirect(url_for('register'))
            
            if password != confirm_password:
                return redirect(url_for('register'))
                
            sp = Salesperson(name=name, phone_number=phone_number)
            sp.set_password(password)
            db.session.add(sp)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            db.session.rollback()
            return redirect(url_for('register'))
            
    return render_template('register.html')


# LOGIN AUTHENTICATION ROUTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        
        if not phone_number or not password:
            flash('Please provide both phone number and password')
            return redirect(url_for('login'))
            
        sp = Salesperson.query.filter_by(phone_number=phone_number).first()
        if sp and sp.check_password(password):
            login_user(sp)
            return redirect(url_for('form'))
        flash('Invalid credentials')
        return redirect(url_for('login'))
    return render_template('login.html')


# LOGOUT AUTHENTICATION ROUTE
@app.route('/logout')
@login_required
def logout():
    session.clear()  # clear session data
    return redirect(url_for('login'))





# INDEX PAGE
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')





# FORM TO COLLECT NECESSARY DATA TO CREATE SALES DRAFT. ACCESSING DATABSE WITH SQLALCHEMY INSTEAD OF TRADITIONAL SQLITE
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        try:
            form = request.form
            
            # check if required fields exist
            required_fields = ['customer_name', 'customer_contact', 'model', 'retail_price', 'discount']
            for field in required_fields:
                if field not in form:
                    flash(f"Missing required field: {field}", "error")
                    return redirect(url_for('form'))

            # 1) REQUIRED QUOTE FIELDS (with safe defaults)
            customer_name = form.get('customer_name', '')
            customer_contact = form.get('customer_contact', '')
            model_name = form.get('model', '')
            retail_price = int(form.get('retail_price', 0))
            # safe conversion for optional fields
            discount = int(form.get('discount')) if form.get('discount') else 0
            addons = int(form.get('addons')) if form.get('addons') else 0
            net_price = retail_price - discount + addons
            # special case for packages -> grab all checked packages
            packages = form.getlist('packages')
            
            # handle custom packages
            custom_packages = form.getlist('custom_packages[]')
            # filter out empty custom packages
            custom_packages = [pkg.strip() for pkg in custom_packages if pkg.strip()]
            
            # combine regular packages and custom packages
            all_packages = packages + custom_packages
            package_str = "||".join(all_packages)  # Use || as delimiter instead of comma

            # 2) CREATE THE QUOTE
            quote = Quote(
                salesperson_id = current_user.id,
                customer_name = customer_name,
                customer_contact = customer_contact,
                model = model_name,
                retail_price = retail_price,
                discount = discount,
                addons = addons, 
                net_price = net_price,
                package = package_str
            )
            db.session.add(quote)
            db.session.flush()

            # 3) OPTIONAL TRADE-IN
            if form.get('tradein-checkbox'):
                trade_in_value = int(form.get('tradein_price', 0))
                outstanding_loan = int(form.get('tradein_outstanding', 0))
                balance = trade_in_value - outstanding_loan
                ti = TradeIn(
                    plate = form.get('tradein_plate', ''),
                    trade_in_value = trade_in_value,
                    outstanding_loan = outstanding_loan,
                    balance = balance,
                    quote_id = quote.id
                )
                db.session.add(ti)

            # 4) OPTIONAL FINANCE
            if form.get('finance-checkbox'):
                bank = form.get('finance_bank', '')
                loan_amount = int(form.get('finance_loan', 0))
                tenure_months = int(form.get('finance_tenure', 0))
                interest_rate = float(form.get('finance_rate', 0))
                monthly_installment = loan_amount * (1 + (interest_rate/100) * (tenure_months/12)) / tenure_months
                fin = Finance(
                    bank = bank,
                    loan_amount = loan_amount,
                    tenure_months = tenure_months,
                    interest_rate = interest_rate,
                    monthly_installment = monthly_installment,
                    quote_id = quote.id
                )
                db.session.add(fin)

            # 5) COMMIT ALL AT ONCE
            db.session.commit()
            flash("Sales draft created successfully.", "success")
            return redirect(url_for('pdf', quote_id=quote.id))
            
        except Exception as e:
            print("Error processing form:", str(e))
            flash(f"Error processing form: {str(e)}", "error")
            return redirect(url_for('form'))

    return render_template('form.html')





# SALES DRAFT PDF GENERATOR
@app.route('/quote/<int:quote_id>/download')
@login_required
def download_quote_pdf(quote_id):
    quote = db.session.get(Quote, quote_id) or abort(404)
    if int(quote.salesperson_id) != int(current_user.get_id()):
            abort(403)

    # pass in related objects
    trade_ins = quote.trade_ins if quote.trade_ins else None
    finance  = quote.finance
    packages = quote.package.split('||') if quote.package else []  # Split on || instead of comma

    pdf_buffer = generate_quote_pdf(quote, current_user, trade_ins, finance, packages)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"quote_{quote.id}.pdf"
    )





# DISPLAY PDF
@app.route('/quote/<int:quote_id>/pdf')
@login_required
def pdf(quote_id):
    # security check
    quote = db.session.get(Quote, quote_id) or abort(404)
    if quote.salesperson_id != current_user.id:
        abort(403)

    # generate
    trade_in = quote.trade_ins if quote.trade_ins else None
    finance  = quote.finance
    packages = quote.package.split('||') if quote.package else []  # Split on || instead of comma
    buf  = generate_quote_pdf(quote, current_user, trade_in, finance, packages)

   # send_file defaults to inline (content-disposition: inline)
    return send_file(
        io.BytesIO(buf.getvalue()),
        mimetype='application/pdf',
        download_name=f"quote_{quote.id}.pdf",
        as_attachment=False
    )





if __name__ == "__main__":
    app.run(debug=True)

