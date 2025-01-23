import tkinter as tk
from tkinter import messagebox, ttk
from mysql.connector import Error
from database import Connection


BG_COLOR = "#1E1E2F"
FG_COLOR = "#E0E0E0"
BUTTON_COLOR = "#3F3C6E"
BUTTON_HOVER_COLOR = "#5A5A8F"

db_connection = Connection()
cursor = db_connection.conn.cursor() if db_connection.conn else None


class App:
    """
    The main application class that handles window transitions.
    """

    def __init__(self, window):
        self.window = window
        self.window.title("App")
        self.window.geometry("400x300")
        self.window.resizable(0, 0)
        self.window.configure(bg=BG_COLOR)
        self.current_frame = None
        self.current_user = None
        self.current_user_id = None
        self.show_main_menu()

    def clear_window(self):
        """Destroy the current active frame."""
        if self.current_frame:
            self.current_frame.destroy()

    def show_main_menu(self):
        """Show the main menu frame."""
        self.clear_window()
        self.window.geometry("400x300")
        self.current_frame = MainMenu(
            self.window, self.show_login, self.show_register, self.window.quit
        )

    def show_login(self):
        """Show the login frame."""
        self.clear_window()
        self.current_frame = LoginWindow(
            self.window, self.show_dashboard, self.show_main_menu
        )

    def show_register(self):
        """Show the register frame."""
        self.clear_window()
        self.current_frame = RegisterWindow(self.window, self.show_main_menu)

    def show_dashboard(self, username, user_id):
        """Show the dashboard frame."""
        self.clear_window()
        self.username = username
        self.current_user_id = user_id
        self.current_frame = Dashboard(
            self.window, username, user_id, self.show_main_menu
        )

    def on_login_success(self, username, user_id):
        """Callback for successful login."""
        self.show_dashboard(username, user_id)


