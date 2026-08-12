# Member Data Management System

A Python utility that cleans and validates raw member data using regular
expressions, stores it using core Python data structures, and exposes an
object-oriented interface to work with it. Built as part of a Python Core
Concepts training assignment.

## Features

- **Data validation** — validates emails and phone numbers using the `re` module
- **Custom exception handling** — a dedicated `InvalidMemberDataError` catches
  malformed records without crashing the program
- **Object-Oriented Design** — a `Member` class represents each validated
  member profile
- **Functional programming** — filter and transform member lists using
  `lambda` with `filter()` and `map()`
- **Modular structure** — logic is split across multiple files connected via
  `import`
- **Packaged as a wheel** — distributable as a standard installable Python
  package (`.whl`)

## Requirements

- Python 3.9+

## How to Access and Run This Project

### 1. Clone the repository

```bash
git clone https://github.com/Shaili05/Assignment_folder.git
cd python_project

### 2. Create and activate a virtual environment
python -m venv venv

### 3. Activate it:
venv\Scripts\activate

### 4. Run the project
python demo.py