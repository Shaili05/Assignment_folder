package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Security config for the app.
 * For now I am allowing all requests freely
 * since we are handling roles manually in the service layer.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    /**
     * Disabling CSRF and allowing all requests.
     * CSRF is not needed for REST APIs.
     *
     * @param http HttpSecurity object
     * @return built security filter chain
     * @throws Exception if something goes wrong in config
     */
    @Bean
    public SecurityFilterChain securityFilterChain(
            final HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(
                        auth -> auth.anyRequest().permitAll()
                );
        return http.build();
    }

    /**
     * BCrypt encoder bean.
     * Using this to hash passwords before saving to database.
     *
     * @return PasswordEncoder instance
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}