package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * What we send back when someone asks for user data.
 * Password is not included here on purpose.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseDto {

    /** User's ID from database. */
    private Long id;

    /** User's full name. */
    private String name;

    /** User's email. */
    private String email;

    /** Role assigned to this user. */
    private String role;

    /**
     * Manager's name if one is assigned.
     * Stays null until admin assigns a manager.
     */
    private String managerName;
}