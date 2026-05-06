package com.example.demo.exception;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.enums.Role;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Validates business rules before processing user operations.
 */
@Component
@RequiredArgsConstructor
public class UserValidator {

    /** Logger for tracking validation operations. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(UserValidator.class);

    /** Repository used to check email and ID existence. */
    private final UserRepository userRepository;

    /**
     * Validates a user creation request.
     * Checks email is not taken and role is valid.
     *
     * @param dto the create user request to validate
     */
    public void validateCreateUser(final UserRequestDto dto) {
        LOGGER.debug("Validating user creation for email: {}",
                dto.getEmail());

        if (userRepository.existsByEmail(dto.getEmail())) {
            LOGGER.warn("Duplicate email: {}", dto.getEmail());
            throw new IllegalArgumentException(
                    "A user already exists with email: "
                            + dto.getEmail());
        }

        try {
            Role.valueOf(dto.getRole().toUpperCase());
        } catch (IllegalArgumentException ex) {
            LOGGER.warn("Invalid role: {}", dto.getRole());
            throw new IllegalArgumentException(
                    "Invalid role: " + dto.getRole()
                            + ". Allowed: MANAGER, EMPLOYEE");
        }
    }

    /**
     * Validates that a user with the given ID exists.
     *
     * @param id the user ID to check
     */
    public void validateUserExists(final Long id) {
        LOGGER.debug("Checking existence of user ID: {}", id);
        if (!userRepository.existsById(id)) {
            LOGGER.warn("User not found with ID: {}", id);
            throw new ResourceNotFoundException(
                    "No user found with ID: " + id);
        }
    }
}