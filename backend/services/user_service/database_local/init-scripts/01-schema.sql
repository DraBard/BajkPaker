-- SQLite schema

-- Create tables based on SQLAlchemy models
CREATE TABLE IF NOT EXISTS bikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    bought BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bike_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bike_id INTEGER,
    image_url TEXT NOT NULL,
    is_main BOOLEAN DEFAULT 0,
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bike_id INTEGER,
    quantity INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_price INTEGER NOT NULL,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    bike_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (bike_id) REFERENCES bikes(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE NOT NULL
);
