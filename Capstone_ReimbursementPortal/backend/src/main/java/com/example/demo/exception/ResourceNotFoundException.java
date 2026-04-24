package com.example.demo.exception;

/**
 * Exception thrown when a requested resource cannot be found.
 * For example when looking up a user ID that does not exist.
 * Extends RuntimeException so it does not need to be declared
 * in every method signature.
 */
public class ResourceNotFoundException extends RuntimeException {

    /**
     * Creates a new exception with a descriptive message.
     *
     * @param message explanation of what was not found
     */
    public ResourceNotFoundException(final String message) {
        super(message);
    }
}