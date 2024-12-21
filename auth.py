"""
Authentication Module

Description:
Handles user authentication and session management for the library system.
Functions:
- login_user: Validates credentials and creates session
- logout_user: Clears session data
- check_authentication: Verifies user session status
"""



import streamlit as st
from dbconfig import DatabasePool

class Auth:
    """
   Handles authentication and session management operations.
   """
    @staticmethod
    def login_user(email, password):

        # Authenticates user with provided credentials and initializes session.

        conn = DatabasePool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT UserID, Name, UserType 
                FROM Users 
                WHERE Email = %s AND Password = %s
            """, (email, password))
            user = cur.fetchone()
            
            if user:
                st.session_state['user_id'] = user[0]
                st.session_state['user_name'] = user[1]
                st.session_state['user_type'] = user[2]
                st.session_state['authenticated'] = True
                return True
            return False
        finally:
            cur.close()
            DatabasePool.return_connection(conn)

    @staticmethod
    def logout_user():

        # Logs out user by clearing session state.
        for key in ['user_id', 'user_name', 'user_type', 'authenticated']:
            if key in st.session_state:
                del st.session_state[key]