from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:lm091702@localhost/cset180"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

app.config['SECRET_KEY'] = 'fireagatha2413.'


def q(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum


@app.route('/')
def homep():
    return render_template('landing.html')


@app.route("/register", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        acc_type = request.form['acc_type']
        query = text(
            "INSERT INTO accounts(username,password,email,acc_type)"
            "VALUES(:username, :password, :email, :acc_type)")
        params = {"username": username, "password": password, "email": email, "acc_type": acc_type}
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        return render_template('index.html')
    else:
        return render_template("base.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        acc_type = request.form['acc_type']
        user_query = text("select * from accounts where username = :username AND password = :password AND acc_type = :acc_type")
        params = {"username": username, "password": password, "acc_type": acc_type}
        result = conn.execute(user_query, params)
        user = result.fetchone()
        if user is None:
            return render_template('index.html')
        else:
            session['id'] = user[0]
            session['username'] = user[1]
            session['password'] = user[2]
            session['email'] = user[0]
            session['acc_type'] = user[3]
            if user[3] == 'admin':
                return render_template('Admin_Only.html')
            elif user[3] == 'vendor':
                return render_template('Admin_Vendor.html')
            else:
                return render_template('customer_dash.html')
    else:
        return render_template('index.html')


@app.route('/login/logout')
def logout(none=None):
    session.pop('logged in', none)
    session.pop('id', none)
    session.pop('username', none)

    return redirect(url_for('login'))


@app.route('/accounts', methods=['GET','POST'])
def Accounts():
    if 'username' in session:
        username = session['username']
        query = text("SELECT * FROM accounts WHERE username = :username")
        params = {'username': username}
        with engine.connect() as conn:
            accounts = conn.execute(query, params).fetchall()
        return render_template('accounts.html', accounts=accounts)
    else:
        return redirect(url_for('login'))


@app.route('/products')
def products():
    query = text("SELECT * FROM products")
    with engine.connect() as conn:
        products = conn.execute(query).fetchall()
    return render_template('products.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)

