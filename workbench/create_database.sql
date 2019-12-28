CREATE DATABASE d0018e_lab;
USE d0018e_lab;

CREATE TABLE categories (
	category_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    description VARCHAR(200),
    image_filename VARCHAR(20)
);

CREATE TABLE products (
	product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    short_description VARCHAR(55),
    full_description VARCHAR(500) NOT NULL,
    price INT NOT NULL,
    category_id INT UNSIGNED,
    quantity INT UNSIGNED NOT NULL,
    image_filename VARCHAR(20),
    
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

CREATE TABLE users (
	user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    password_hash VARCHAR(100) NOT NULL,
    date_joined DATE NOT NULL,
    admin BOOL
);

CREATE TABLE cart_products (
	cart_product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id INT UNSIGNED,
    user_id INT UNSIGNED,
    quantity INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
	order_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    date_ordered DATE NOT NULL,
    complete BOOL,
    
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE ordered_products (
	ordered_product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNSIGNED,
    product_id INT UNSIGNED,
    name VARCHAR(50),
    price INT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE comments (
	comment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    product_id INT UNSIGNED,
    comment VARCHAR(500),
    rating INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)