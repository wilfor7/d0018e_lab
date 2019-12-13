import mysql.connector
from datetime import  date

from werkzeug.security import generate_password_hash


class StoreQuantityError(Exception):
    """ Exception raised if the cart quantity exceeds the store quantity """


class Database:
    def __init__(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="9a5k3Aq5zb5XaAFW",
                database="d0018e_lab"
            )
            print("Server and database connection established.")
            self.cursor = self.db.cursor()
            print("Cursor created.")
        except mysql.connector.errors.ProgrammingError:
            print("Error establishing a connection")

    # Insert some stuff to a table
    # Columns: A list of column names (in order)
    # Values: The values (in order) to be inserted into the matching column names
    def __table_insert(self, table_name, columns, values):
        sql = "INSERT INTO " + table_name + " ("
        for e in columns:
            sql += e + ", "
        sql = sql[:len(sql)-2]      # remove last ", "
        sql += ") VALUES ("
        for e in values:
            if type(e) == int:
                sql += "%d, "
            if type(e) == str:
                sql += "%s, "
        sql = sql[:len(sql) - 2]    # remove last ", "
        sql += ")"
        self.cursor.execute(sql, values)

    def __fetch_table(self, table_name):
        sql = "SELECT * FROM " + table_name
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # Parses a list (single row table) into a dictionary which works with Flask
    def __parse_list(self, l):
        column_names = self.cursor.column_names
        result = {}
        i = 0
        for name in column_names:
            result[name] = l[i]
            i += 1
        return result

    # Parses a list of lists (multiple row table) into a list of dictionaries which works with Flask
    def __parse_double_list(self, l):
        result = []
        column_names = self.cursor.column_names
        for product in l:  # table = list of lists
            i = 0
            dictionary = {}
            for name in column_names:
                dictionary[name] = product[i]
                i += 1
            result.append(dictionary)
        return result

    # Returns a list of dictionaries, one for each product
    # Each dictionary has a entry for each column:
    #   {column_name : value}
    def get_products(self):
        table = self.__fetch_table("products")      # actual table information (list of lists)
        column_names = self.cursor.column_names     # column names of table (list)
        result = []
        for product in table:   # table = list of lists
            i = 0
            dictionary = {}
            for name in column_names:
                dictionary[name] = product[i]
                i += 1
            result.append(dictionary)
        return result

    # Subtracts the quantity of products in the table "products" with some given products
    def subtract_products_quantity(self, products):
        for product in products:
            sql = "SELECT quantity FROM products WHERE product_id = " + str(product["product_id"])
            self.cursor.execute(sql)
            product_quantity = self.cursor.fetchone()[0]
            new_quantity = product_quantity - product["quantity"]
            if new_quantity < 0:
                new_quantity = 0
            sql = "UPDATE products SET quantity = " + str(new_quantity) + " WHERE product_id = " + \
                  str(product["product_id"])
            self.cursor.execute(sql)
            self.db.commit()

    def add_user(self, user_columns, user_values):
        self.__table_insert("users", user_columns, user_values)
        self.db.commit()

    # Fetches all the information about a user given the primary key (email address)
    # User comes in the form of a dictionary
    # Returns -1 if user does not exist
    def get_user(self, email):
        sql = "SELECT * FROM users WHERE email = \'" + email + "'"
        self.cursor.execute(sql)
        user_info = self.cursor.fetchone()
        if user_info is None:
            return -1
        return self.__parse_list(user_info)

    def change_user_info(self, new_email, old_email, password):
        sql = "UPDATE users SET password_hash = '" + generate_password_hash(password) + "', email = '" + new_email + \
              "' WHERE email = '" + old_email + "'"
        self.cursor.execute(sql)
        self.db.commit()

    def get_cart(self, user_id):
        sql = "SELECT * FROM products p INNER JOIN cart_products cp " \
              "ON p.product_id = cp.product_id AND user_id = '" + str(user_id) + "'"
        self.cursor.execute(sql)
        cart_products = self.cursor.fetchall()
        return self.__parse_double_list(cart_products)

    def add_product_to_cart(self, product_id, user_id):
        sql = "SELECT quantity FROM cart_products WHERE product_id = " + str(product_id) + " AND user_id = " + \
              str(user_id)
        self.cursor.execute(sql)
        quantity = self.cursor.fetchone()
        if quantity is None:    # insert item into cart_products, otherwise just increment quantity
            self.__quantity_check(1, product_id)
            column_names = ["product_id", "user_id", "quantity"]
            column_values = [str(product_id), str(user_id), str(1)]
            self.__table_insert("cart_products", column_names, column_values)
            self.db.commit()
        else:
            self.__quantity_check(quantity[0] + 1, product_id)
            sql = "UPDATE cart_products SET quantity = " + str(quantity[0] + 1) + " WHERE product_id = " + \
                  str(product_id)
            self.cursor.execute(sql)
            self.db.commit()

    def alter_cart_product_quantity(self, user_id, product_id, delta_quantity):
        sql = "SELECT quantity FROM cart_products WHERE product_id = " + str(product_id) + " AND user_id = " + \
            str(user_id)
        self.cursor.execute(sql)
        quantity = int(self.cursor.fetchone()[0]) + delta_quantity
        self.__quantity_check(quantity, product_id)
        if quantity < 1:
            self.remove_cart_product(user_id, product_id)
        sql = "UPDATE cart_products SET quantity = " + str(quantity) + " WHERE product_id = " + str(product_id) + \
            " AND user_id = " + str(user_id)
        self.cursor.execute(sql)
        self.db.commit()

    def remove_cart_product(self, user_id, product_id):
        sql = "DELETE FROM cart_products WHERE product_id = " + str(product_id) + " AND user_id = " + str(user_id)
        self.cursor.execute(sql)
        self.db.commit()

    def clear_cart(self, user_id):
        sql = "DELETE FROM cart_products WHERE user_id = " + str(user_id)
        self.cursor.execute(sql)
        self.db.commit()

    def __quantity_check(self, new_cart_quantity, product_id):
        sql = "SELECT quantity FROM products WHERE product_id = " + str(product_id)
        self.cursor.execute(sql)
        store_quantity = self.cursor.fetchone()[0]
        if new_cart_quantity > store_quantity:
            raise StoreQuantityError

    # Add a order and ordered_products given some products
    def add_order(self, products, user_id):
        columns = ("user_id", "date_ordered")
        values = (str(user_id), date.today().__str__())
        self.__table_insert("orders", columns, values)
        order_id = self.cursor.lastrowid
        for product in products:
            columns = ("order_id", "product_id", "name", "price", "quantity")
            values = (str(order_id), str(product["product_id"]), product["name"], str(product["price"]),
                      str(product["quantity"]))
            self.__table_insert("ordered_products", columns, values)
        self.db.commit()

    def get_orders(self, user_id):
        sql = "SELECT * FROM orders WHERE user_id = " + str(user_id)
        self.cursor.execute(sql)
        orders = self.cursor.fetchall()
        return self.__parse_double_list(orders)

    def get_ordered_products(self, user_id):
        sql = "SELECT order_id FROM orders WHERE user_id = " + str(user_id)
        self.cursor.execute(sql)
        ids = self.cursor.fetchall()
        if len(ids) == 0:            # no orders in the database
            ids = [(0,)]         # could be any integer, really
        ids_str = ""
        for id in ids:
            ids_str = ids_str + str(id[0]) + ", "
        ids_str = ids_str[:len(ids_str) - 2]    # remove last ", "
        sql = "SELECT * FROM ordered_products WHERE order_id IN (" + ids_str + ")"
        self.cursor.execute(sql)
        ordered_products = self.cursor.fetchall()
        return self.__parse_double_list(ordered_products)
