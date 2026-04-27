# Session 3 – Spring Boot REST API
Submitted by : SHAILI TIWARI
This is my third assignment where I built a REST API using Spring Boot.
The idea was to practice layered architecture and dependency injection properly.

# What I built

A simple user management system with in-memory data (no database).
Users have an id, name, age and role.

Three APIs in total:

1. Search Users
GET /users/search

You can pass any combination of name, age, role as query params.
If nothing is passed, all users come back.
Matching is case-insensitive for name and role, exact for age.

Examples I tested:
- /users/search → all 7 users
- /users/search?name=Palak Shete → just that user
- /users/search?age=30 → two users
- /users/search?role=USER → four users
- /users/search?age=30&role=USER → two users matching both

2. Submit a User
POST /submit

Accepts JSON body. I added manual checks — if name or role is empty,
or age is 0 or less, it returns 400 with a message.
On success it returns 201.

3. Delete a User
DELETE /users/{id}?confirm=true

Won't delete unless confirm=true is passed.
If confirm is false or missing, returns "Confirmation required".
If user doesn't exist, returns 404.

# Project structure

controller -- handles incoming requests  
service -- all the logic lives here  
repository -- stores and manages the data  
model -- the User class  

# How to run