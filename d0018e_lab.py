from datetime import timedelta

from flask import Flask, render_template, redirect, session, url_for, request, flash

from database import Database, StoreQuantityError
from config import Config

db = Database()
app = Flask(__name__)
app.config.from_object(Config)
app.send_file_max_age_default = timedelta(seconds=1)


@app.route('/placeholder/category/<int:category_id>/<string:category_name>')
@app.route("/placeholder", defaults={'category_id': 0, 'category_name': 'All products'})
def placeholder(category_id, category_name):
    return str(category_id) + " " + category_name


@app.route("/", methods=["GET", "POST"], defaults={"category_id": 0})
@app.route("/category/<int:category_id>", methods=["GET", "POST"])
def index(category_id):
    categories = db.get_categories()
    products = db.get_products(category_id)
    active_category = {"id": category_id, "name": "All products"}
    for category in categories:
        if category["category_id"] == category_id:
            active_category["name"] = category["name"]
    user = session["user"] if "user" in session else None
    return render_template("index.html", products=products, user=user, categories=categories,
                           active_category=active_category)


@app.route("/item/<int:product_id>", methods=["GET", "POST"])
def show_product(product_id):
    user = session["user"] if "user" in session else None
    categories = db.get_categories()
    product = db.get_product(product_id)
    comments = db.get_comments(product_id)
    db.add_names(comments)
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
        return redirect(url_for("show_product", product_id=product_id))
    if product is None:
        return redirect(url_for("index"))
    return render_template("product.html", product=product, user=user, categories=categories, comments=comments)


@app.route("/set_category", methods=["POST"])
def set_category():
    category_id = request.form["category_id"]
    if category_id == "0":
        return redirect(url_for("index"))
    return redirect(url_for("index", category_id=category_id))


@app.route("/search_products", methods=["POST"])
def search_products():
    categories = db.get_categories()
    user = session["user"] if "user" in session else None
    products = db.search_products(request.form["search"])
    active_category = {"name": "Search result", "id": 0}
    return render_template("index.html", products=products, user=user, categories=categories,
                           active_category=active_category)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = int(request.form["product_id"])
    if "user" not in session:
        flash("Please login before adding any products to your shopping cart.")
        if request.form["show_page"] == "0":
            return redirect(url_for("index", category_id=request.form["category_id"]))
        return redirect(url_for("show_product", product_id=product_id))
    try:
        db.add_product_to_cart(product_id, session["user"]["user_id"])
        flash("The product has been added to your shopping cart.")
    except StoreQuantityError:
        flash("We do not have that many items in stock currently (your cart quantity exceeds the store quantity).")
    if request.form["show_page"] == "0":
        return redirect(url_for("index", category_id=request.form["category_id"]))
    return redirect(url_for("show_product", product_id=product_id))


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
        user = db.get_user(email)
        if (user is not None) and (user["user_id"] != session["user"]["user_id"]):
            flash("A user with that email address already exists.")
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
    if db_user != -1:
        flash("A user with that email already exists.")
        return redirect(url_for("register"))
    if len(email) == 0:
        flash("Please enter an email.")
        return redirect(url_for("register"))
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    if password != confirm_password:
        flash("The passwords does not match. Try again.")
        return redirect(url_for("register"))
    if len(password) == 0:
        flash("Please enter a password.")
        return redirect(url_for("register"))
    first_name = request.form["first_name"]
    if len(first_name) == 0:
        flash("Please enter a first name.")
        return redirect(url_for("register"))
    db.add_user(email, password, first_name, request.form["last_name"])
    flash("Your new user account has been registered.")
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login_user():
    user = db.get_user(request.form["email"])
    if user != -1 and Database.authenticate_user(user, request.form["password"]):  # check username and pass
        session["user"] = user
        return redirect(url_for("index"))
    flash("Incorrect username or password.")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"], defaults={"order_type": "Empty"})
@app.route("/admin/<string:order_type>", methods=["GET", "POST"])
def admin_orders(order_type):
    if "user" not in session or session["user"]["admin"] == 0:  # access denied
        return redirect(url_for("index"))
    if order_type == "Empty":
        orders = None
    elif order_type == "Complete":
        orders = db.get_complete_orders()
    elif order_type == "Incomplete":
        orders = db.get_incomplete_orders()
    ordered_products = db.get_ordered_products()
    categories = db.get_categories()
    if orders is not None:
        db.add_names(orders)
    return render_template("admin_orders.html", orders=orders, ordered_products=ordered_products, categories=categories,
                           user=session["user"])


@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    order_id = request.form["cancel_order_id"]
    db.cancel_order(order_id)
    return redirect(url_for("my_page"))


@app.route("/complete_order", methods=["POST"])
def complete_order():
    order_id = request.form["complete_order_id"]
    db.complete_order(order_id)
    return redirect(url_for("admin_orders"))


if __name__ == '__main__':
    app.run(debug=True)
