from datetime import timedelta, date

from flask import Flask, render_template, redirect, session, url_for, request, flash

from database import Database
from config import Config

from werkzeug.security import generate_password_hash, check_password_hash

db = Database()
app = Flask(__name__)
app.config.from_object(Config)
app.send_file_max_age_default = timedelta(seconds=1)

product_info = db.get_products()    # gonna have to "reload" this everytime table is changed
                                    # (i.e an admin changes the price, description or automatic change of quantity)


@app.route("/", methods=["GET", "POST"])
def index():
    if "user" in session:                                               # if logged in
        if request.method == "POST":                                    # if logging out
            session.pop("user", None)
            return redirect(url_for("index"))
        return render_template("index.html", products=product_info, user=session["user"])
    if request.method == "POST":                                        # if logging in
        db_user = db.get_user(request.form["email"])
        # TODO: Check if email exists (and mby flash error msg if not)
        if db_user != -1 and db.authenticate_user(db_user, request.form["password"]):     # check username and pass
            session["user"] = db_user                                   # load user into session["user"] and ...
            return redirect(url_for("index"))
        flash("Incorrect username or password")
    return render_template("index.html", products=product_info, user=None)


@app.route("/mypage", methods=["GET", "POST"])
def my_page():
    if "user" not in session:
        redirect(url_for("index"))
    return render_template("mypage.html")


@app.route("/cart", methods=["GET", "POST"])
def shopping_cart():
    if "user" not in session:
        redirect(url_for("index"))
    cart_products = db.get_cart(session["user"]["email"])
    return render_template("cart.html", cart_products=cart_products, user=session["user"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        redirect(url_for("my_page"))    # TODO: change this to "mypage" later?
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("The passwords does not match. Try again.")
            render_template("register.html")
        user_columns = ("email", "password_hash", "first_name", "last_name", "date_joined")
        user_values = [request.form["email"], generate_password_hash(request.form["password"]),
                       request.form["first_name"], request.form["last_name"], date.today().__str__()]
        db.add_user(user_columns, user_values)
    return render_template("register.html")


@app.route('/item/<int:product_id>', methods=["GET", "POST"])
def show_product(product_id):
    return '<h2> Wow look, so much information about the product with product id: %d' % product_id


@app.route('/add_to_cart/<int:product_id>', methods=["GET", "POST"])
def add_to_cart(product_id):
    db.add_product_to_cart(product_id, session["user"]["email"])
    return render_template("index.html", products=product_info, user=session["user"])


@app.route('/placeholder')
def placeholder():
    return 'This is a placeholder ...'


if __name__ == '__main__':
    app.run(debug=True)
