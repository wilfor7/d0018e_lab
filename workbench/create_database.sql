CREATE DATABASE IF NOT EXISTS d0018e_lab;
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
    short_description VARCHAR(100),
    full_description VARCHAR(500) NOT NULL,
    price INT NOT NULL,
    category_id INT UNSIGNED,
    quantity INT UNSIGNED NOT NULL,
    image_filename VARCHAR(20),
    
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

CREATE TABLE users (
	email VARCHAR(100) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    password_hash VARCHAR(100) NOT NULL,
    date_joined DATE NOT NULL
);

CREATE TABLE cart_products (
	cart_product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id INT UNSIGNED,
    email VARCHAR(100),
    quantity INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(email) REFERENCES users(email)
);

CREATE TABLE orders (
	order_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    date_ordered DATE NOT NULL,
    shipping_address VARCHAR(50),
    completed BOOLEAN,
    
    FOREIGN KEY(email) REFERENCES users(email)
);

CREATE TABLE ordered_products (
	ordered_product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNSIGNED,
    product_id INT UNSIGNED,
    price INT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE comments (
	comment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    product_id INT UNSIGNED,
    comment VARCHAR(500),
    rating INT UNSIGNED NOT NULL,
    
    FOREIGN KEY(email) REFERENCES users(email),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)