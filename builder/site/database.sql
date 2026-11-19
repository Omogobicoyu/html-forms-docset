-- Импортировать в phpMyAdmin. Существующие таблицы не удаляются.
CREATE DATABASE IF NOT EXISTS conferences CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE conferences;

CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user'
) ENGINE=InnoDB;

CREATE TABLE requests (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    room VARCHAR(200) NOT NULL,
    starts_at DATETIME NOT NULL,
    payment ENUM('При очном посещении', 'Переводом по системе СБП') NOT NULL,
    status ENUM('Новая', 'Мероприятие назначено', 'Завершено') NOT NULL DEFAULT 'Новая',
    review TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- Пароль администратора: Demo77 (хранится в виде хеша).
INSERT INTO users (login, password, full_name, phone, email, role) VALUES
('Conf2027', '$2y$10$ZpmZkMV/dl7H625PURr8/.koF19cyj2wlRF/BIvY6NFlgwJ1uoate', 'Администратор', '8(000)000-00-00', 'admin@example.test', 'admin');
