-- Database creation and setup
CREATE DATABASE librarydb;
ALTER DATABASE librarydb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE librarydb;
SET GLOBAL event_scheduler=ON;

-- Table definitions
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_name VARCHAR(50),
    password VARCHAR(255),
    email VARCHAR(50),
    phone_number VARCHAR(15),
    role ENUM('admin', 'customer') DEFAULT 'customer'
);


CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);


CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(50)
);


CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50)
);


CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50),
    author_id INT,
    genre_id INT,
    publisher_id INT,
    available_copies INT DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id)
);


CREATE TABLE book_author (
    book_id INT,
    author_id INT,
    PRIMARY KEY (book_id, author_id),
    CONSTRAINT fk_ba_book FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ba_author FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    loan_date DATE DEFAULT CURRENT_DATE,
    return_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);


CREATE TABLE memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    membership_type ENUM('standard', 'premium'),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    notification_type ENUM('info', 'warning') DEFAULT 'info',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    amount DECIMAL(5,2),
    status ENUM('unpaid', 'paid') DEFAULT 'unpaid',
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);


CREATE TABLE deleted_users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_name VARCHAR(50),
    password VARCHAR(255),
    email VARCHAR(50),
    phone_number VARCHAR(15)
);


CREATE TABLE logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_type ENUM('loan', 'return', 'donate'),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    rating TINYINT CHECK (rating BETWEEN 1 AND 5),
    review TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Events
DELIMITER $$
CREATE EVENT update_fines
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- Update existing penalties
    UPDATE fines f
    JOIN loans l ON f.loan_id = l.loan_id
    SET f.amount = DATEDIFF(CURDATE(), DATE_ADD(l.loan_date, INTERVAL 14 DAY)) * 5
    WHERE 
        l.return_date IS NULL
        AND CURDATE() > DATE_ADD(l.loan_date, INTERVAL 14 DAY)
        AND f.status = 'unpaid';

    -- Adding new penalties if they don't already exist
    INSERT INTO fines (loan_id, amount, status)
    SELECT 
        l.loan_id,
        DATEDIFF(CURDATE(), DATE_ADD(l.loan_date, INTERVAL 14 DAY)) * 5 AS fine_amount,
        'unpaid'
    FROM loans l
    LEFT JOIN fines f ON l.loan_id = f.loan_id AND f.status = 'unpaid'
    WHERE 
        l.return_date IS NULL
        AND CURDATE() > DATE_ADD(l.loan_date, INTERVAL 14 DAY)
        AND f.loan_id IS NULL;
END$$

DELIMITER ;

-- Procedures

DELIMITER $$

CREATE PROCEDURE register_user(
    IN p_first_name VARCHAR(255),
    IN p_last_name VARCHAR(255),
    IN p_user_name VARCHAR(255),
    IN p_phone_number VARCHAR(20),
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE user_exists INT DEFAULT 0;

    -- Check if a user with the specified name or email already exists
    SELECT COUNT(*)
    INTO user_exists
    FROM users
    WHERE user_name = p_user_name OR email = p_email;

    IF user_exists > 0 THEN
        -- If it exists, terminate the procedure with an error code
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username or email already exists.';
    ELSE
        -- If it does not exist, insert a new user
        INSERT INTO users (first_name, last_name, user_name, phone_number, email, password)
        VALUES (p_first_name, p_last_name, p_user_name, p_phone_number, p_email, p_password);
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE fetch_unrated_books (
    IN p_user_id INT
)
BEGIN
    SELECT DISTINCT b.book_id, b.title
    FROM loans l
    JOIN books b ON l.book_id = b.book_id
    LEFT JOIN ratings r ON l.book_id = r.book_id AND r.user_id = p_user_id
    WHERE l.user_id = p_user_id AND r.rating IS NULL;
END$$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE recommend_books(IN p_user_id INT)
BEGIN
    SELECT b.book_id, b.title, a.first_name, a.last_name, g.genre_name, AVG(r.rating) AS avg_rating
    FROM books b
    LEFT JOIN authors a ON b.author_id = a.author_id
    LEFT JOIN genres g ON b.genre_id = g.genre_id
    LEFT JOIN ratings r ON b.book_id = r.book_id
    LEFT JOIN loans l ON b.book_id = l.book_id AND l.user_id = p_user_id
    JOIN (
        SELECT b.genre_id
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.user_id = p_user_id
        GROUP BY b.genre_id
        ORDER BY COUNT(*) / (SELECT COUNT(*) FROM loans WHERE user_id = p_user_id) DESC
        LIMIT 5
    ) top_genres ON b.genre_id = top_genres.genre_id
    WHERE l.book_id IS NULL
    GROUP BY b.book_id, b.title, a.first_name, a.last_name, g.genre_name
    HAVING AVG(r.rating) >= 3.5
    ORDER BY avg_rating DESC, b.title ASC;

END$$

DELIMITER ;


-- Views
CREATE VIEW all_reviews AS
SELECT 
    u.user_name AS reviewer,
    b.title AS book_title,
    r.rating,
    r.review
FROM ratings r
JOIN users u ON r.user_id = u.user_id
JOIN books b ON r.book_id = b.book_id;

CREATE VIEW standard_user_loans AS
SELECT 
    u.user_id,
    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
    COUNT(l.loan_id) AS total_loans
FROM 
    users u
JOIN 
    memberships m ON u.user_id = m.user_id
JOIN 
    loans l ON u.user_id = l.user_id
WHERE 
    m.membership_type = 'standard'
GROUP BY 
    u.user_id, u.first_name, u.last_name;

CREATE VIEW premium_user_loans AS
SELECT 
    u.user_id,
    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
    COUNT(l.loan_id) AS total_loans
FROM 
    users u
JOIN 
    memberships m ON u.user_id = m.user_id
JOIN 
    loans l ON u.user_id = l.user_id
WHERE 
    m.membership_type = 'premium'
GROUP BY 
    u.user_id, u.first_name, u.last_name;

-- Triggers

DELIMITER $$
CREATE TRIGGER after_user_delete
AFTER DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO deleted_users (user_id, first_name, last_name, user_name, password, email, phone_number)
    VALUES (OLD.user_id, OLD.first_name, OLD.last_name, OLD.user_name, OLD.password, OLD.email, OLD.phone_number);
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER log_loan_operations
AFTER INSERT ON loans
FOR EACH ROW
BEGIN
    INSERT INTO logs (user_id, action_type, description)
    VALUES (NEW.user_id, 'loan', CONCAT('User borrowed the book with ID: ', NEW.book_id));
END$$

DELIMITER $$

DELIMITER $$

CREATE TRIGGER notify_membership
AFTER INSERT ON memberships
FOR EACH ROW
BEGIN
    INSERT INTO notifications (user_id, notification_type, message, created_at)
    VALUES (
        NEW.user_id,
        'info',
        CONCAT('You have a ', NEW.membership_type, ' membership.'),
        NOW()
    );
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER insert_membership
AFTER
INSERT
	ON
	users
FOR EACH ROW
BEGIN
    DECLARE random_membership ENUM('standard',
	'premium');
    
    SET random_membership = CASE
        WHEN FLOOR(1 + (RAND() * 2)) = 1 THEN 'standard'
        ELSE 'premium'
    END;
    
    INSERT INTO memberships (user_id, membership_type, start_date, end_date)
    VALUES (
        NEW.user_id,
        random_membership,
        CURRENT_DATE,
        DATE_ADD(CURRENT_DATE, INTERVAL 1 YEAR)
    );
END$$

DELIMITER ;














