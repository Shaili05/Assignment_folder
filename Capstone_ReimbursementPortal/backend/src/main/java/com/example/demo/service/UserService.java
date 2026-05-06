package com.example.demo.service;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Interface for user operations.
 * Defines what methods UserServiceImpl must implement.
 */
public interface UserService {

    /**
     * Creates a new user in the system.
     *
     * @param dto incoming request with user details
     * @return saved user details without password
     */
    UserResponseDto createUser(UserRequestDto dto);

    /**
     * Deletes a user by their ID.
     *
     * @param id the user ID to delete
     */
    void deleteUser(Long id);

    /**
     * Returns all users with pagination support.
     *
     * @param pageable page number and size
     * @return one page of users
     */
    Page<UserResponseDto> getAllUsers(Pageable pageable);

    /**
     * Assigns a manager to an employee.
     *
     * @param employeeId employee who needs a manager
     * @param managerId manager being assigned
     * @return updated employee details
     */
    UserResponseDto assignManager(Long employeeId, Long managerId);
}