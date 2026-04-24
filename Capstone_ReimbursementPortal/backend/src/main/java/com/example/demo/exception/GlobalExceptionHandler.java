package com.example.demo.exception;

import com.example.demo.dto.ApiResponseDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * Catches all exceptions in one place.
 * Without this, Spring returns ugly HTML error pages.
 * Now every error returns a clean JSON response.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** To log whatever error occurred. */
    private static final Logger logger =
            LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * When something is not found in db, return 404.
     *
     * @param ex the exception thrown
     * @return 404 with error message
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleNotFound(
            final ResourceNotFoundException ex) {
        logger.error("Not found: {}", ex.getMessage());
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResponseDto.error(ex.getMessage()));
    }

    /**
     * For bad inputs like duplicate email or wrong role.
     * Returns 400 with what went wrong.
     *
     * @param ex the exception thrown
     * @return 400 with error message
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleBadRequest(
            final IllegalArgumentException ex) {
        logger.error("Bad request: {}", ex.getMessage());
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponseDto.error(ex.getMessage()));
    }

    /**
     * When @Valid fails on request body fields.
     * I pick the first error message and return it.
     *
     * @param ex the validation exception
     * @return 400 with which field failed and why
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponseDto<Object>> handleValidationErrors(
            final MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": "
                        + error.getDefaultMessage())
                .findFirst()
                .orElse("Validation failed");
        logger.error("Validation error: {}", errorMessage);
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponseDto.error(errorMessage));
    }
}