class MainMenu(tk.Frame):
    """
    The main menu frame that shows 'Login', 'Register', and 'Exit' options.
    """

    def __init__(
        self, parent, login_callback, register_callback, exit_callback
    ):
        super().__init__(parent, bg=BG_COLOR)
        self.pack(fill="both", expand=True)

        tk.Label(
            self,
            text="Welcome 📖",
            font=("Roboto", 20, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=20)

        self.create_button("Login", login_callback).pack(pady=10)
        self.create_button("Register", register_callback).pack(pady=10)
        self.create_button("Exit", exit_callback).pack(pady=10)

    def create_button(self, text, command):
        """
        Helper method to create a styled button.
        """
        button = tk.Button(
            self,
            text=text,
            font=("Consolas", 12),
            width=15,
            command=command,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        )
        button.bind(
            "<Enter>", lambda e: button.configure(bg=BUTTON_HOVER_COLOR)
        )
        button.bind("<Leave>", lambda e: button.configure(bg=BUTTON_COLOR))
        return button


class LoginWindow(tk.Frame):
    """
    Frame that allows the user to log in.
    """

    def __init__(self, parent, success_callback, back_callback):
        super().__init__(parent, bg=BG_COLOR)
        self.success_callback = success_callback
        self.back_callback = back_callback
        self.pack(fill="both", expand=True)
        self.render()

    def render(self):
        """
        Renders the login form.
        """
        tk.Label(
            self,
            text="Login 💎",
            font=("Roboto", 20, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=20)

        tk.Label(
            self,
            text="Username:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)
        self.username_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.username_entry.pack(pady=5)

        tk.Label(
            self,
            text="Password:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=10)
        self.password_entry = tk.Entry(
            self, show="*", bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.password_entry.pack(pady=5)

        self.create_button("Login", self.login).pack(pady=5)
        self.create_button("Back", self.back_callback).pack(pady=5)

    def create_button(self, text, command):
        """
        Helper method to create a styled button.
        """
        button = tk.Button(
            self,
            text=text,
            font=("Consolas", 10),
            width=10,
            command=command,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        )
        button.bind(
            "<Enter>", lambda e: button.configure(bg=BUTTON_HOVER_COLOR)
        )
        button.bind("<Leave>", lambda e: button.configure(bg=BUTTON_COLOR))
        return button

    def login(self):
        """
        Handles the login attempt, verifies against the database.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror(
                "Login Failed", "Username and password are required."
            )
            return

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return

        try:
            query = "SELECT user_id, password FROM users WHERE user_name = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result and result[1] == password:
                user_id = result[0]
                messagebox.showinfo("Login Success", "Welcome!")
                self.success_callback(username, user_id)
            else:
                messagebox.showerror(
                    "Login Failed", "Invalid username or password."
                )
        except Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")


class RegisterWindow(tk.Frame):
    """
    Frame that allows a new user to register.
    """

    def __init__(self, parent, back_callback):
        super().__init__(parent, bg=BG_COLOR)
        self.back_callback = back_callback
        self.pack(fill="both", expand=True)
        self.render()

    def render(self):
        """
        Renders the registration form.
        """
        self.master.geometry("400x380")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        tk.Label(
            self,
            text="Register 📝",
            font=("Roboto", 20, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # Name
        tk.Label(
            self,
            text="Name:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.name_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.name_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # Last name
        tk.Label(
            self,
            text="Last name:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.last_name_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.last_name_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        # Username
        tk.Label(
            self,
            text="Username:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.username_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.username_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")

        # Phone Number
        tk.Label(
            self,
            text="Phone Number:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.phone_number_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.phone_number_entry.grid(
            row=4, column=1, pady=5, padx=10, sticky="w"
        )

        # Email
        tk.Label(
            self,
            text="Email:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.email_entry = tk.Entry(
            self, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.email_entry.grid(row=5, column=1, pady=5, padx=10, sticky="w")

        # Password
        tk.Label(
            self,
            text="Password:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=6, column=0, sticky="e", padx=10, pady=5)
        self.password_entry = tk.Entry(
            self, show="*", bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.password_entry.grid(row=6, column=1, pady=5, padx=10, sticky="w")

        # Confirm password
        tk.Label(
            self,
            text="Confirm Password:",
            font=("Roboto", 10, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).grid(row=7, column=0, sticky="e", padx=10, pady=5)
        self.confirm_password_entry = tk.Entry(
            self, show="*", bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat"
        )
        self.confirm_password_entry.grid(
            row=7, column=1, pady=5, padx=10, sticky="w"
        )

        # Buttons
        self.create_button("Register", self.register).grid(
            row=8, column=0, columnspan=1, pady=20, padx=0, sticky="e"
        )
        self.create_button("Back", self.back_callback).grid(
            row=8, column=1, columnspan=1, pady=20, padx=10, sticky="w"
        )

    def create_button(self, text, command):
        """
        Helper method to create a styled button.
        """
        button = tk.Button(
            self,
            text=text,
            font=("Consolas", 10),
            width=10,
            command=command,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        )
        button.bind(
            "<Enter>", lambda e: button.configure(bg=BUTTON_HOVER_COLOR)
        )
        button.bind("<Leave>", lambda e: button.configure(bg=BUTTON_COLOR))
        return button

    def register(self):
        """
        Handles registration logic and inserts a new user into the DB.
        """
        name = self.name_entry.get().title()
        last_name = self.last_name_entry.get().title()
        username = self.username_entry.get()
        phone_number = self.phone_number_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate
        if not all(
            [name, last_name, username, password, confirm_password, email]
        ):
            messagebox.showerror(
                "Registration Failed", "All fields are required."
            )
            return

        if password != confirm_password:
            messagebox.showerror(
                "Registration Failed", "Passwords do not match."
            )
            return

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return

        try:
            # call the register procedure
            cursor.callproc(
                "register_user",
                (name, last_name, username, phone_number, email, password),
            )
            db_connection.conn.commit()

            messagebox.showinfo(
                "Registration Success", "You have registered successfully!"
            )
            self.back_callback()

        except Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")


class Dashboard(tk.Frame):
    """
    The user dashboard frame where users can issue/return/donate books
    and check fines/notifications.
    """

    def __init__(self, parent, username, user_id, logout_callback):
        super().__init__(parent, bg=BG_COLOR)
        self.username = username
        self.user_id = user_id
        self.logout_callback = logout_callback
        self.pack(fill="both", expand=True)
        self.render()

    def render(self):
        """
        Renders the dashboard UI with buttons and notifications.
        """
        self.master.geometry("750x450")
        self.master.title("Dashboard")

        top_bar = tk.Frame(self, bg=BUTTON_COLOR, height=60)
        top_bar.pack(side="top", fill="x")

        tk.Label(
            top_bar,
            text=f"Welcome, {self.username}!",
            font=("Roboto", 20, "bold"),
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
        ).pack(side="left", padx=20, pady=15)

        logout_button = tk.Button(
            top_bar,
            text="Log Out",
            font=("Roboto", 10),
            command=self.logout_callback,
            bg=BUTTON_HOVER_COLOR,
            fg=FG_COLOR,
            activebackground="#3B4252",
            activeforeground=FG_COLOR,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
        )
        logout_button.pack(side="right", padx=20, pady=10)

        content_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        actions_frame = tk.Frame(content_frame, bg=BG_COLOR)
        actions_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        tk.Label(
            actions_frame,
            text="Actions",
            font=("Roboto", 16, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        def create_button(root, text, command):
            button = tk.Button(
                root,
                text=text,
                font=("Consolas", 12),
                width=15,
                command=command,
                bg=BUTTON_COLOR,
                fg=FG_COLOR,
                activebackground=BUTTON_HOVER_COLOR,
                activeforeground=FG_COLOR,
                relief="flat",
            )
            button.bind(
                "<Enter>", lambda e: button.configure(bg=BUTTON_HOVER_COLOR)
            )
            button.bind("<Leave>", lambda e: button.configure(bg=BUTTON_COLOR))
            return button

        create_button(actions_frame, "Issue Book", self.issue_book).grid(
            row=1, column=0, pady=10
        )
        create_button(actions_frame, "Return Book", self.return_book).grid(
            row=2, column=0, pady=10
        )
        create_button(actions_frame, "Donate Book", self.donate_book).grid(
            row=3, column=0, pady=10
        )
        create_button(actions_frame, "Fines", self.show_fines).grid(
            row=4, column=0, pady=10
        )
        create_button(actions_frame, "Recommendations", self.show_recommendations).grid(
            row=5, column=0, pady=10
        )

        reviews_frame = tk.Frame(content_frame, bg=BG_COLOR, relief="flat")
        reviews_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)
        tk.Label(
            reviews_frame,
            text="Reviews",
            font=("Roboto", 16, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        create_button(reviews_frame, "Add Review", self.review_menu).grid(
            row=1, column=0, pady=10
        )
        create_button(reviews_frame, "Browse Reviews", self.browse_menu).grid(
            row=2, column=0, pady=10
        )

        notifications_frame = tk.Frame(
            content_frame, bg=BG_COLOR, bd=1, relief="flat"
        )
        notifications_frame.grid(row=0, column=2, sticky="nw", padx=20, pady=5)
        tk.Label(
            notifications_frame,
            text="Notifications",
            font=("Roboto", 16, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR,
            pady=5,
        ).pack(anchor="nw")
        self.display_notifications(notifications_frame)


    def show_recommendations(self):
        """
        Open a new window to show book recommendations for the current user.
        """
        recom_window = tk.Toplevel(self)
        recom_window.title("Recommendations")
        recom_window.geometry("400x400")
        recom_window.resizable(0, 0)
        recom_window.configure(bg=BG_COLOR)

        tk.Label(
            recom_window,
            text="Recommendations",
            font=("Roboto", 18, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=10)

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return

        try:
            cursor.callproc('recommend_books', (self.user_id,))

            result = cursor.stored_results()
            recommendations = []
            for res in result:
                recommendations.extend(res.fetchall())

            canvas = tk.Canvas(recom_window, bd=0, highlightthickness=0)
            scrollbar = tk.Scrollbar(recom_window, orient="vertical", command=canvas.yview, bd=0, highlightthickness=0)
            canvas.configure(yscrollcommand=scrollbar.set)

            recommendation_frame = tk.Frame(canvas, bg=BG_COLOR)

            canvas.create_window((0, 0), window=recommendation_frame, anchor="nw")
            
            if not recommendations:
                tk.Label(
                    recommendation_frame,
                    text="No recommendations available.",
                    font=("Consolas", 12),
                    fg=FG_COLOR,
                    bg=BG_COLOR,
                ).pack(pady=20)
            else:
                for book in recommendations:
                    book_id, title, author_first_name, author_last_name, genre_name, avg_rating = book
                    tk.Label(
                        recommendation_frame,
                        text=f"{title} by {author_first_name} {author_last_name} "
                            f"(Genre: {genre_name}, Rating: {avg_rating:.2f})",
                        font=("Consolas", 10),
                        fg=FG_COLOR,
                        bg=BG_COLOR,
                        wraplength=380,
                        justify="left",
                    ).pack(pady=5, anchor="w")

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            recommendation_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"), bg=BG_COLOR, bd=0)

        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch recommendations: {e}")



    # change query after adding self.user_id --------------------
    def show_fines(self):
        """
        Fetch and display the user's fines.
        """
        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return

        try:
            query = "SELECT user_id FROM users WHERE user_name = %s"
            cursor.execute(query, (self.username,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                query = (
                    "SELECT amount, status FROM fines "
                    "WHERE loan_id IN (SELECT loan_id FROM loans "
                    "WHERE user_id = %s)"
                )
                cursor.execute(query, (user_id,))
                fines = cursor.fetchall()

                if fines:
                    fines_message = "\n".join(
                        f"Amount: {fine[0]} | Status: {fine[1]}"
                        for fine in fines
                    )
                    messagebox.showinfo(
                        "Fines Details", f"Your fines:\n{fines_message}"
                    )
                else:
                    messagebox.showinfo("Fines Details", "You have no fines.")
            else:
                messagebox.showerror("Error", "User not found.")
        except Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def fetch_notifications(self):
        """
        Fetch user notifications from the database.
        """
        if cursor is None:
            return []
        query = (
            "SELECT notification_type, message "
            "FROM notifications WHERE user_id = %s"
        )
        cursor.execute(query, (self.user_id,))
        return cursor.fetchall()

    def display_notifications(self, parent):
        """
        Display notifications in the GUI.
        """
        notifications = self.fetch_notifications()
        if not notifications:
            tk.Label(
                parent,
                text="No new notifications.",
                font=("Roboto", 12),
                bg=FG_COLOR,
                fg="#4C566A",
                wraplength=300,
            ).pack(anchor="w", padx=10, pady=10)
            return

        for notification in notifications:
            notification_type, message = notification
            tk.Label(
                parent,
                text=f"• {message}",
                font=("Roboto", 10),
                bg=BG_COLOR,
                fg=FG_COLOR,
                wraplength=300,
                justify="left",
            ).pack(anchor="w", padx=10, pady=5)

    def issue_book(self):
        """
        Open a new window allowing the user to issue a book.
        """
        issue_window = tk.Toplevel(self)
        issue_window.title("Issue Book")
        issue_window.geometry("400x400")
        issue_window.resizable(0, 0)
        issue_window.configure(bg=BG_COLOR)

        tk.Label(
            issue_window,
            text="Issue Book",
            font=("Roboto", 18, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=10)

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return

        try:
            cursor.execute(
                """
                SELECT book_id, title, available_copies
                FROM books
                WHERE available_copies > 0
                """
            )
            available_books = cursor.fetchall()

            if not available_books:
                tk.Label(
                    issue_window,
                    text="No books available for issuing.",
                    font=("Consolas", 12),
                    fg=FG_COLOR,
                    bg=BG_COLOR,
                ).pack(pady=20)
                return

        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching books: {e}")
            return

        book_options = [
            f"{book[1]} (Available: {book[2]})" for book in available_books
        ]
        book_var = tk.StringVar(issue_window)
        #book_var.set(book_options[0])

        tk.Label(
            issue_window,
            text="Select a book to issue:",
            font=("Consolas", 12),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        dropdown = ttk.Combobox(issue_window, textvariable=book_var, values=book_options)
        dropdown.config(
            font=("Roboto", 12),
            width=40,
            background=BG_COLOR,
            foreground=BG_COLOR,
        )
        dropdown.pack(pady=10)
    

        def submit_issue():
            selected_index = book_options.index(book_var.get())
            book_id = available_books[selected_index][0]

            try:
                cursor.execute(
                    "INSERT INTO loans (user_id, book_id, loan_date) "
                    "VALUES (%s, %s, CURDATE())",
                    (self.user_id, book_id),
                )
                db_connection.conn.commit()

                cursor.execute(
                    "UPDATE books "
                    "SET available_copies = available_copies - 1 "
                    "WHERE book_id = %s",
                    (book_id,),
                )
                db_connection.conn.commit()

                messagebox.showinfo("Success", "Book issued successfully!")
                issue_window.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Could not issue book: {ex}")

        tk.Button(
            issue_window,
            text="Issue",
            font=("Consolas", 12),
            width=15,
            command=submit_issue,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        ).pack(pady=20)

    def donate_book(self):
        """
        Open a new window allowing the user to donate a book.
        """
        donate_window = tk.Toplevel(self)
        donate_window.title("Donate Book")
        donate_window.geometry("400x350")
        donate_window.resizable(0, 0)
        donate_window.configure(bg=BG_COLOR)

        tk.Label(
            donate_window,
            text="Donate Book Form",
            font=("Roboto", 18, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        def create_label(text, font_size):
            return tk.Label(
                donate_window,
                text=text,
                font=("Consolas", font_size),
                fg=FG_COLOR,
                bg=BG_COLOR,
            )

        def create_entry():
            return tk.Entry(
                donate_window,
                font=("Consolas", 10),
                bg=BUTTON_COLOR,
                fg=FG_COLOR,
                relief="flat",
            )

        create_label("Title:", 12).pack(pady=5)
        title_entry = create_entry()
        title_entry.pack(pady=5)

        create_label("Author:", 12).pack(pady=5)
        author_entry = create_entry()
        author_entry.pack(pady=5)

        create_label("Genre:", 12).pack(pady=5)
        genre_entry = create_entry()
        genre_entry.pack(pady=5)

        create_label("Publisher:", 12).pack(pady=5)
        publisher_entry = create_entry()
        publisher_entry.pack(pady=5)

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            donate_window.destroy()
            return

        def submit_donation():
            title = title_entry.get().title()
            author = author_entry.get().title()
            genre = genre_entry.get().title()
            publisher = publisher_entry.get().title()

            if not all([title, author, genre, publisher]):
                messagebox.showwarning(
                    "Input Error", "Please fill in all fields."
                )
                return

            try:
                # Check for author
                first_name, last_name = author.split()[0], author.split()[-1]
                cursor.execute(
                    "SELECT author_id FROM authors "
                    "WHERE first_name = %s AND last_name = %s",
                    (first_name, last_name),
                )
                author_id = cursor.fetchone()

                # If author not found, insert new
                if not author_id:
                    cursor.execute(
                        "INSERT INTO authors (first_name, last_name) "
                        "VALUES (%s, %s)",
                        (first_name, last_name),
                    )
                    db_connection.conn.commit()
                    author_id = cursor.lastrowid
                else:
                    author_id = author_id[0]

                # Check for genre
                cursor.execute(
                    "SELECT genre_id FROM genres WHERE genre_name = %s",
                    (genre,),
                )
                genre_id = cursor.fetchone()

                # If genre not found, insert new
                if not genre_id:
                    cursor.execute(
                        "INSERT INTO genres (genre_name) VALUES (%s)",
                        (genre,),
                    )
                    db_connection.conn.commit()
                    genre_id = cursor.lastrowid
                else:
                    genre_id = genre_id[0]

                # Check for publisher
                cursor.execute(
                    "SELECT publisher_id FROM publishers "
                    "WHERE publisher_name = %s",
                    (publisher,),
                )
                publisher_id = cursor.fetchone()

                # If publisher not found, insert new
                if not publisher_id:
                    cursor.execute(
                        "INSERT INTO publishers (publisher_name) VALUES (%s)",
                        (publisher,),
                    )
                    db_connection.conn.commit()
                    publisher_id = cursor.lastrowid
                else:
                    publisher_id = publisher_id[0]

                # Insert new book
                cursor.execute(
                    "INSERT INTO books (title, author_id, genre_id, publisher_id) "
                    "VALUES (%s, %s, %s, %s)",
                    (title, author_id, genre_id, publisher_id),
                )
                db_connection.conn.commit()

                messagebox.showinfo(
                    "Success", f"Book '{title}' donated successfully!"
                )
                donate_window.destroy()
            except Error as err:
                messagebox.showerror("Error", f"Error: {err}")
            except ValueError:
                # If user enters an author name with only one part
                messagebox.showwarning(
                    "Input Error",
                    "Please enter author name in 'FirstName LastName' format.",
                )

        tk.Button(
            donate_window,
            text="Donate",
            font=("Consolas", 12),
            width=15,
            command=submit_donation,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        ).pack()

    def return_book(self):
        """
        Open a new window allowing the user to return a previously issued book.
        """
        return_window = tk.Toplevel(self)
        return_window.title("Return Book")
        return_window.geometry("400x350")
        return_window.resizable(0, 0)
        return_window.configure(bg=BG_COLOR)

        tk.Label(
            return_window,
            text="Return Book",
            font=("Roboto", 18, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=10)

        if cursor is None:
            messagebox.showerror(
                "Database Error", "No valid database connection found."
            )
            return_window.destroy()
            return

        try:
            cursor.execute(
                """
                SELECT loans.loan_id, books.title, loans.loan_date
                FROM loans
                INNER JOIN books ON loans.book_id = books.book_id
                WHERE loans.user_id = %s AND loans.return_date IS NULL
                """,
                (self.user_id,),
            )
            books_to_return = cursor.fetchall()

            if not books_to_return:
                tk.Label(
                    return_window,
                    text="No books to return.",
                    font=("Consolas", 12),
                    fg=FG_COLOR,
                    bg=BG_COLOR,
                ).pack(pady=20)
                return

        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching books: {e}")
            return

        book_options = [
            f"{book[1]} (Loaned on: {book[2]})" for book in books_to_return
        ]
        book_var = tk.StringVar(return_window)
        book_var.set(book_options[0])

        tk.Label(
            return_window,
            text="Select a book to return:",
            font=("Consolas", 12),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        dropdown = tk.OptionMenu(return_window, book_var, *book_options)
        dropdown.config(
            width=40,
            font=("Roboto", 12),
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )

        dropdown.pack(pady=10)

        def submit_return():
            selected_index = book_options.index(book_var.get())
            loan_id = books_to_return[selected_index][0]

            try:
                cursor.execute(
                    "SELECT book_id FROM loans WHERE loan_id = %s",
                    (loan_id,),
                )
                book_id = cursor.fetchone()[0]

                cursor.execute(
                    "UPDATE loans SET return_date = CURDATE() "
                    "WHERE loan_id = %s",
                    (loan_id,),
                )

                cursor.execute(
                    "UPDATE books SET available_copies = available_copies + 1 "
                    "WHERE book_id = %s",
                    (book_id,),
                )

                db_connection.conn.commit()

                messagebox.showinfo("Success", "Book returned successfully!")
                return_window.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Could not return book: {ex}")

        tk.Button(
            return_window,
            text="Return",
            font=("Consolas", 12),
            width=15,
            command=submit_return,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        ).pack(pady=20)

    def review_menu(self):
        def fetch_unrated_books():
            try:
                cursor.callproc("fetch_unrated_books", [self.user_id])
                books = []
                for result in cursor.stored_results():
                    books = result.fetchall()
                return books
            except Exception as e:
                messagebox.showerror(
                    "Database Error", f"Error fetching books: {e}"
                )
                return []

        def submit_review():
            """Submit the review and rating to the database."""
            selected_title = book_var.get()
            book_id = book_mapping.get(selected_title)
            review_text = review_entry.get()
            rating = rating_var.get()

            if not book_id or not rating:
                messagebox.showerror(
                    "Input Error", "Please select a book and provide a rating."
                )
                return

            try:
                query = """
                    INSERT INTO ratings (user_id, book_id, rating, review)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(
                    query, (self.user_id, book_id, rating, review_text)
                )
                db_connection.conn.commit()
                messagebox.showinfo("Success", "Review submitted successfully!")
                review_window.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Database Error", f"Error submitting review: {e}"
                )

        books = fetch_unrated_books()
        if not books:
            messagebox.showinfo("No Books", "No unrated books available.")
            return

        book_mapping = {book[1]: book[0] for book in books}

        review_window = tk.Toplevel(self)
        review_window.title("Add Review")
        review_window.geometry("400x350")
        review_window.resizable(0, 0)
        review_window.configure(bg=BG_COLOR)

        tk.Label(
            review_window,
            text="Review Book",
            font=("Roboto", 18, "bold"),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=10)

        tk.Label(
            review_window,
            text="Select Book:",
            font=("Roboto", 14),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        book_var = tk.StringVar()
        book_menu = tk.OptionMenu(review_window, book_var, *book_mapping.keys())
        book_menu.config(
            width=40,
            font=("Roboto", 12),
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )

        book_menu.pack(pady=5)

        tk.Label(
            review_window,
            text="Write your review:",
            font=("Roboto", 14),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        review_entry = tk.Entry(
            review_window, bg=BUTTON_COLOR, fg=FG_COLOR, relief="flat", width=50
        )
        review_entry.pack(pady=5)

        tk.Label(
            review_window,
            text="Rate:",
            font=("Roboto", 14),
            fg=FG_COLOR,
            bg=BG_COLOR,
        ).pack(pady=5)

        rating_var = tk.IntVar(value=0)
        for i in range(1, 6):
            tk.Radiobutton(
                review_window,
                text=i,
                variable=rating_var,
                value=i,
                font=("Roboto", 10, "bold"),
                bg=BG_COLOR,
                fg=FG_COLOR,
            ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            review_window,
            text="Submit",
            font=("Consolas", 12),
            command=submit_review,
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=FG_COLOR,
            relief="flat",
        ).pack()

    def browse_menu(self):
        """Displays a window for browsing reviews."""

        def fetch_reviews():
            """Fetches all reviews from the `all_reviews` view in the database."""
            try:
                query = "SELECT * FROM all_reviews"
                cursor.execute(query)
                return cursor.fetchall()
            except Exception as e:
                messagebox.showerror(
                    "Database Error", f"Error fetching reviews: {e}"
                )
                return []

        reviews = fetch_reviews()

        if not reviews:
            messagebox.showinfo("No Data", "No reviews found.")
            return

        browse_window = tk.Toplevel(self)
        browse_window.title("Browse Reviews")
        browse_window.geometry("700x400")
        browse_window.configure(bg=BG_COLOR)

        tk.Label(
            browse_window,
            text="All Reviews",
            font=("Roboto", 18, "bold"),
            bg=BG_COLOR,
            fg=FG_COLOR,
        ).pack(pady=10)

        columns = ("Reviewer", "Book Title", "Rating", "Review")
        tree = ttk.Treeview(
            browse_window, columns=columns, show="headings", height=15
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.column("Reviewer", width=150)
        tree.column("Book Title", width=200)
        tree.column("Review", width=300)

        for review in reviews:
            tree.insert("", "end", values=review)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(
            browse_window,
            text="Close",
            command=browse_window.destroy,
            bg=BG_COLOR,
            fg=FG_COLOR,
            activebackground=BUTTON_COLOR,
            activeforeground=BUTTON_HOVER_COLOR,
        ).pack(pady=10)


if __name__ == "__main__":
    window = tk.Tk()
    app = App(window)
    window.mainloop()
