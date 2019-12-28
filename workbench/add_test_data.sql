USE d0018e_lab;

# clear
DELETE FROM ordered_products;
DELETE FROM orders;
DELETE FROM cart_products;
DELETE FROM comments;
DELETE FROM users;
DELETE FROM products;
DELETE FROM categories;

ALTER TABLE ordered_products AUTO_INCREMENT = 1;
ALTER TABLE orders AUTO_INCREMENT = 1;
ALTER TABLE cart_products AUTO_INCREMENT = 1;
ALTER TABLE comments AUTO_INCREMENT = 1;
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE products AUTO_INCREMENT = 1;
ALTER TABLE categories AUTO_INCREMENT = 1;

# insert data
INSERT INTO categories (name)
VALUES ('Laptops');
INSERT INTO categories (name)
VALUES ('GPUs');

INSERT INTO products (name, short_description, full_description, price, category_id, quantity, image_filename)
VALUES ('product A', 'This is some (short) description about product A', 'This is a full description about product A. Wow so much info!', 1337, 1, 10, 'placeholder_a.jpg');
INSERT INTO products (name, short_description, full_description, price, category_id, quantity, image_filename)
VALUES ('product B', 'This is some (short) description about product B', 'This is a full description about product B. Wow so much info!', 4242, 2, 10, 'placeholder_b.jpg');

INSERT INTO users (email, first_name, last_name, password_hash, date_joined, admin)
VALUES ('test@gmail.com', 'William', 'Fors', 'pbkdf2:sha256:150000$L3HFb8SA$473ae733ee66504e8a46215d74f0afe60c8b3ac05299b8861775d4ba696c5d6d', '2019-11-28', true);
INSERT INTO users (email, first_name, password_hash, date_joined, admin)
VALUES ('test2@gmail.com', 'Pelle', 'pbkdf2:sha256:150000$L3HFb8SA$473ae733ee66504e8a46215d74f0afe60c8b3ac05299b8861775d4ba696c5d6d', '3000-01-01', false);

INSERT INTO comments (user_id, product_id, comment, rating)
VALUES (1, 1, 'Den här produkten suger! Gör om, gör rätt!', 0);
INSERT INTO comments (user_id, product_id, comment, rating)
VALUES (2, 1, 'Wow, bästa produkten någonsin! Nice!!!', 5);

INSERT INTO cart_products (product_id, user_id, quantity)
VALUES (1, 1, 1);
INSERT INTO cart_products (product_id, user_id, quantity)
VALUES (2, 1, 5);


INSERT INTO orders (user_id, date_ordered, complete)
VALUES (1, '2019-11-28', true);
INSERT INTO orders (user_id, date_ordered, complete)
VALUES (1, '3000-01-01', false);

INSERT INTO ordered_products (order_id, product_id, name, price, quantity)
VALUES (1, 1, "product A", 1337, 5);
INSERT INTO ordered_products (order_id, product_id, name, price, quantity)
VALUES (1, 2, "product B", 4242, 3);
INSERT INTO ordered_products (order_id, product_id, name, price, quantity)
VALUES (2, 1, "product A", 9999, 10);