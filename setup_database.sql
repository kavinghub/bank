-- ═══════════════════════════════════════════════════════════════
-- VaultX Bank Management System — Database Setup Script
-- Run this in MySQL before starting the Django app.
-- ═══════════════════════════════════════════════════════════════

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS bank_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bank_db;

-- 2. Users Table
CREATE TABLE IF NOT EXISTS bank_users (
    id             BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    name           VARCHAR(150)      NOT NULL,
    email          VARCHAR(254)      NOT NULL UNIQUE,
    phone          VARCHAR(20)       NOT NULL,
    account_number VARCHAR(20)       NOT NULL UNIQUE,
    password_hash  VARCHAR(255)      NOT NULL,   -- bcrypt hash
    pin_hash       VARCHAR(255)      NOT NULL,   -- bcrypt hash
    balance        DECIMAL(15, 2)    NOT NULL DEFAULT 0.00,
    created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_email          (email),
    INDEX idx_account_number (account_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Transactions Table
CREATE TABLE IF NOT EXISTS bank_transactions (
    id          BIGINT UNSIGNED    NOT NULL AUTO_INCREMENT,
    user_id     BIGINT UNSIGNED    NOT NULL,
    type        ENUM('deposit','withdraw') NOT NULL,
    amount      DECIMAL(15, 2)     NOT NULL,
    date_time   DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255)       NOT NULL DEFAULT '',
    PRIMARY KEY (id),
    INDEX idx_user_id  (user_id),
    INDEX idx_datetime (date_time),
    CONSTRAINT fk_txn_user
        FOREIGN KEY (user_id)
        REFERENCES bank_users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Django session table (created by migrate, shown here for reference)
-- django_session is managed by Django's migrate command — do not create manually.

-- ── Verification queries ─────────────────────────────────────────
-- Run these after setup to confirm everything is correct:
--
-- SHOW TABLES;
-- DESCRIBE bank_users;
-- DESCRIBE bank_transactions;
