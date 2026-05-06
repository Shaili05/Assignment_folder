package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Response DTO returned after successful login.
 * Contains user details needed by frontend for navigation.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponseDto {

    /**
     * Unique ID of the logged in user.
     * Stored in localStorage for subsequent API calls.
     */
    private Long id;

    /**
     * Full name of the logged in user.
     * Displayed in the header after login.
     */
    private String name;

    /**
     * Email of the logged in user.
     */
    private String email;

    /**
     * Role of the logged in user.
     * Used by frontend to redirect to correct dashboard.
     */
    private String role;
}