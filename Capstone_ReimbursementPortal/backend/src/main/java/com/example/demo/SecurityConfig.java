package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Security configuration for the reimbursement portal.
 * Disables default Spring Security login page and CSRF protection
 * since the application uses stateless REST API design.
 * Provides BCrypt password encoder bean for password hashing.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    /**
     * Configures HTTP security to permit all requests without authentication.
     * CSRF is disabled as REST APIs use stateless token-based requests.
     *
     * @param http the HttpSecurity builder to configure
     * @return the configured SecurityFilterChain bean
     * @throws Exception if the security configuration fails
     */
    @Bean
    public SecurityFilterChain securityFilterChain(
            final HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(
                        auth -> auth.anyRequest().permitAll());
        return http.build();
    }

    /**
     * Provides a BCryptPasswordEncoder bean for password hashing.
     * Injected into UserServiceImpl and AuthController.
     *
     * @return a BCryptPasswordEncoder instance
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}