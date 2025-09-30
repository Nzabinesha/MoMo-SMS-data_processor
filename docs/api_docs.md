SMS Transactions API with Basic Authentication

1. Introduction to API Security

APIs are the backbone of modern applications, enabling different systems to communicate and share data. Because APIs often expose sensitive data or perform critical actions, securing them is essential.

One common but simple method is Basic Authentication, where each request includes a username and password encoded in the Authorization header.

Strengths of Basic Auth

Easy to implement and test
Supported in all HTTP clients

Limitations of Basic Auth

Credentials are sent with every request, increasing exposure risk
Credentials do not expire unless changed manually
Difficult to revoke access for a single user without changing the password
Vulnerable to interception if HTTPS is not enforced

For small projects, Basic Auth may be sufficient. For production, however, stronger alternatives such as JWT (JSON Web Token) or OAuth2 are recommended.

2. API Documentation

Base URL:

http://localhost:8000


Authentication:
All endpoints require Basic Authentication with credentials set in environment variables API_USER and API_PASS. Example default:

Authorization: Basic <base64(admin:changeme)>


Content Type:

Requests and responses use application/json.
All IDs are integers (internal_id), while transaction_id may be alphanumeric.

API Documentation

Document all endpoints, their methods, request examples, responses, and error codes.

Example table format:

 

Endpoint
Method
Request Example
Response Example
Error Codes
/transactions
GET
curl -u admin:changeme http://localhost:8000/transactions
json [ { "internal_id": 1, "phone": "+250788123456", "message": "Hello", "status": "SENT" } ]
401 Unauthorized – Invalid/missing credentials500 Internal Server Error – Server failure
/transactions/{id}
GET
curl -u admin:changeme http://localhost:8000/transactions/1
json { "internal_id": 1, "phone": "+250788123456", "message": "Hello", "status": "SENT" }
401 Unauthorized404 Not Found – Transaction ID does not exist500 Internal Server Error
/transactions
POST
curl -u admin:changeme -X POST -H "Content-Type: application/json" -d '{"phone":"+250700000000","message":"Test","status":"SENT"}' http://localhost:8000/transactions
json { "internal_id": 3, "phone": "+250700000000", "message": "Test", "status": "SENT" }
401 Unauthorized400 Bad Request – Invalid JSON or missing fields500 Internal Server Error
/transactions/{id}
PUT
curl -u admin:changeme -X PUT -H "Content-Type: application/json" -d '{"status":"DELIVERED"}' http://localhost:8000/transactions/1
json { "internal_id": 1, "phone": "+250788123456", "message": "Hello", "status": "DELIVERED" }
401 Unauthorized404 Not Found – Transaction does not exist400 Bad Request – Invalid update payload500 Internal Server Error
/transactions/{id}
DELETE
curl -u admin:changeme -X DELETE http://localhost:8000/transactions/2
json { "internal_id": 2, "phone": "+250700000000", "message": "Test", "status": "SENT" }
401 Unauthorized404 Not Found500 Internal Server Error


Notes:

All endpoints require Basic Authentication with admin:changeme (or your configured API_USER/API_PASS).

Unauthorized requests return 401 with WWW-Authenticate header.

The request/response format is JSON.

internal_id is the unique identifier for each transaction.

DELETE returns the deleted transaction object (not empty).


Results of DSA Comparison

Overview:
The SMS parser converts unstructured SMS messages into structured transaction records in JSON format. We evaluated different approaches to storing and accessing these transactions and analyzed the efficiency of our data structures.

Data Structures Used

Structure
Purpose
Notes
List
Store all transactions in order
Preserves the sequence of messages, simple to iterate over for GET /transactions.
Dictionary (per transaction)
Store individual transaction fields
Allows fast access to fields by key (amount, transaction_id, sender, etc.).


Algorithm Summary

Steps of the Parser:

1.Load XML using xml.etree.ElementTree.

2.Iterate over all <sms> elements.

3.Use regex patterns to extract key transaction information:

Amount (AMOUNT_RE)

Transaction ID (TXID_RE)

Fees (FEE_RE)

Balance (BALANCE_RE)

Sender/Receiver (RECEIVED_RE, PAYMENT_RE, TRANSFER_RE)

4.Classify transaction type (receive, payment, transfer, deposit, other).


5.Assign internal sequential IDs and fallback transaction IDs.

6.Save the structured data to JSON.

Complexity Analysis


Operation
Time Complexity
Space Complexity
Notes
Parse XML
O(n)
O(n)
n = number of SMS messages
Regex matching per message
O(m)
O(1)
m = length of SMS body
Storing transactions
O(n)
O(n)
Each transaction stored as a dictionary
Lookup by internal_id
O(n)
O(1)
Linear search through list; acceptable for small datasets
Lookup by transaction_id
O(n)
O(1)
Could optimize to O(1) with a dictionary keyed by transaction_id


Sample Output (First 2 Transactions)

[
  {
    "internal_id": 1,
    "transaction_id": "Tx12345",
    "transaction_type": "receive",
    "amount": 10000,
    "fee": null,
    "balance": 50000,
    "sender": {"name": "John Doe", "phone": "+250788123456"},
    "receiver": null,
    "timestamp": "2025-09-29T08:15:00Z",
    "raw": "You have received 10,000 RWF from John Doe (+250788123456)"
  },
  {
    "internal_id": 2,
    "transaction_id": "Tx12346",
    "transaction_type": "payment",
    "amount": 5000,
    "fee": 50,
    "balance": 45000,
    "sender": null,
    "receiver": {"name": "Alice Smith"},
    "timestamp": "2025-09-29T09:20:00Z",
    "raw": "TxId: Tx12346 Your payment of 5,000 RWF to Alice Smith. Fee was 50 RWF."
  }
]





Insights:

Lists preserve order and are easy to iterate for API endpoints.

Dictionaries can optimize lookups by transaction_id to O(1).

Regex-based parsing is flexible but requires maintenance if SMS formats change.

 Reflection on Basic Auth Limitations

Basic Authentication is simple and works well for small projects, but it has several limitations:

Credentials Sent in Every Request: Increases the risk of exposure.

No Token Expiration: Compromised credentials remain valid until changed.

Difficult to Revoke Access: Cannot revoke a single client easily.

Vulnerable Without HTTPS: Credentials are transmitted in plain text.

Stronger Alternatives:


Alternative
Advantage
JWT(Json Web Token)
Stateless, supports token expiration, encodes user claims.
OAuth2
Industry standard for delegated authorization, supports scopes, refresh tokens, and revocation.



For production systems, JWT or OAuth2 are recommended over Basic Auth for better security and scalability.

Conclusion

This project demonstrated:

How to secure a simple SMS Transactions API using Basic Authentication.
Full documentation of CRUD endpoints with examples and error handling.
A comparison of data structures and algorithmic complexity for parsing SMS data.
A critical reflection on the limitations of Basic Auth and more robust alternatives.

This serves as a foundation for understanding both API design and API security, while highlighting areas for improvement in real-world deployments.
