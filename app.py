from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///treasury.db'
app.config['SECRET_KEY'] = 'change-this-to-something-random-later'
app.config['INVITE_CODE'] = 'kdphi2026'  # share this privately with officers

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # redirect here if not logged in

# Loads the logged-in user on every request using their session cookie
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Models (database tables) ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # stores hashed password, never plain text

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit = db.Column(db.Float, nullable=False)
    # lets us access category.transactions to get all linked transactions
    transactions = db.relationship('Transaction', backref='category', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    description = db.Column(db.String(200))
    amount = db.Column(db.Float)
    type = db.Column(db.String(20))  # 'income' or 'expense'
    # foreign key links each transaction to a category — nullable so it's optional
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

# Creates all tables if they don't already exist
with app.app_context():
    db.create_all()

# --- Auth Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Block registration if invite code is wrong
        if request.form['invite_code'] != app.config['INVITE_CODE']:
            flash('Invalid invite code.', 'danger')
            return redirect('/register')

        username = request.form['username']

        # Don't allow duplicate usernames
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken.', 'danger')
            return redirect('/register')

        # Hash the password before saving — never store plain text
        hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        # check_password_hash compares the plain text input to the stored hash
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)  # creates the session cookie
            return redirect('/')
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # clears the session cookie
    return redirect('/login')

# --- Main Routes ---

@app.route('/')
@login_required
def home():
    transactions = Transaction.query.all()
    categories = Category.query.all()
    balance = sum(t.amount if t.type == 'income' else -t.amount for t in transactions)

    # Convert transactions to plain dicts so they can be passed to JavaScript as JSON
    transactions_json = [
        {
            'date': str(t.date),
            'amount': t.amount,
            'type': t.type,
            'category': {'name': t.category.name} if t.category else None
        }
        for t in transactions
    ]

    return render_template('index.html',
        transactions=transactions,
        balance=balance,
        categories=categories,
        transactions_json=transactions_json
    )

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    new_transaction = Transaction(
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
        description=request.form['description'],
        amount=float(request.form['amount']),
        type=request.form['type'],
        # .get() returns None instead of crashing if no category was selected
        category_id=request.form.get('category_id') or None
    )
    db.session.add(new_transaction)
    db.session.commit()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    categories = Category.query.all()
    return render_template('edit.html', transaction=transaction, categories=categories)

@app.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    transaction.description = request.form['description']
    transaction.amount = float(request.form['amount'])
    transaction.type = request.form['type']
    transaction.category_id = request.form.get('category_id') or None
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect('/')

@app.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    new_category = Category(
        name=request.form['name'],
        limit=float(request.form['limit'])
    )
    db.session.add(new_category)
    db.session.commit()
    return redirect('/categories')

@app.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect('/categories')

if __name__ == '__main__':
    app.run(debug=True)