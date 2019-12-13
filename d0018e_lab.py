from datetime import timedelta, date

from flask import Flask, render_template, redirect, session, url_for, request, flash

from database import Database, StoreQuantityError
from config import Config

from werkzeug.security import generate_password_hash, check_password_hash

db = Database()
app = Flask(__name__)
app.config.from_object(Config)
app.send_file_max_age_default = timedelta(seconds=1)


@app.route("/", methods=["GET", "POST"])
def index():
    product_info = db.get_products()
    if "user" in session:
        return render_template("index.html", products=product_info, user=session["user"])
    return render_template("index.html", products=product_info, user=None)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = int(request.form["product_id"])
    try:
        db.add_product_to_cart(product_id, session["user"]["user_id"])
        flash("The product has been added to your shopping cart.")
    except StoreQuantityError:
        flash("We do not have that many items in stock currently (your cart quantity exceeds the store quantity).")
    return redirect(url_for("index"))


@app.route("/mypage", methods=["GET", "POST"])
def my_page():
    if "user" not in session:
        return redirect(url_for("index"))
    if request.method == "POST":    # changing user information
        email = request.form["email"]
        if not email == request.form["confirm_email"]:
            flash("The emails do not match. Try again.")
            return render_template("mypage.html", user=session["user"])

        if len(email) == 0:
            flash("Please enter an email.")
            return render_template("mypage.html", user=session["user"])

        password = request.form["password"]
        if not password == request.form["confirm_password"]:
            flash("The passwords do not match. Try again.")
            return render_template("mypage.html", user=session["user"])

        if len(password) == 0:
            flash("Please enter a password.")
            return render_template("mypage.html", user=session["user"])

        db.change_user_info(email, session["user"]["email"], password)
        session["user"] = db.get_user(email)
        flash("Your user information has been updated.")

    orders = db.get_orders(session["user"]["user_id"])
    ordered_products = db.get_ordered_products(session["user"]["user_id"])
    return render_template("mypage.html", user=session["user"], orders=orders, ordered_products=ordered_products)


@app.route("/cart", methods=["GET", "POST"])
def shopping_cart():
    if "user" not in session:
        return redirect(url_for("index"))
    cart_products = db.get_cart(session["user"]["user_id"])
    print(cart_products)
    if request.method == "POST":    # checkout
        db.add_order(cart_products, session["user"]["user_id"])
        db.clear_cart(session["user"]["user_id"])
        db.subtract_products_quantity(cart_products)
        return redirect(url_for("shopping_cart"))
    return render_template("cart.html", cart_products=cart_products, user=session["user"])


@app.route("/increment_cart_product", methods=["POST"])
def increment_cart_product():
    product_id = int(request.form["product_id"])
    try:
        db.alter_cart_product_quantity(session["user"]["user_id"], product_id, 1)
    except StoreQuantityError:
        flash("We do not have that many items in stock currently (your cart quantity exceeds the store quantity).")
    return redirect(url_for("shopping_cart"))


@app.route("/decrement_cart_product", methods=["POST"])
def decrement_cart_product():
    product_id = int(request.form["product_id"])
    try:
        db.alter_cart_product_quantity(session["user"]["user_id"], product_id, -1)
    except StoreQuantityError:
        flash("We do not have that many items in stock currently (your cart quantity exceeds the store quantity).")
    return redirect(url_for("shopping_cart"))


@app.route("/remove_cart_product", methods=["POST"])
def remove_cart_product():
    product_id = int(request.form["product_id"])
    db.remove_cart_product(session["user"]["user_id"], product_id)
    return redirect(url_for("shopping_cart"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("my_page"))
    return render_template("register.html")


@app.route("/register_user", methods=["POST"])
def register_user():
    if "user" in session:
        return redirect(url_for("my_page"))
    email = request.form["email"]
    db_user = db.get_user(email)
    if db_user is not -1:
        flash("A user with that email already exists.")
        return render_template("register.html")
    if len(email) == 0:
        flash("Please enter an email.")
        return render_template("register.html")
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    if password != confirm_password:
        flash("The passwords does not match. Try again.")
        return render_template("register.html")
    if len(password) == 0:
        flash("Please enter a password.")
        return render_template("register.html")
    first_name = request.form["first_name"]
    if len(first_name) == 0:
        flash("Please enter a first name.")
        return render_template("register.html")
    user_columns = ("email", "password_hash", "first_name", "last_name", "date_joined")
    user_values = [email, generate_password_hash(password),
                   first_name, request.form["last_name"], date.today().__str__()]
    db.add_user(user_columns, user_values)


@app.route("/login", methods=["POST"])
def login_user():
    db_user = db.get_user(request.form["email"])
    if db_user != -1 and authenticate_user(db_user, request.form["password"]):  # check username and pass
        session["user"] = db_user
        return redirect(url_for("index"))   # TODO: Change to "call url"
    flash("Incorrect username or password")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route('/item/<int:product_id>', methods=["GET", "POST"])
def show_product(product_id):
    render_template("product.html", product=None)


@app.route('/placeholder')
def placeholder():
    return 'This is a placeholder ...'


def authenticate_user(user, password):
    if check_password_hash(user["password_hash"], password):
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
