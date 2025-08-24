from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, send_file, render_template, redirect, url_for, flash, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from config import Config
from models import db, Salesperson, Quote, TradeIn, Finance
from pdf_utils import generate_quote_pdf
import io
import click
from flask.cli import with_appcontext

# --- app & db ---------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Optional: CLI command to create tables when YOU want (never at import)
@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Database tables created.")

# --- login -----------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Salesperson, int(user_id))

# --- admin -----------------------------------------------------------------
class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminIndex(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        abort(403)

admin = Admin(app, name="Sales Admin", template_mode="bootstrap3", index_view=MyAdminIndex())

class QuoteAdmin(AuthenticatedModelView):
    form_ajax_refs = { 'salesperson': { 'fields': ['name', 'phone_number'] } }
    inline_models = (TradeIn, Finance)
    column_searchable_list = ['customer_name','customer_contact','model','salesperson.name','salesperson.phone_number']
    column_formatters = {
        'trade_in_value': lambda v, c, m, n: (m.trade_ins.trade_in_value if m.trade_ins else None),
        'balance':       lambda v, c, m, n: (m.trade_ins.balance       if m.trade_ins else None),
    }
    column_list = (
        'id','salesperson.name','customer_name','model','net_price','discount','addons',
        'trade_in_value','balance','finance.bank','finance.loan_amount','finance.tenure_months',
        'finance.interest_rate','finance.monthly_installment','date_created'
    )
    column_labels = {
        'salesperson.name':'Salesperson','trade_in_value':'Trade-in Value','balance':'Trade-in Balance',
        'finance.bank':'Bank','finance.loan_amount':'Loan Amount','finance.tenure_months':'Tenure (months)',
        'finance.interest_rate':'Interest Rate (%)','finance.monthly_installment':'Monthly Installment',
        'date_created':'Date Created',
    }

admin.add_view(AuthenticatedModelView(Salesperson, db.session, name="Salespeople"))
admin.add_view(QuoteAdmin(Quote, db.session, name="Quotes"))
admin.add_view(AuthenticatedModelView(TradeIn, db.session, name="Trade-Ins"))
admin.add_view(AuthenticatedModelView(Finance, db.session, name="Financing"))

# --- routes ----------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone_number = request.form.get('phone_number')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not all([name, phone_number, password, confirm_password]): 
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
            print(f"Registration error: {e}")
            db.session.rollback()
            return redirect(url_for('register'))
    return render_template('register.html')

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

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        try:
            form = request.form
            for f in ['customer_name','customer_contact','model','retail_price','discount']:
                if f not in form:
                    flash(f"Missing required field: {f}", "error")
                    return redirect(url_for('form'))

            customer_name  = form.get('customer_name','')
            customer_contact = form.get('customer_contact','')
            model_name     = form.get('model','')
            retail_price   = int(form.get('retail_price',0))
            discount       = int(form.get('discount') or 0)
            addons         = int(form.get('addons') or 0)
            net_price      = retail_price - discount + addons

            packages           = form.getlist('packages')
            custom_packages    = [p.strip() for p in form.getlist('custom_packages[]') if p.strip()]
            package_str        = "||".join(packages + custom_packages)

            quote = Quote(
                salesperson_id=current_user.id,
                customer_name=customer_name,
                customer_contact=customer_contact,
                model=model_name,
                retail_price=retail_price,
                discount=discount,
                addons=addons,
                net_price=net_price,
                package=package_str
            )
            db.session.add(quote)
            db.session.flush()

            if form.get('tradein-checkbox'):
                trade_in_value   = int(form.get('tradein_price') or 0)
                outstanding_loan = int(form.get('tradein_outstanding') or 0)
                ti = TradeIn(
                    plate=form.get('tradein_plate',''),
                    trade_in_value=trade_in_value,
                    outstanding_loan=outstanding_loan,
                    balance=trade_in_value - outstanding_loan,
                    quote_id=quote.id
                )
                db.session.add(ti)

            if form.get('finance-checkbox'):
                bank               = form.get('finance_bank','')
                loan_amount        = int(form.get('finance_loan') or 0)
                tenure_months      = int(form.get('finance_tenure') or 0)
                interest_rate      = float(form.get('finance_rate') or 0)
                monthly_installment = loan_amount * (1 + (interest_rate/100)*(tenure_months/12)) / max(tenure_months,1)
                fin = Finance(
                    bank=bank, loan_amount=loan_amount, tenure_months=tenure_months,
                    interest_rate=interest_rate, monthly_installment=monthly_installment,
                    quote_id=quote.id
                )
                db.session.add(fin)

            db.session.commit()
            flash("Sales draft created successfully.", "success")
            return redirect(url_for('pdf', quote_id=quote.id))
        except Exception as e:
            print("Error processing form:", e)
            db.session.rollback()
            flash(f"Error processing form: {e}", "error")
            return redirect(url_for('form'))

    return render_template('form.html')

@app.route('/quote/<int:quote_id>/download')
@login_required
def download_quote_pdf(quote_id):
    quote = db.session.get(Quote, quote_id) or abort(404)
    if int(quote.salesperson_id) != int(current_user.get_id()):
        abort(403)
    trade_ins = quote.trade_ins if quote.trade_ins else None
    finance   = quote.finance
    packages  = quote.package.split('||') if quote.package else []
    pdf_buffer = generate_quote_pdf(quote, current_user, trade_ins, finance, packages)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True,
                     download_name=f"quote_{quote.id}.pdf")

@app.route('/quote/<int:quote_id>/pdf')
@login_required
def pdf(quote_id):
    quote = db.session.get(Quote, quote_id) or abort(404)
    if quote.salesperson_id != current_user.id:
        abort(403)
    trade_in = quote.trade_ins if quote.trade_ins else None
    finance  = quote.finance
    packages = quote.package.split('||') if quote.package else []
    buf = generate_quote_pdf(quote, current_user, trade_in, finance, packages)
    return send_file(io.BytesIO(buf.getvalue()), mimetype='application/pdf',
                     download_name=f"quote_{quote.id}.pdf", as_attachment=False)

# no init or run here; serverless imports `app`
