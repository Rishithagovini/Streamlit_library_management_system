# Library Management System

## Overview
PostgreSQL-based library management system with Streamlit UI for managing books, users, issues, and fines.

## Prerequisites
- Python 
- PostgreSQL
- pip

## Installation
```bash
# Install dependencies
pip install streamlit psycopg2-binary pandas sqlalchemy

# Create database
psql -U <username> -h localhost -p 5432
CREATE DATABASE library_management;

# Import schema
psql -U <username> -h localhost -d library_management -f library_schema.sql
```

## Configuration
Update database credentials in `dbconfig.py`:
```python
user='username'
password='password'
host='localhost'
port='5432'
database='library_management'
```

## Running the Application
```terminal
streamlit run app.py
```

## Features
- User Authentication
- Books Management
- Users Management
- Issue/Return System
- Fine Management

## File Structure
```
├── app.py           # Main application
├── auth.py         # Authentication module
├── dbconfig.py     # Database configuration
└── library_schema.sql  # Database schema
```

## Default Login
```
Email: admin@library.com
Password: admin123
```


