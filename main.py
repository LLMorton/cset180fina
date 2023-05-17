from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:lm091702@localhost/cset180"
engine = create_engine(conn_str, echo=True)

app.config['SECRET_KEY'] = 'fireagatha2413.'


def q(s):
    alph = "abcdefghijklmnopqrstuvwxyz"
    total = 0
    for char in s:
        total += alph.find(char) + 1
    return total


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
            "INSERT INTO accounts(username, password, email, acc_type) "
            "VALUES(:username, :password, :email, :acc_type)"
        )
        params = {
            "username": username,
            "password": password,
            "email": email,
            "acc_type": acc_type
        }
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
        user_query = text(
            "SELECT * FROM accounts WHERE username = :username AND password = :password AND acc_type = :acc_type"
        )
        params = {
            "username": username,
            "password": password,
            "acc_type": acc_type
        }
        with engine.connect() as conn:
            result = conn.execute(user_query, params)
            user = result.fetchone()

        if user is None:
            return render_template('index.html')
        else:
            session['id'] = user[0]
            session['username'] = user[1]
            session['password'] = user[2]
            session['email'] = user[3]
            session['acc_type'] = user[4]

            if user[4] == 'admin':
                return render_template('Admin_Only.html')
            elif user[4] == 'vendor':
                return render_template('Admin_Vendor.html')
            else:
                return render_template('customer_dash.html')
    else:
        return render_template('index.html')


@app.route('/login/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
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


@app.route('/dash')
def dash():
    return render_template('customer_dash.html')


@app.route('/Admin_Only/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_color = request.form['product_color']
        product_size = request.form['product_size']
        query = text(
        "INSERT INTO products (product_name, product_color, product_size) "
        "VALUES (:product_name, :product_color, :product_size)"
    )
    params = {
        "product_name": product_name,
        "product_color": product_color,
        "product_size": product_size,
    }
    with engine.connect() as conn:
        conn.execute(query, params)
        return redirect(url_for('products'))
        return render_template('add_product.html')


@app.route('/Admin_Only/edit_product/int:product_id', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_color = request.form['product_color']
        product_size = request.form['product_size']
        query = text(
        "UPDATE products SET product_name = :product_name, "
        "product_color = :product_color, product_size = :product_size "
        "WHERE id = :product_id"
    )
    params = {
        "product_id": product_id,
        "product_name": product_name,
        "product_color": product_color,
        "product_size": product_size,
    }
    with engine.connect() as conn:
        conn.execute(query, params)

    return redirect(url_for('products'))
    query = text("SELECT * FROM products WHERE id = :product_id")
    params = {"product_id": product_id}
    with engine.connect() as conn:
        product = conn.execute(query, params).fetchone()
        return render_template('edit_product.html', product=product)


@app.route('/Admin_Only/delete_product/int:product_id', methods=['GET', 'POST'])
def delete_product(product_id):
    query = text("DELETE FROM products WHERE id = :product_id")
    params = {"product_id": product_id}
    with engine.connect() as conn:
        conn.execute(query, params)
        return redirect(url_for('products'))

@app.route('/cart')
def cart():
    if 'cart' in session:
        cart_items = session['cart']
    else:
        cart_items = []
    return render_template('cart.html', cart_items=cart_items)



@app.route('/remove_from_cart/<product_name>', methods=['GET'])
def remove_from_cart(product_name):
    if 'cart' in session:
        cart_items = session['cart']
        for item in cart_items:
            if item.get('product_name') == product_name:
                cart_items.remove(item)
                session['cart'] = cart_items
                return redirect(url_for('cart'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_name = request.form['product_name']
    product_color = request.form['product_color']
    product_size = request.form['product_size']
    product = {
        'product_name': product_name,
        'product_color': product_color,
        'product_size': product_size
    }
    if 'cart' in session:
        cart_items = session['cart']
        cart_items.append(product)
        session['cart'] = cart_items
    else:
        session['cart'] = [product]
    return redirect(url_for('cart'))



@app.route('/cart/empty_cart')
def empty_cart():
    if 'cart' in session:
        session.pop('cart')
        return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET'])
def checkout():
    if 'cart' in session:
        cart_items = session['cart']
        total_price = 0
        for item in cart_items:
            total_price += item['product_price']
            session.pop('cart', None)
            return f"Checkout completed successfully! Total price: {total_price}"
            return "Your cart is empty. Please add items before checking out."


if __name__ == '__main__':
    app.run(debug=True)
