package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/**
 * Standard wrapper for all API responses in the system.
 * Every endpoint returns this same structure so the frontend
 * always knows what fields to expect.
 *
 * @param <T> type of data payload being returned
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponseDto<T> {

    /** Response status, either success or error. */
    private String status;

    /** Short human readable message describing the outcome. */
    private String message;

    /** Actual response payload, varies by endpoint. */
    private T data;

    /** Timestamp of when this response was generated. */
    private Instant timestamp;

    /**
     * Creates a success response with data and default message.
     *
     * @param <T> data type
     * @param data the payload to return
     * @return success response wrapper
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
     *
     * @param <T> data type
     * @param data the payload to return
     * @param msg custom message describing the outcome
     * @return success response wrapper
     */
    public static <T> ApiResponseDto<T> success(
            final T data, final String msg) {
        return ApiResponseDto.<T>builder()
                .status("success")
                .message(msg)
                .data(data)
                .timestamp(Instant.now())
                .build();
    }

    /**
     * Creates an error response with an error message.
     *
     * @param <T> data type
     * @param msg error message describing what went wrong
     * @return error response wrapper
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