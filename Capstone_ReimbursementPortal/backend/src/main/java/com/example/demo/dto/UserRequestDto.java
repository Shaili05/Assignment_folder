package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * This is what the API receives when creating a user.
 * Added validation here so bad data gets rejected early.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserRequestDto {

    /** Name can't be empty. */
    @NotBlank(message = "Name is required")
    private String name;

    /**
     * Email must be from @company.com domain only.
     * I used a regex pattern to enforce this.
     */
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    @Pattern(
            regexp = "^[a-zA-Z0-9._%+-]+@company\\.com$",
            message = "Email must be a valid @company.com address"
    )
    private String email;

    /**
     * Password will be encrypted before saving.
     * Minimum 8 characters required.
     */
    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    /** Role should be ADMIN, MANAGER or EMPLOYEE. */
    @NotBlank(message = "Role is required")
    private String role;
}