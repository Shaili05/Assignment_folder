package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Wrapper for all API responses in the system.
 * Every endpoint returns this same structure so frontend
 * always knows what to expect.
 *
 * @param <T> type of data being returned
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponseDto<T> {

    /** Either "success" or "error". */
    private String status;

    /** Short message about what happened. */
    private String message;

    /** Actual data, can be anything depending on the endpoint. */
    private T data;

    /** When this response was created. */
    private Instant timestamp;

    /**
     * Quick way to return success with data.
     *
     * @param <T> data type
     * @param data the data to return
     * @return success response
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
     * Success response with a custom message.
     *
     * @param <T> data type
     * @param data the data to return
     * @param msg custom message to show
     * @return success response
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
     * Used when something goes wrong.
     *
     * @param <T> data type
     * @param msg error message
     * @return error response
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