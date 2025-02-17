# 📚 Library Management System

The Library Management System project was developed as part of the Database Systems course at university. The main goal of the project was to design, implement, and integrate a relational database with an application written in Python. The database was created in the MariaDB environment, while Python served as the tool for communication with the database and handling the application logic.

![menu](assets/menu.gif)
---
## 🗺️ Diagram
![diagram](assets/diagram.png)
---
## 📋 Functionality

### 1. **User Registration and Login**

- Registration and verification of unique users.
- Automatic membership assignment (standard or premium).

### 2. **Book and Loan Management**

- Handling book loans, returns, and donations. 
- Automatic fine calculation for overdue books.

### 3. **Viewing and Adding Reviews**

- Adding ratings (1–5) and book reviews.
- The `all_reviews` view displays all user reviews.

### 4. **Book Recommendation**
The `recommend_books` procedure generates book recommendations for the user based on ratings, loan history, and genre preferences.

- Selects the top 5 genres by weight
   ```sql
   SELECT b.genre_id
   FROM loans l
   JOIN books b ON l.book_id = b.book_id
   WHERE l.user_id = p_user_id
   GROUP BY b.genre_id
   ORDER BY COUNT(*) / (SELECT COUNT(*) FROM loans WHERE user_id = p_user_id) DESC
   LIMIT 5```
   
---

## 📄 Key Project Elements

### Database Tables:

- **users**: user information
- **books**: book management
- **loans**: handling book loans
- **fines**: fine calculation
- **ratings**: user ratings and reviews

### Procedures:

- **`register_user`**: register a new user
- **`fetch_unrated_books`**: list of borrowed books not yet rated
- **`recommend_books`**: book recommendation algorithm

### Events:

- **`update_fines`**: automatic fine calculation for overdue books

### Views:

- **`all_reviews`**: displays user reviews and ratings
- **`standard_user_loans`** i **`premium_user_loans`**: loan statistics for standard and premium users

---
## 🛠️ Technical Requirements

1. **MariaDB 10.3 or newer**

2. **Python 3.8 or newer**
   - Key libraries:
     - `mysql-connector-python`
     - `tkinter`
