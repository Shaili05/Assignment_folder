package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Standard API response wrapper for all endpoints.
 * Every API response will be wrapped in this structure.
 * @param <T> the type of data being returned
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponseDto<T> {

    /** Status of the response - "success" or "error". */
    private String status;

    /** Human readable message about the response. */
    private String message;

    /** The actual data being returned. */
    private T data;

    /** Timestamp of when the response was generated. */
    private Instant timestamp;

    /**
     * Creates a success response with data.
     * @param <T> the type of data
     * @param data the data to return
     * @return success ApiResponseDto
     */
    public static <T> ApiResponseDto<T> success(final T data) {
        return ApiResponseDto.<T>builder()
                .status("success")
                .message("Request processed successfully")
                .data(data)
                .timestamp(Instant.now())
                .build();
    }

    /**
     * Creates a success response with data and custom message.
     * @param <T> the type of data
     * @param data the data to return
     * @param msg custom message
     * @return success ApiResponseDto
     */
    public static <T> ApiResponseDto<T> success(final T data, final String msg) {
        return ApiResponseDto.<T>builder()
                .status("success")
                .message(msg)
                .data(data)
                .timestamp(Instant.now())
                .build();
    }

    /**
     * Creates an error response.
     * @param <T> the type of data
     * @param msg error message
     * @return error ApiResponseDto
     */
    public static <T> ApiResponseDto<T> error(final String msg) {
        return ApiResponseDto.<T>builder()
                .status("error")
                .message(msg)
                .data(null)
                .timestamp(Instant.now())
                .build();
    }
}