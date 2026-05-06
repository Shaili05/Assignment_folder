package com.example.demo.exception;

import com.example.demo.dto.ApiResponseDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Centralized exception handler for all controllers.
 * Converts exceptions into structured JSON error responses
 * instead of default Spring error pages.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** Logger for recording exception details. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Handles resource not found exceptions with a 404 response.
     *
     * @param ex the ResourceNotFoundException that was thrown
     * @return 404 response with error message
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleNotFound(
            final ResourceNotFoundException ex) {
        LOGGER.error("Resource not found: {}", ex.getMessage());
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResponseDto.error(ex.getMessage()));
    }

    /**
     * Handles illegal argument exceptions with a 400 response.
     * Used for duplicate email, invalid role, and workflow violations.
     *
     * @param ex the IllegalArgumentException that was thrown
     * @return 400 response with error message
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleBadRequest(
            final IllegalArgumentException ex) {
        LOGGER.error("Bad request: {}", ex.getMessage());
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponseDto.error(ex.getMessage()));
    }

    /**
     * Handles validation failures from the Valid annotation.
     * Collects all field errors and returns them together.
     *
     * @param ex the MethodArgumentNotValidException that was thrown
     * @return 400 response with all validation error messages
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleValidationErrors(
            final MethodArgumentNotValidException ex) {
        final List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error ->
                        error.getField() + ": "
                                + error.getDefaultMessage())
                .collect(Collectors.toList());
        LOGGER.error("Validation failed: {}", errors);
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponseDto.error(errors.toString()));
    }
}