package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Request DTO for user login.
 * Contains email and password for authentication.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequestDto {

    /**
     * Email address of the user trying to log in.
     * Must be a valid company email.
     */
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    /**
     * Password of the user.
     * Will be matched against stored BCrypt hash.
     */
    @NotBlank(message = "Password is required")
    private String password;
}