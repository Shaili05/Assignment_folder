package com.example.session4.exception;

public class TodoNotFoundException extends RuntimeException {

    public TodoNotFoundException(Long id) {
        super("Could not find todo with id: " + id);
    }
}