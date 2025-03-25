-- Create tables based on SQLAlchemy models
CREATE TABLE IF NOT EXISTS bikes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price INT NOT NULL,
    description TEXT,
    bought BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS bike_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bike_id INT,
    image_url VARCHAR(2048) NOT NULL,
    is_main BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bike_id INT,
    quantity INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_price INT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    bike_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(124) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL
);
