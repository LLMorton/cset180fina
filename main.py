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


@app.route('/login')
def login():
    if request.method == ['GET', 'POST']:
        username = request.form['username']
        password = request.form['password']
        acc_type = request.form['acc_type']

        query = text("select * from accounts where username = :username AND password= :password and acc_type= :acc_type")
        params = {"username": username, "password": password,  "acc_type": acc_type}
        with engine.connect() as conn:
            user = conn.execute(query, params).fetchone()
        if user is None:
            return redirect(url_for('login'))
        else:
            return render_template('index.html')


@app.route('/login/logout')
def logout(none=None):
    session.pop('logged in', none)
    session.pop('id', none)
    session.pop('username', none)

    return redirect(url_for('login'))


@app.route("/dashboard")
def dash():
    return render_template("dashboard.html")


@app.route("/home")
def home():
    query = text("SELECT * FROM accounts")
    result = conn.execute(query)
    accounts = []
    for row in result:
        accounts.append(row)
    return render_template("homepage.html")


@app.route('/accounts')
def get_accounts():
    accs = conn.execute(text("select * from accounts")).all()
    query = text("SELECT * FROM accounts")
    result = conn.execute(query)
    accounts = []
    for row in result:
        accounts.append(row)

    return render_template('accounts.html', accounts=accs)


@app.route('/products')
def products():
    query = text("SELECT * FROM products")
    with engine.connect() as conn:
        products = conn.execute(query).fetchall()
    return render_template('products.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)

