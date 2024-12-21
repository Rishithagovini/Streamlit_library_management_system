"""
Library Management System

Description:
A comprehensive library management system with the following modules:
- Authentication: Handles user login/logout
- Books Management: CRUD operations for books
- Users Management: Student and faculty management
- Issues Management: Book lending and returns
- Fines Management: Late return fine calculation and tracking

Database: PostgreSQL
Frontend: Streamlit
"""


import streamlit as st
import pandas as pd
from dbconfig import DatabasePool
from auth import Auth

# ************Login page rendering**********

def render_login():
    st.title("Library Management System")
    
    col1, col2 = st.columns([2,1])
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if Auth.login_user(email, password):
                    st.success("Login successful!")
                    st.session_state['authenticated'] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

# ************Books management section**********

def show_books():
    st.title("Books Management")
    try:
        tab1, tab2 = st.tabs(["Add Book", "Manage Books"])
        
        with tab1:
            with st.form("add_book"):
                title = st.text_input("Title")
                author = st.text_input("Author")
                publisher = st.text_input("Publisher")
                year = st.number_input("Year Published", min_value=1900, max_value=2024)
                category = st.text_input("Category")
                copies = st.number_input("Copies Available", min_value=1)
                
                if st.form_submit_button("Add Book"):
                    conn = DatabasePool.get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO Books (Title, Author, Publisher, YearPublished, Category, CopiesAvailable)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING BookID;
                    """, (title, author, publisher, year, category, copies))
                    book_id = cur.fetchone()[0]
                    conn.commit()
                    DatabasePool.return_connection(conn)
                    st.success(f"Book added successfully with ID: {book_id}")
                    st.rerun()

        with tab2:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Books ORDER BY BookID")
            books = cur.fetchall()
            DatabasePool.return_connection(conn)
            
            if books:
                df = pd.DataFrame(books, columns=["BookID", "Title", "Author", "Publisher", "Year", "Category", "Copies"])
                st.dataframe(df)
                
                with st.form("delete_book"):
                    book_id = st.number_input("Enter Book ID to Delete", min_value=1)
                    if st.form_submit_button("Delete Book"):
                        conn = DatabasePool.get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM Books WHERE BookID = %s", (book_id,))
                        conn.commit()
                        DatabasePool.return_connection(conn)
                        st.success(f"Book {book_id} deleted successfully!")
                        st.rerun()
            else:
                st.info("No books available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

#************Books management section**********

def show_users():
    st.title("Users Management")
    try:
        tab1, tab2 = st.tabs(["Add User", "Manage Users"])
        
        with tab1:
            with st.form("add_user"):
                name = st.text_input("Name")
                user_type = st.selectbox("User Type", ["Student", "Faculty"])
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                max_books = st.number_input("Max Books Allowed", value=3 if user_type == "Student" else 5)
                issue_duration = st.number_input("Issue Duration (Days)", value=14 if user_type == "Student" else 30)
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Add User"):
                    conn = DatabasePool.get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO Users (Name, UserType, Email, PhoneNumber, MaxBooksAllowed, IssueDurationDays, Password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (name, user_type, email, phone, max_books, issue_duration, password))
                    conn.commit()
                    DatabasePool.return_connection(conn)
                    st.success("User added successfully!")
                    st.rerun()

        with tab2:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users")
            users = cur.fetchall()
            DatabasePool.return_connection(conn)
            
            if users:
                df = pd.DataFrame(users, columns=["UserID", "Name", "Type", "Email", "Phone", "MaxBooks", "Duration", "Password"])
                st.dataframe(df.drop(columns=["Password"]))
                
                with st.form("delete_user"):
                    user_id = st.number_input("Enter User ID to Delete", min_value=1)
                    if st.form_submit_button("Delete User"):
                        conn = DatabasePool.get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
                        conn.commit()
                        DatabasePool.return_connection(conn)
                        st.success(f"User {user_id} deleted successfully!")
                        st.rerun()
            else:
                st.info("No users available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

#************Book issues management section**********


def show_issues():
    st.title("Book Issues")
    try:
        tab1, tab2 = st.tabs(["Issue Book", "Manage Issues"])
         # Issue new book tab
        with tab1:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            # Get available books and users
            cur.execute("SELECT BookID, Title FROM Books WHERE CopiesAvailable > 0")
            available_books = cur.fetchall()
            book_dict = {f"{b[0]} - {b[1]}": b[0] for b in available_books}
            
            cur.execute("SELECT UserID, Name FROM Users")
            users = cur.fetchall()
            user_dict = {f"{u[0]} - {u[1]}": u[0] for u in users}
            
            DatabasePool.return_connection(conn)
            # Book issue form
            with st.form("issue_book"):
                selected_book = st.selectbox("Select Book", options=list(book_dict.keys()) if book_dict else ["No books available"])
                selected_user = st.selectbox("Select User", options=list(user_dict.keys()) if user_dict else ["No users available"])
                issue_date = st.date_input("Issue Date")
                due_date = st.date_input("Due Date")
                
                if st.form_submit_button("Issue Book"):
                    if book_dict and user_dict:
                        conn = DatabasePool.get_connection()
                        cur = conn.cursor()
                        try:
                            book_id = book_dict[selected_book]
                            user_id = user_dict[selected_user]
                            
                            cur.execute("""
                                INSERT INTO IssuedBooks (BookID, UserID, IssueDate, DueDate)
                                VALUES (%s, %s, %s, %s)
                            """, (book_id, user_id, issue_date, due_date))
                            
                            cur.execute("""
                                UPDATE Books 
                                SET CopiesAvailable = CopiesAvailable - 1 
                                WHERE BookID = %s
                            """, (book_id,))
                            
                            conn.commit()
                            st.success("Book issued successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to issue book: {str(e)}")
                        finally:
                            DatabasePool.return_connection(conn)

        with tab2:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT i.IssueID, i.BookID, i.UserID, i.IssueDate, i.DueDate, i.ReturnDate, b.Title, u.Name 
                FROM IssuedBooks i 
                JOIN Books b ON i.BookID = b.BookID 
                JOIN Users u ON i.UserID = u.UserID
                ORDER BY i.IssueDate DESC
            """)
            issues = cur.fetchall()
            DatabasePool.return_connection(conn)
            
            if issues:
                df = pd.DataFrame(issues, columns=["IssueID", "BookID", "UserID", "IssueDate", "DueDate", "ReturnDate", "Title", "User"])
                st.dataframe(df)
                
                with st.form("return_book"):
                    issue_id = st.number_input("Enter Issue ID to Return", min_value=1)
                    if st.form_submit_button("Return Book"):
                        conn = DatabasePool.get_connection()
                        cur = conn.cursor()
                        try:
                            cur.execute("""
                                UPDATE IssuedBooks 
                                SET ReturnDate = CURRENT_DATE 
                                WHERE IssueID = %s
                            """, (issue_id,))
                            
                            cur.execute("""
                                UPDATE Books 
                                SET CopiesAvailable = CopiesAvailable + 1 
                                WHERE BookID = (
                                    SELECT BookID FROM IssuedBooks WHERE IssueID = %s
                                )
                            """, (issue_id,))
                            
                            conn.commit()
                            st.success("Book returned successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to return book: {str(e)}")
                        finally:
                            DatabasePool.return_connection(conn)
            else:
                st.info("No issues available")
    except Exception as e:
        st.error(f"Error: {str(e)}")

