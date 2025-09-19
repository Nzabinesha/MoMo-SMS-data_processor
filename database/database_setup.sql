#Create Tables

CREATE TABLE Users (
	User_id VARCHAR(20) PRIMARY KEY,
	PhoneNumber VARCHAR(20) UNIQUE,
	AccountType VARCHAR(20),
	RegisteredDate DATETIME,
	FullName VARCHAR(50)
);

CREATE TABLE Transaction_Categories (
	CategoryID VARCHAR(50) PRIMARY KEY,
	CategoryName VARCHAR(100),
	Description TEXT
);

CREATE TABLE Tags (
	TagID VARCHAR(50) PRIMARY KEY,
	TagName VARCHAR(100)
);

CREATE TABLE Transactions (
	TransactionID VARCHAR(50) PRIMARY KEY,
	Date DATETIME,
	Amount INT,
	SenderUserId VARCHAR(50),
	ReceiverUserId VARCHAR(50),
	CategoryID VARCHAR(50),
	Status VARCHAR(50),
	FOREIGN KEY (SenderUserId) REFERENCES Transaction_Categories(CategoryID),
	FOREIGN KEY (CategoryID) REFERENCES System_Logs(TransactionId)
);

CREATE TABLE Transaction_Tags (
	TransactionID VARCHAR(50) FOREIGN KEY,
	TagID VARCHAR(50) FOREIGN KEY,
	FOREIGN KEY (TransactionId) REFERENCES Transactions(TransactionID),
	FOREIGN KEY (TagID) REFERENCES Tags(TagID)
);

CREATE TABLE System_Logs (
	LogID VARCHAR(50) PRIMARY KEY,
	TimeStamp DATETIME,
	TransactionId VARCHAR(50),
	Message TEXT,
	ErrorDetails TEXT,
);

#Indexes for performance optimisation

CREATE INDEX users_phone ON Users(PhoneNumber);
CREATE INDEX category_name ON Transaction_Categories(CategoryName);
CREATE INDEX tag_name ON Tags(TagName);

CREATE INDEX transactions_sender ON Transactions(SenderUserId);
CREATE INDEX transactions_receiver ON Transactions(ReceiverUserId);
CREATE INDEX transactions_category ON Transactions(CategoryID);
CREATE INDEX transactions_date ON Transactions(Date);
CREATE INDEX transactions_status ON Transactions(Status);

CREATE INDEX tags_transaction ON Transaction_Tags(TransactionID);
CREATE INDEX tags_tag ON Transaction_Tags(TagID);

CREATE INDEX logs_transaction ON System_Logs(TransactionID);
CREATE INDEX logs_timestamp ON System_Logs(Timestamp);

#Insert test data

INSERT INTO Users (User_id, PhoneNumber, Account_Type, Registered_Date, Full_Name) VALUES
('U001', '250781234567', 'Personal', '2024-01-10 09:30:00', 'Alice Mukamana'),
('U002', '250782345678', 'Business', '2024-02-15 14:20:00', 'John Kamali'),
('U003', '250783456789', 'Personal', '2024-03-01 08:00:00', 'Grace Niyonsaba'),
('U004', '250784567890', 'Personal', '2024-03-20 11:45:00', 'Eric Habimana'),
('U005', '250785678901', 'Business', '2024-04-05 17:15:00', 'Claudine Uwase');

-- Transaction Categories
INSERT INTO Transaction_Categories (CategoryID, CategoryName, Description) VALUES
('C001', 'Airtime Purchase', 'Buying mobile airtime'),
('C002', 'Money Transfer', 'Sending money between users'),
('C003', 'Bill Payment', 'Paying utility or service bills'),
('C004', 'Merchant Payment', 'Paying for goods/services at merchants'),
('C005', 'Cash Withdrawal', 'Withdrawing cash from an agent');

-- Tags
INSERT INTO Tags (TagID, TagName) VALUES
('T001', 'Urgent'),
('T002', 'Recurring'),
('T003', 'Family'),
('T004', 'Work'),
('T005', 'Entertainment');

-- Transactions
INSERT INTO Transactions (TransactionID, Date, Amount, SenderUserId, ReceiverUserId, CategoryID, Status) VALUES
('Tr001', '2024-05-01 10:00:00', 5000.00, 'U001', 'U002', 'C002', 'Success'),
('Tr002', '2024-05-02 12:30:00', 2000.00, 'U003', 'U004', 'C001', 'Success'),
('Tr003', '2024-05-03 15:45:00', 15000.00, 'U002', 'U005', 'C004', 'Pending'),
('Tr004', '2024-05-04 09:15:00', 10000.00, 'U005', 'U001', 'C005', 'Failed'),
('Tr005', '2024-05-05 18:20:00', 8000.00, 'U004', 'U003', 'C003', 'Success');

-- Transaction Tags
INSERT INTO Transaction_Tags (TransactionID, TagID) VALUES
('Tr001', 'T001'),
('Tr001', 'T003'),
('Tr002', 'T002'),
('Tr003', 'T004'),
('Tr004', 'T005');

-- System Logs
INSERT INTO System_Logs (LogID, Timestamp, TransactionID, Message, ErrorDetails) VALUES
('L001', '2024-05-01 10:01:00', 'TRX001', 'Transaction completed successfully', NULL),
('L002', '2024-05-02 12:31:00', 'TRX002', 'Airtime purchase successful', NULL),
('L003', '2024-05-03 15:46:00', 'TRX003', 'Transaction pending confirmation', NULL),
('L004', '2024-05-04 09:16:00', 'TRX004', 'Transaction failed due to insufficient funds', 'Balance too low'),
('L005', '2024-05-05 18:21:00', 'TRX005', 'Bill payment successful', NULL);
