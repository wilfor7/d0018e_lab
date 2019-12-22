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
    categories = db.get_categories()
    products = db.get_products(session["category_id"]) if "category_id" in session else db.get_products()
    user = session["user"] if "user" in session else None
    active_category_name = session["category_name"] if "category_name" in session else None
    return render_template("index.html", products=products, user=user, categories=categories,
                           active_category_name=active_category_name)


@app.route("/set_category", methods=["POST"])
def set_category():
    category_id = request.form["category_id"]
    if category_id == "0":
        session.pop("category_id", None)
        session.pop("category_name", None)
    else:
        session["category_id"] = category_id
        session["category_name"] = request.form["category_name"]
    return redirect(url_for("index"))


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user" not in session:
        flash("Please login before adding any products to your shopping cart.")
        return redirect(url_for("index"))
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
    orders = db.get_orders(session["user"]["user_id"])
    ordered_products = db.get_ordered_products(session["user"]["user_id"])
    categories = db.get_categories()
    if request.method == "POST":    # changing user information
        email = request.form["email"]
        if not email == request.form["confirm_email"]:
            flash("The emails do not match. Try again.")
            return render_template("mypage.html", user=session["user"], orders=orders,
                                   ordered_products=ordered_products, categories=categories)
        if len(email) == 0:
            flash("Please enter an email.")
            return render_template("mypage.html", user=session["user"], orders=orders,
                                   ordered_products=ordered_products, categories=categories)
        password = request.form["password"]
        if not password == request.form["confirm_password"]:
            flash("The passwords do not match. Try again.")
            return render_template("mypage.html", user=session["user"], orders=orders,
                                   ordered_products=ordered_products, categories=categories)
        if len(password) > 0:
            db.change_user_password(session["user"]["email"], password)
        db.change_user_email(session["user"]["email"], email)
        session["user"] = db.get_user(email)
        flash("Your user information has been updated.")
    return render_template("mypage.html", user=session["user"], orders=orders, ordered_products=ordered_products,
                           categories=categories)


@app.route("/cart", methods=["GET", "POST"])
def shopping_cart():
    if "user" not in session:
        return redirect(url_for("index"))
    cart_products = db.get_cart(session["user"]["user_id"])
    cart_empty = True if len(cart_products) == 0 else False
    if request.method == "POST":    # checkout
        db.add_order(cart_products, session["user"]["user_id"])
        db.clear_cart(session["user"]["user_id"])
        db.subtract_products_quantity(cart_products)
        return redirect(url_for("shopping_cart"))
    categories = db.get_categories()
    return render_template("cart.html", cart_products=cart_products, user=session["user"], categories=categories,
                           cart_empty=cart_empty)


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
    categories = db.get_categories()
    if "user" in session:
        return redirect(url_for("my_page"))
    return render_template("register.html", categories=categories)


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
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login_user():
    user = db.get_user(request.form["email"])
    if user != -1 and authenticate_user(user, request.form["password"]):  # check username and pass
        session["user"] = user
        return redirect(url_for("index"))   # TODO: Change to "call url"
    flash("Incorrect username or password.")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/item/<int:product_id>", methods=["GET", "POST"])
def show_product(product_id):
    user = session["user"] if "user" in session else None
    categories = db.get_categories()
    product = db.get_product(product_id)
    comments = db.get_comments(product_id)
    if request.method == "POST":    # add comment
        if user is None:
            flash("Please login before submitting a comment.")
            return render_template("product.html", product=product, user=user, categories=categories, comments=comments)
        rating = request.form["rate"]
        comment = request.form["test"]
        if len(comment) == 0:
            flash("Please enter a comment.")
            return render_template("product.html", product=product, user=user, categories=categories, comments=comments)
        db.add_comment(session["user"]["user_id"], product_id, comment, rating)
    if product is None:
        return redirect(url_for("index"))
    return render_template("product.html", product=product, user=user, categories=categories, comments=comments)


def authenticate_user(user, password):
    if check_password_hash(user["password_hash"], password):
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
