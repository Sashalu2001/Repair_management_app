CREATE DATABASE IF NOT EXISTS repair_management;
USE repair_management;

-- Создание таблиц
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    contact VARCHAR(100),
    role ENUM('user', 'admin') NOT NULL
);

CREATE TABLE IF NOT EXISTS contractors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS objects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS types_of_work (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    multiplier DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_statuses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contractor_id INT,
    object_id INT,
    type_of_work_id INT,
    user_id INT,
    materials TEXT,
    customer_price DECIMAL(10, 2) NOT NULL,
    area DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (contractor_id) REFERENCES contractors(id),
    FOREIGN KEY (object_id) REFERENCES objects(id),
    FOREIGN KEY (type_of_work_id) REFERENCES types_of_work(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Вставка первоначальных данных
INSERT INTO users (login, password, contact, role) VALUES
('user', 'user', 'user@example.com', 'user'),
('admin', 'admin', 'admin@example.com', 'admin');

INSERT INTO contractors (name) VALUES
('Строительный Дом'),
('Мастер-Ремонт'),
('Уютный Дом'),
('РемонтСервис'),
('ДомСтрой');

INSERT INTO materials (name, price) VALUES
('Гипсокартон', 150),
('Декоративная штукатурка', 300),
('Полимерная плитка', 250),
('Ламинат Lamington', 200),
('Экошпон', 400);

INSERT INTO objects (name) VALUES
('Квартира'),
('Офис'),
('Торговый центр'),
('Дачный дом'),
('Таунхаус');

INSERT INTO types_of_work (name, multiplier) VALUES
('Штукатурка стен', 1.2),
('Укладка плитки', 2.0),
('Монтаж натяжных потолков', 2.5),
('Монтаж электропроводки', 3.0),
('Установка сантехники', 1.8);

-- Добавление начальных статусов
INSERT INTO order_statuses (status) VALUES
('В обработке'),
('Выполнен'),
('Отменен'),
('Ожидает подтверждения');