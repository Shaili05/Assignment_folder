# Session 4 – Spring Boot JPA Todo App
Submitted by : SHAILI TIWARI
# What I built

A Todo management app with proper database storage using JPA and H2.

Todo has: id, title, description, status (PENDING or COMPLETED), createdAt

# APIs

POST /todos  
Creates a new todo. Status defaults to PENDING if not given.
Title must be at least 3 characters otherwise it returns 400.
createdAt is set automatically by the server.

GET /todos  
Returns all todos in the database.

GET /todos/{id}  
Returns a single todo by id. Returns 404 if not found.

PUT /todos/{id}  
Updates title, description and status of an existing todo.

DELETE /todos/{id}  
Deletes a todo by id. Returns 404 if it doesn't exist.

# Project structure

controller – receives requests, calls service  
service – all logic here, converts between DTO and entity  
repository – JpaRepository handles all database operations  
model – Todo entity with JPA annotations  
dto – TodoDTO used for request and response, never expose entity directly  
exception – custom exception and global handler  

# How to run

cd java/session4
mvn spring-boot:run

Runs on port 8084.
H2 console available at http://localhost:8084/h2-console

