use d0018e_lab;

ALTER TABLE products DROP FOREIGN KEY FK_category_id;
ALTER TABLE products ADD CONSTRAINT FK_category_id_products FOREIGN KEY (category_id) REFERENCES categories(category_id);

ALTER TABLE cart_products DROP FOREIGN KEY cart_products_ibfk_1;
ALTER TABLE cart_products ADD CONSTRAINT FK_category_id_cart_products FOREIGN KEY (product_id) REFERENCES products(product_id);
ALTER TABLE cart_products DROP FOREIGN KEY cart_products_ibfk_2;
ALTER TABLE cart_products ADD CONSTRAINT FK_email_cart_products FOREIGN KEY (email) REFERENCES users(email);

ALTER TABLE orders DROP FOREIGN KEY orders_ibfk_1;
ALTER TABLE orders ADD CONSTRAINT FK_email FOREIGN KEY (email) REFERENCES users(email);

ALTER TABLE ordered_products DROP FOREIGN KEY ordered_products_ibfk_1;
ALTER TABLE ordered_products ADD CONSTRAINT FK_order_id_ordered_products FOREIGN KEY (order_id) REFERENCES orders(order_id);
ALTER TABLE ordered_products DROP FOREIGN KEY ordered_products_ibfk_2;
ALTER TABLE ordered_products ADD CONSTRAINT FK_product_id_ordered_products FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE comments DROP FOREIGN KEY comments_ibfk_1;
ALTER TABLE comments ADD CONSTRAINT FK_email_comments FOREIGN KEY (email) REFERENCES users(email);
ALTER TABLE comments DROP FOREIGN KEY comments_ibfk_2;
ALTER TABLE comments ADD CONSTRAINT FK_product_id_comments FOREIGN KEY (product_id) REFERENCES products(product_id);