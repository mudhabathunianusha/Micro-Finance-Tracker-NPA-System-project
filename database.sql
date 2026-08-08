CREATE TABLE borrowers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    village TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_id INTEGER NOT NULL,
    principal_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    tenure_months INTEGER NOT NULL,
    loan_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    outstanding_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);

CREATE TABLE repayments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date TEXT NOT NULL,
    mode TEXT DEFAULT 'Cash',
    FOREIGN KEY (loan_id) REFERENCES loans(id)
);

INSERT INTO borrowers (name, phone, village) VALUES
('Ravi Kumar', '9876543210', 'Karnal'),
('Meena Devi', '9123456780', 'Panipat'),
('Amit Singh', '9988776655', 'Hisar'),
('Sonia Rani', '9765432109', 'Faridabad');

INSERT INTO loans (borrower_id, principal_amount, interest_rate, tenure_months, loan_date, due_date, outstanding_amount, status) VALUES
(1, 50000, 12, 12, '2025-01-15', '2025-12-15', 42000, 'Active'),
(2, 75000, 14, 18, '2025-02-10', '2026-08-10', 61000, 'Active'),
(3, 120000, 18, 24, '2024-10-01', '2026-10-01', 98000, 'NPA'),
(4, 90000, 15, 12, '2025-03-20', '2026-03-20', 0, 'Closed');

INSERT INTO repayments (loan_id, amount, payment_date, mode) VALUES
(1, 8000, '2025-03-05', 'Bank Transfer'),
(2, 14000, '2025-04-18', 'Cash'),
(3, 22000, '2025-06-22', 'UPI'),
(4, 90000, '2025-05-15', 'Bank Transfer');

SELECT * FROM borrowers;
SELECT * FROM loans;
SELECT * FROM repayments;

SELECT COUNT(*) AS total_borrowers FROM borrowers;
SELECT SUM(principal_amount) AS total_portfolio FROM loans;
SELECT SUM(outstanding_amount) AS outstanding FROM loans;
SELECT SUM(amount) AS total_recovery FROM repayments;
SELECT COUNT(*) AS npa_count FROM loans WHERE status = 'NPA';
