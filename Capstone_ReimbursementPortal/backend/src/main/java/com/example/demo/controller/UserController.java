package com.example.demo.controller;

import com.example.demo.dto.ApiResponseDto;
import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Controller for user related APIs.
 * All requests come here first, then I pass them to the service.
 */
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    /** Using this to log which API got called. */
    private static final Logger logger =
            LoggerFactory.getLogger(UserController.class);

    /** Service does the actual work, controller just receives requests. */
    private final UserService userService;

    /**
     * Creates a new user.
     * @Valid checks the request body before it even reaches here.
     *
     * @param dto request body with user details
     * @return 201 with the created user
     */
    @PostMapping
    public ResponseEntity<ApiResponseDto<UserResponseDto>> createUser(
            @Valid @RequestBody final UserRequestDto dto) {
        logger.info("POST /api/users called for email: {}", dto.getEmail());
        UserResponseDto response = userService.createUser(dto);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponseDto.success(response,
                        "User created successfully"));
    }

    /**
     * Deletes a user by ID.
     *
     * @param id user ID from the URL
     * @return 200 if deleted successfully
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponseDto<Void>> deleteUser(
            @PathVariable final Long id) {
        logger.info("DELETE /api/users/{} called", id);
        userService.deleteUser(id);
        return ResponseEntity.ok(
                ApiResponseDto.success(null, "User deleted successfully"));
    }

    /**
     * Returns all users, paginated.
     * Default page is 0 and default size is 10.
     *
     * @param page which page to fetch
     * @param size how many records per page
     * @return list of users for that page
     */
    @GetMapping
    public ResponseEntity<ApiResponseDto<Page<UserResponseDto>>> getAllUsers(
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        logger.info("GET /api/users called - page={}, size={}", page, size);
        Page<UserResponseDto> users =
                userService.getAllUsers(PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponseDto.success(users));
    }

    /**
     * Assigns a manager to an employee.
     * Both IDs come from the URL path.
     *
     * @param employeeId employee who needs a manager
     * @param managerId manager being assigned
     * @return updated employee details
     */
    @PutMapping("/{employeeId}/assign-manager/{managerId}")
    public ResponseEntity<ApiResponseDto<UserResponseDto>> assignManager(
            @PathVariable final Long employeeId,
            @PathVariable final Long managerId) {
        logger.info("PUT assign-manager called - employee: {}, manager: {}",
                employeeId, managerId);
        UserResponseDto response =
                userService.assignManager(employeeId, managerId);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Manager assigned successfully"));
    }
}