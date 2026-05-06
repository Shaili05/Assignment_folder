package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Response DTO returned when user data is requested.
 * Password field is intentionally excluded for security.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseDto {

    /** Unique identifier of the user. */
    private Long id;

    /** Full name of the user. */
    private String name;

    /** Email address of the user. */
    private String email;

    /** Role assigned to this user in the system. */
    private String role;

    /**
     * Name of the manager assigned to this user.
     * Null if no manager has been assigned yet.
     */
    private String managerName;
}