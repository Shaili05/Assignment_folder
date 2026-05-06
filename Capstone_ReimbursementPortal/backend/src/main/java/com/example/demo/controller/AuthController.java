package com.example.demo.controller;

import com.example.demo.dto.ApiResponseDto;
import com.example.demo.dto.LoginRequestDto;
import com.example.demo.dto.LoginResponseDto;
import com.example.demo.entity.User;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.repository.UserRepository;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Handles authentication requests.
 * Provides login endpoint for frontend to authenticate users.
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    /** Logger for tracking authentication requests. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(AuthController.class);

    /** Default page size constant. */
    private static final String INVALID_CREDENTIALS =
            "Invalid email or password";

    /** Repository for fetching user by email. */
    private final UserRepository userRepository;

    /** Encoder for verifying password against stored hash. */
    private final PasswordEncoder passwordEncoder;

    /**
     * POST /api/auth/login
     * Authenticates a user with email and password.
     * Returns user details including role for frontend navigation.
     *
     * @param dto login request with email and password
     * @return user details on success or error message on failure
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponseDto<LoginResponseDto>> login(
            @Valid @RequestBody final LoginRequestDto dto) {
        LOGGER.info("Login request received for email: {}",
                dto.getEmail());

        final User user = userRepository.findByEmail(dto.getEmail())
                .orElseThrow(() -> new ResourceNotFoundException(
                        INVALID_CREDENTIALS));

        if (!passwordEncoder.matches(
                dto.getPassword(), user.getPassword())) {
            LOGGER.warn("Invalid password attempt for email: {}",
                    dto.getEmail());
            throw new IllegalArgumentException(INVALID_CREDENTIALS);
        }

        final LoginResponseDto response = LoginResponseDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();

        LOGGER.info("Login successful for user ID: {}", user.getId());
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Login successful"));
    }
}