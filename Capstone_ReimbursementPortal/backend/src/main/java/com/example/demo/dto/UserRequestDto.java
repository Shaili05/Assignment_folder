package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Request DTO received when creating a new user.
 * Validation annotations ensure all fields meet requirements
 * before any business logic is executed.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UserRequestDto {

    /** Full name of the user, cannot be blank. */
    @NotBlank(message = "Name is required")
    private String name;

    /**
     * Company email address of the user.
     * Must follow the company domain format.
     */
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    @Pattern(
            regexp = "^[a-zA-Z0-9._%+-]+@company\\.com$",
            message = "Email must be a valid @company.com address"
    )
    private String email;

    /**
     * Password for the user account.
     * Will be encrypted using BCrypt before storage.
     */
    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    /** Role assigned to the user, must be ADMIN, MANAGER or EMPLOYEE. */
    @NotBlank(message = "Role is required")
    private String role;
}