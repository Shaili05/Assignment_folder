package com.example.demo.exception;

/**
 * Exception thrown when a requested resource cannot be found.
 * Used when looking up a user, claim, or any entity by ID or email
 * that does not exist in the database.
 */
public class ResourceNotFoundException extends RuntimeException {

    /** Serial version UID for serialization compatibility. */
    private static final long serialVersionUID = 1L;

    /**
     * Creates a new exception with a descriptive message.
     *
     * @param message explanation of what resource was not found
     */
    public ResourceNotFoundException(final String message) {
        super(message);
    }
}