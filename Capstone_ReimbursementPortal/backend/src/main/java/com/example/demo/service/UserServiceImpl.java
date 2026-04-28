package com.example.demo.service;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import com.example.demo.entity.User;
import com.example.demo.enums.Role;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.exception.UserValidator;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Service class for user related operations.
 * Validator is called first before any database operation.
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    /** For logging what is happening in each method. */
    private static final Logger logger =
            LoggerFactory.getLogger(UserServiceImpl.class);

    /** Handles all database queries for users. */
    private final UserRepository userRepository;

    /** Checks business rules before we process anything. */
    private final UserValidator userValidator;

    /**
     * BCrypt password encoder injected from SecurityConfig.
     * Using interface PasswordEncoder for flexibility.
     */
    private final PasswordEncoder passwordEncoder;

    /**
     * Creates a new user.
     * Validates first, then encrypts password, then saves.
     *
     * @param dto incoming request data
     * @return saved user details without password
     */
    @Override
    public UserResponseDto createUser(final UserRequestDto dto) {
        logger.info("Creating user with email: {}", dto.getEmail());

        // validate first before touching the database
        userValidator.validateCreateUser(dto);

        User user = new User();
        user.setName(dto.getName());
        user.setEmail(dto.getEmail());

        // never save plain text password - BCrypt hashes it
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setRole(Role.valueOf(dto.getRole().toUpperCase()));

        User savedUser = userRepository.save(user);
        logger.info("User saved with ID: {}", savedUser.getId());

        return mapToResponse(savedUser);
    }

    /**
     * Deletes user by ID.
     * Validates user exists before attempting deletion.
     *
     * @param id user ID to delete
     */
    @Override
    public void deleteUser(final Long id) {
        logger.info("Deleting user ID: {}", id);

        // validate user exists before trying to delete
        userValidator.validateUserExists(id);

        userRepository.deleteById(id);
        logger.info("Deleted user ID: {}", id);
    }

    /**
     * Gets all users with pagination.
     * Pagination prevents loading all records at once.
     *
     * @param pageable page number and size
     * @return one page of users
     */
    @Override
    public Page<UserResponseDto> getAllUsers(final Pageable pageable) {
        logger.info("Fetching page: {}, size: {}",
                pageable.getPageNumber(), pageable.getPageSize());

        return userRepository.findAll(pageable)
                .map(this::mapToResponse);
    }

    /**
     * Assigns a manager to an employee.
     * findById with orElseThrow already handles not-found case
     * so no need for separate validateUserExists calls here.
     *
     * @param employeeId employee to update
     * @param managerId manager to assign
     * @return updated employee data
     */
    @Override
    public UserResponseDto assignManager(
            final Long employeeId, final Long managerId) {
        logger.info("Assigning manager {} to employee {}",
                managerId, employeeId);

        // orElseThrow handles not-found - no need for validateUserExists
        User employee = userRepository.findById(employeeId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: " + employeeId));

        User manager = userRepository.findById(managerId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Manager not found with ID: " + managerId));

        // only MANAGER or ADMIN role can be assigned as a manager
        if (manager.getRole() != Role.MANAGER
                && manager.getRole() != Role.ADMIN) {
            throw new IllegalArgumentException(
                    "User with ID " + managerId
                            + " does not have MANAGER or ADMIN role");
        }

        employee.setManager(manager);
        User updated = userRepository.save(employee);
        logger.info("Manager assigned to employee ID: {}", employeeId);

        return mapToResponse(updated);
    }

    /**
     * Converts User entity to response DTO.
     * Entity is never returned directly to avoid exposing DB fields.
     *
     * @param user entity from database
     * @return response DTO
     */
    private UserResponseDto mapToResponse(final User user) {
        return UserResponseDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .role(user.getRole().name())
                .managerName(user.getManager() != null
                        ? user.getManager().getName() : null)
                .build();
    }
}