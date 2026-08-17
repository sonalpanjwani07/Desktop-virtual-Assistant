-- Smart AI Assistant Pro - MySQL setup for logging
-- Run in MySQL Workbench

CREATE DATABASE IF NOT EXISTS `log`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `log`;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(120) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS command_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command_name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    command_type_id INT NOT NULL,
    input_text TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_activity_command_type FOREIGN KEY (command_type_id) REFERENCES command_types(id)
);

CREATE TABLE IF NOT EXISTS user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command VARCHAR(100) NOT NULL,
    input_text TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mood_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mood VARCHAR(50) NOT NULL,
    suggestion TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS funfact_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fact TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(120) NOT NULL,
    status_message TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_log_id INT NULL,
    query_text TEXT NOT NULL,
    search_engine VARCHAR(40) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_search_activity FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
);

CREATE TABLE IF NOT EXISTS weather_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_log_id INT NULL,
    city VARCHAR(120) NOT NULL,
    country VARCHAR(80) NULL,
    channel VARCHAR(80) NULL,
    temperature_c DECIMAL(6,2) NULL,
    feels_like_c DECIMAL(6,2) NULL,
    weather_description VARCHAR(255) NULL,
    result_text TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_weather_activity FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
);

CREATE TABLE IF NOT EXISTS gift_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_log_id INT NULL,
    occasion VARCHAR(50) NOT NULL,
    relation_name VARCHAR(50) NOT NULL,
    suggestions TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_gift_activity FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
);

CREATE TABLE IF NOT EXISTS file_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_log_id INT NULL,
    query_text TEXT NOT NULL,
    match_path TEXT NULL,
    action_type VARCHAR(30) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_file_activity FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
);

CREATE TABLE IF NOT EXISTS screenshot_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_log_id INT NULL,
    file_path TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_screenshot_activity FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
);

INSERT INTO users (username) VALUES ('default_user')
ON DUPLICATE KEY UPDATE username = username;

CREATE INDEX idx_user_history_time ON user_history (timestamp);
CREATE INDEX idx_activity_logs_time ON activity_logs (timestamp);
CREATE INDEX idx_mood_logs_mood_id ON mood_logs (mood, id);
CREATE INDEX idx_funfact_logs_id ON funfact_logs (id);
CREATE INDEX idx_app_logs_name_id ON app_logs (app_name, id);
CREATE INDEX idx_search_logs_engine_id ON search_logs (search_engine, id);
CREATE INDEX idx_weather_logs_city_time ON weather_logs (city, timestamp);
CREATE INDEX idx_gift_logs_occasion_relation ON gift_logs (occasion, relation_name);
CREATE INDEX idx_file_logs_action_id ON file_logs (action_type, id);

