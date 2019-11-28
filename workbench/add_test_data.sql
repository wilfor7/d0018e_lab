USE d0018e_lab;

INSERT INTO products (name, short_description, full_description, price, quantity, image_filename)
VALUES ('product A', 'This is some (short) description about product A', 'This is a full description about product A. Wow so much info!', 1337, 100, 'placeholder_a.jpg');
INSERT INTO products (name, short_description, full_description, price, quantity, image_filename)
VALUES ('product B', 'This is some (short) description about product A', 'This is a full description about product A. Wow so much info!', 4242, 99, 'placeholder_b.jpg');

INSERT INTO users (email, first_name, last_name, password_hash, date_joined)
VALUES ('test@gmail.com', 'William', 'Fors', 'pbkdf2:sha256:150000$L3HFb8SA$473ae733ee66504e8a46215d74f0afe60c8b3ac05299b8861775d4ba696c5d6d', '2019-11-28');
INSERT INTO users (email, first_name, password_hash, date_joined)
VALUES ('test2@gmail.com', 'Pelle', 'pbkdf2:sha256:150000$L3HFb8SA$473ae733ee66504e8a46215d74f0afe60c8b3ac05299b8861775d4ba696c5d6d', '3000-01-01');

INSERT INTO cart_products (product_id, email, quantity)
VALUES (1, 'test@gmail.com', 1);
INSERT INTO cart_products (product_id, email, quantity)
VALUES (2, 'test@gmail.com', 5);