#************Fines management section**********


def show_fines():
    st.title("Manage Fines")
    try:
        tab1, tab2 = st.tabs(["Add Fine", "View/Update Fines"])
        
        with tab1:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            
            # Get overdue books
            cur.execute("""
                SELECT i.IssueID, b.Title, u.Name, i.DueDate
                FROM IssuedBooks i 
                JOIN Books b ON i.BookID = b.BookID 
                JOIN Users u ON i.UserID = u.UserID
                WHERE i.ReturnDate IS NULL AND i.DueDate < CURRENT_DATE
                ORDER BY i.DueDate
            """)
            overdue_issues = cur.fetchall()
            issue_dict = {f"ID:{i[0]} - {i[1]} ({i[2]})": i[0] for i in overdue_issues}
            
            with st.form("add_fine"):
                selected_issue = st.selectbox(
                    "Select Overdue Issue",
                    options=list(issue_dict.keys()) if issue_dict else ["No overdue books"]
                )
                fine_amount = st.number_input("Fine Amount", min_value=0.0, step=0.5)
                status = st.selectbox("Payment Status", ["Unpaid", "Paid"])
                payment_date = st.date_input("Payment Date") if status == "Paid" else None
                
                if st.form_submit_button("Add Fine"):
                    if issue_dict:
                        try:
                            issue_id = issue_dict[selected_issue]
                            cur.execute("""
                                INSERT INTO Fines (IssueID, FineAmount, PaymentStatus, PaymentDate)
                                VALUES (%s, %s, %s, %s)
                            """, (issue_id, fine_amount, status, payment_date))
                            conn.commit()
                            st.success("Fine added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add fine: {str(e)}")
            
            DatabasePool.return_connection(conn)

        with tab2:
            conn = DatabasePool.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT f.FineID, b.Title, u.Name, f.FineAmount, f.PaymentStatus, 
                       f.PaymentDate, i.DueDate, i.ReturnDate
                FROM Fines f
                JOIN IssuedBooks i ON f.IssueID = i.IssueID
                JOIN Books b ON i.BookID = b.BookID
                JOIN Users u ON i.UserID = u.UserID
                ORDER BY f.PaymentStatus, f.FineID DESC
            """)
            fines = cur.fetchall()
            
            if fines:
                df = pd.DataFrame(fines, columns=[
                    "FineID", "Book", "Member", "Amount", "Status", 
                    "Payment Date", "Due Date", "Return Date"
                ])
                st.dataframe(df)
                
                with st.form("update_fine"):
                    fine_id = st.number_input("Fine ID", min_value=1)
                    new_status = st.selectbox("New Status", ["Paid", "Unpaid"])
                    payment_date = st.date_input("Payment Date") if new_status == "Paid" else None
                    
                    if st.form_submit_button("Update Fine"):
                        try:
                            cur.execute("""
                                UPDATE Fines 
                                SET PaymentStatus = %s, PaymentDate = %s
                                WHERE FineID = %s
                            """, (new_status, payment_date, fine_id))
                            conn.commit()
                            st.success("Fine updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update fine: {str(e)}")
            else:
                st.info("No fines recorded")
            
            DatabasePool.return_connection(conn)
    except Exception as e:
        st.error(f"Error: {str(e)}")


#*********************************************************************************************Main app rendering with navigation**************************************************************************************************************************************


def render_main_app():
    st.sidebar.title(f"Welcome, {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        Auth.logout_user()
        st.rerun()

    menu = st.sidebar.selectbox("Menu", ["Books", "Users", "Issues","Fines"])
     # Route to appropriate section based on menu selection

    if menu == "Books":
        show_books()
    elif menu == "Users":
        show_users()
    elif menu == "Issues":
        show_issues()
    elif menu == "Fines":
        show_fines()


    

def main():
    DatabasePool.initialize()
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        
    if not st.session_state['authenticated']:
        render_login()
    else:
        render_main_app()

if __name__ == "__main__":
    main()