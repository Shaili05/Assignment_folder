package com.example.demo.service;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Service interface defining all User related operations.
 * Having an interface separates the contract from implementation,
 * making it easy to swap implementations or write tests.
 */
public interface UserService {

    /**
     * Creates a new user in the system.
     * Password will be encrypted before saving.
     *
     * @param dto the user details from the request
     * @return the created user details (without password)
     */
    UserResponseDto createUser(UserRequestDto dto);

    /**
     * Removes a user from the system permanently.
     *
     * @param id the unique ID of the user to delete
     */
    void deleteUser(Long id);

    /**
     * Retrieves all users with pagination support.
     * Pagination prevents loading thousands of records at once.
     *
     * @param pageable contains page number and page size
     * @return one page of user records
     */
    Page<UserResponseDto> getAllUsers(Pageable pageable);

    /**
     * Links an employee to their manager.
     * The manager must have MANAGER or ADMIN role.
     *
     * @param employeeId the ID of the employee
     * @param managerId the ID of the manager
     * @return updated employee details showing their manager
     */
    UserResponseDto assignManager(Long employeeId, Long managerId);
}