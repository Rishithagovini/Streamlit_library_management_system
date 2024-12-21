-- Drop tables if they exist
DROP TABLE IF EXISTS Fines;
DROP TABLE IF EXISTS IssuedBooks;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Books;

-- Create tables
CREATE TABLE Books (
    BookID SERIAL PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255) NOT NULL,
    Publisher VARCHAR(255),
    YearPublished INTEGER,
    Category VARCHAR(100),
    CopiesAvailable INTEGER NOT NULL
);

CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    UserType VARCHAR(50) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20),
    MaxBooksAllowed INTEGER NOT NULL,
    IssueDurationDays INTEGER NOT NULL,
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE IssuedBooks (
    IssueID SERIAL PRIMARY KEY,
    BookID INTEGER REFERENCES Books(BookID),
    UserID INTEGER REFERENCES Users(UserID),
    IssueDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    ReturnDate DATE
);

CREATE TABLE Fines (
    FineID SERIAL PRIMARY KEY,
    IssueID INTEGER REFERENCES IssuedBooks(IssueID),
    FineAmount DECIMAL(10,2) NOT NULL,
    PaymentStatus VARCHAR(20) DEFAULT 'Unpaid',
    PaymentDate DATE
);

-- Insert sample data
INSERT INTO Users (Name, UserType, Email, PhoneNumber, MaxBooksAllowed, IssueDurationDays, Password) VALUES
('Admin', 'Admin', 'admin@library.com', '1234567890', 10, 30, 'admin123'),
('John Doe', 'Student', 'john@example.com', '1234567891', 3, 14, 'pass123');

INSERT INTO Books (Title, Author, Publisher, YearPublished, Category, CopiesAvailable) VALUES
('Python Programming', 'John Smith', 'Tech Books', 2023, 'Programming', 5),
('Data Science Basics', 'Jane Doe', 'Data Press', 2022, 'Data Science', 3);