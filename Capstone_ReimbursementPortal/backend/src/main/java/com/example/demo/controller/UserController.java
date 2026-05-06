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
 * REST controller for user management operations.
 */
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    /** Logger for tracking requests. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(UserController.class);

    /** Service layer for user business logic. */
    private final UserService userService;

    /**
     * POST /api/users - Creates a new user.
     *
     * @param dto request body with user details
     * @return 201 with created user
     */
    @PostMapping
    public ResponseEntity<ApiResponseDto<UserResponseDto>> createUser(
            @Valid @RequestBody final UserRequestDto dto) {
        LOGGER.info("Request received - POST /api/users for: {}",
                dto.getEmail());
        final UserResponseDto response = userService.createUser(dto);
        LOGGER.info("Request completed - User created ID: {}",
                response.getId());
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponseDto.success(response,
                        "User created successfully"));
    }

    /**
     * DELETE /api/users/{id} - Deletes a user.
     *
     * @param id the user ID to delete
     * @return 200 confirming deletion
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponseDto<Void>> deleteUser(
            @PathVariable final Long id) {
        LOGGER.info("Request received - DELETE /api/users/{}", id);
        userService.deleteUser(id);
        LOGGER.info("Request completed - User deleted ID: {}", id);
        return ResponseEntity.ok(
                ApiResponseDto.success(null,
                        "User deleted successfully"));
    }

    /**
     * GET /api/users - Returns all non-admin users paginated.
     *
     * @param page page number, defaults to 0
     * @param size records per page, defaults to 10
     * @return paginated user list
     */
    @GetMapping
    public ResponseEntity<ApiResponseDto<Page<UserResponseDto>>>
    getAllUsers(
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        LOGGER.info("Request received - GET /api/users page={}, size={}",
                page, size);
        final Page<UserResponseDto> users =
                userService.getAllUsers(PageRequest.of(page, size));
        LOGGER.info("Request completed - Returned {} users",
                users.getTotalElements());
        return ResponseEntity.ok(ApiResponseDto.success(users));
    }

    /**
     * PUT /api/users/{employeeId}/assign-manager/{managerId}
     *
     * @param employeeId employee to update
     * @param managerId manager to assign
     * @return updated employee details
     */
    @PutMapping("/{employeeId}/assign-manager/{managerId}")
    public ResponseEntity<ApiResponseDto<UserResponseDto>> assignManager(
            @PathVariable final Long employeeId,
            @PathVariable final Long managerId) {
        LOGGER.info("Request received - assign-manager "
                + "employee:{} manager:{}", employeeId, managerId);
        final UserResponseDto response =
                userService.assignManager(employeeId, managerId);
        LOGGER.info("Request completed - Manager assigned to: {}",
                employeeId);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Manager assigned successfully"));
    }
}