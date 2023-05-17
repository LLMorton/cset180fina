from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import cursor

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


@app.route('/Admin_Only/edit_product/<int:product_id>', methods=['GET', 'POST'])
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


@app.route('/Admin_Only/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    query = text("DELETE FROM products WHERE id = :product_id")
    params = {"product_id": product_id}
    with engine.connect() as conn:
        conn.execute(query, params)
        return redirect(url_for('products'))


@app.route('/cart', methods=['GET', 'POST'])
def cart(conn = engine.connect()):
    if request.method == 'POST':
        query = text("SELECT * FROM products")
        result = conn.execute(query)
        product = []
        for row in result:
            product.append(row)
        max_cart_id =  text("SELECT MAX(cart_id) AS max_id FROM cart")
        results = conn.execute(max_cart_id).fetchone()
        max_id = results[0] if results[0] is not None else 1
        max_id = int(max_id)
        new_id = max_id + 1

        item_id = request.form['product_id']
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        inventory = request.form['inventory']
        product_cost = request.form['product_cost']
        image = request.form['image']
        shopper_id = session['id']
        status = 'open'
        Cart_query = text("SELECT cart_id FROM cart WHERE shopper_id = :shopper_id AND status = 'open'")
        Cart_result = conn.execute(Cart_query, {"shopper_id": shopper_id}).fetchone()
        if Cart_result:
            with engine.connect() as conn:
                cart_id = Cart_result[0]
                Item_query = text("SELECT * FROM cart WHERE cart_id = :cart_id AND item_id = :item_id")
                Item_result = conn.execute(Item_query,{"cart_id": cart_id, "item_id": item_id}).fetchone()
            if Item_result:
                previous_amount = int(Item_result[4])
                new_amount = previous_amount + int(inventory)
                update_query = text("UPDATE cart SET inventory = :new_amount "
                                    "WHERE cart_id = :cart_id AND item_id = :item_id")
                update_params = {
                    "new_amount": new_amount,
                    "cart_id": cart_id,
                    "item_id": item_id
                }
            else:
                # Add an item to exisiting cart
                query = text("INSERT INTO cart (cart_id,"
                             " user_id, "
                            "product_id, "
                             "inventory, "
                             "vendor_name, "
                             "img_url, "
                             "ordered_by, "
                             "status) "
                             "VALUES (:cart_id, "
                             ":user_id, "
                             ":item_id, "
                             ":product_name, "
                             ":product_type, "
                             ":product_cost, "
                             ":quantity, "
                             ":image, "
                             ":ordered_by, "
                             ":status)")
                params = {
                    "cart_id": cart_id,
                    "user_id": user_id,
                    "item_id": item_id,
                    "product_name": product_name,
                    "product_type": product_type,
                    "product_cost": product_cost,
                    "inventory": inventory,
                    "image": image,
                    "ordered_by": session['username'],
                    "status": status
                }
                with engine.connect() as conn:
                    conn.execute(query, params)
                    conn.commit()
            return redirect(url_for('Products'))
        else:
            query = text("INSERT INTO cart (cart_id,"
                         " shopper_id, "
                         "item_id, "
                         "product_name, "
                         "product_type, "
                         "product_cost, "
                         "product_quantity, "
                         "vendor_name, "
                         "img_url, "
                         "ordered_by, "
                         "status) "
                         "VALUES (:cart_id, "
                         ":shopper_id, "
                         ":item_id, "
                         ":product_name, "
                         ":product_type, "
                         ":product_cost, "
                         ":product_quantity, "
                         ":vendor_name, "
                         ":img_url, "
                         ":ordered_by, "
                         ":status)")
            params = {
                "id": id,
                "shopper_id": shopper_id,
                "item_id": item_id,
                "product_name": product_name,
                "product_type": product_type,
                "product_cost": product_cost,
                "inventory": inventory,
                "image": image,
                "ordered_by": session['username'],
                "status": status
            }
            with engine.connect() as conn:
                conn.execute(query, params)
                conn.commit()
            return render_template("Products.html")


@app.route('/view_cart')
def view_cart():
    if 'id' in session:
        shopper_id = session['id']
        with engine.connect() as conn:
            query = text("SELECT * FROM cart WHERE shopper_id = :shopper_id AND status = 'open'")
            items = conn.execute(query, {"shopper_id": shopper_id}).fetchall()
            cart_query = text("SELECT cart_id FROM cart WHERE shopper_id = :shopper_id AND status = 'open'")
            cart_result = conn.execute(cart_query, {"shopper_id": shopper_id}).fetchone()
            cart_id = cart_result[0] if cart_result else None
            if cart_id is None:
                update_query = text("INSERT INTO cart (shopper_id, status) VALUES (:shopper_id, 'open') RETURNING cart_id")
                cart_id = conn.execute(update_query, {"shopper_id": shopper_id}).fetchone()[0]

        return render_template('cart.html', items=items, cart_id=cart_id)


@app.route('/cart/empty_cart')
def empty_cart():
    if 'cart' in session:
        session.pop('cart')
        return redirect(url_for('cart'))




def insert_review(product, rating, comment, db_config=None):
    conn = mysql.connector.connect(db_config)
    cursor = conn.cursor()
    query = "INSERT INTO product_reviews (product, rating, comment) VALUES (%s, %s, %s)"
    values = (product, rating, comment)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/review', methods=['POST'])
def review():
    if request.method == 'POST':
        product = request.form['product']
        rating = request.form['rating']
        comment = request.form['comment']
        insert_review(product, rating, comment)
        return "Review successfully submitted!"


if __name__ == '__main__':
    app.run(debug=True)
