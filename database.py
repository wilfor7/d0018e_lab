import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="d0018e_lab"
            )
            print("Server and database connection established.")
            self.cursor = self.db.cursor()
            print("Cursor created.")
        except mysql.connector.errors.ProgrammingError:
            print("Error establishing a connection")

    # Assuming we are already using some database (mysql > USE <database>)
    # column_names is a list where (python --> mysql)
    #   String elements become VARCHAR (of some length (?))
    #   int become INT
    #   ...
    def create_table(self, table_name, column_names):
        sql = "CREATE TABLE " + table_name  # TODO: finish
        self.cursor.execute(sql)

    # Insert some stuff to a table
    # columns: A list of column names (in order)
    # values: The values (in order) to be inserted into the matching column names
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
        self.db.commit()

    def __fetch_table(self, table_name):
        sql = "SELECT * FROM " + table_name
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # prases a list of lists (table) into a dictionary which Flask likes
    def __parse_list(self, l):
        column_names = self.cursor.column_names
        result = {}
        i = 0
        for name in column_names:
            result[name] = l[i]
            i += 1
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

    def add_user(self, user_columns, user_values):
        self.__table_insert("users", user_columns, user_values)

    # fetches all the information about a user given the primary key (email address)
    # user comes in the form of a dictionary
    # returns -1 if user does not exist
    def get_user(self, email):
        sql = "SELECT * FROM users WHERE email = '" + email + "'"
        self.cursor.execute(sql)
        user_info = self.cursor.fetchone()
        if user_info is None:
            return -1
        return self.__parse_list(user_info)

    def authenticate_user(self, user, password):
        if check_password_hash(user["password_hash"], password):
            return True
        return False

    def get_cart(self, email):
        sql = "SELECT * FROM products p INNER JOIN cart_products cp " \
              "ON p.product_id = cp.product_id AND email = '" + email + "'"
        self.cursor.execute(sql)
        cart_products = self.cursor.fetchall()
        result = []
        column_names = self.cursor.column_names
        for product in cart_products:  # table = list of lists
            i = 0
            dictionary = {}
            for name in column_names:
                dictionary[name] = product[i]
                i += 1
            result.append(dictionary)
        return result

    def add_product_to_cart(self, product_id, email):
        sql = "SELECT quantity FROM cart_products WHERE product_id = " + str(product_id) + ""
        self.cursor.execute(sql)
        quantity = self.cursor.fetchone()
        if quantity is None:    # insert item into cart_products, otherwise just increment quantity
            column_names = ["product_id", "email", "quantity"]
            column_values = [product_id, email, 1]
            self.__table_insert("cart_products", column_names, column_values)
        else:
            sql = "UPDATE cart_products SET quantity = " + str(quantity[0] +  1) + " WHERE product_id = " + str(product_id)\
                  + ""
            self.cursor.execute(sql)
            self.db.commit()