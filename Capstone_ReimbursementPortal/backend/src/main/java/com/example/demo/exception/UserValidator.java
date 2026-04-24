package com.example.demo.exception;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.enums.Role;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Handles validation before any user operation.
 * I kept this separate from the service so it stays clean.
 */
@Component
@RequiredArgsConstructor
public class UserValidator {

    /** To log what validation is happening. */
    private static final Logger logger =
            LoggerFactory.getLogger(UserValidator.class);

    /** Need this to check if email or ID already exists in db. */
    private final UserRepository userRepository;

    /**
     * Checks if we can create a new user.
     * Email should not already exist, and role should be valid.
     *
     * @param dto the create user request
     * @throws IllegalArgumentException if email taken or role wrong
     */
    public void validateCreateUser(final UserRequestDto dto) {
        logger.debug("Validating new user with email: {}", dto.getEmail());

        if (userRepository.existsByEmail(dto.getEmail())) {
            logger.warn("Email already exists: {}", dto.getEmail());
            throw new IllegalArgumentException(
                    "A user already exists with email: " + dto.getEmail());
        }

        try {
            Role.valueOf(dto.getRole().toUpperCase());
        } catch (IllegalArgumentException e) {
            logger.warn("Invalid role given: {}", dto.getRole());
            throw new IllegalArgumentException(
                    "Invalid role: " + dto.getRole()
                            + ". Allowed values are ADMIN, MANAGER, EMPLOYEE");
        }

        logger.debug("Validation passed for: {}", dto.getEmail());
    }

    /**
     * Checks if a user with given ID exists.
     * Used before delete or assign manager operations.
     *
     * @param id user ID to look up
     * @throws ResourceNotFoundException if not found
     */
    public void validateUserExists(final Long id) {
        logger.debug("Checking if user exists, ID: {}", id);

        if (!userRepository.existsById(id)) {
            logger.warn("User not found with ID: {}", id);
            throw new ResourceNotFoundException(
                    "No user found with ID: " + id);
        }

        logger.debug("User found with ID: {}", id);
    }
}