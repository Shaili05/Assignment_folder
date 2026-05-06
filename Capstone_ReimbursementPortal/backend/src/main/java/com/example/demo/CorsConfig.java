package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * CORS configuration for the reimbursement portal.
 * Allows the frontend HTML pages to communicate with backend APIs
 * by permitting cross-origin requests.
 */
@Configuration
public class CorsConfig {

    /**
     * Registers CORS mappings to allow frontend API access.
     *
     * @return WebMvcConfigurer with CORS rules applied
     */
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            /**
             * Configures allowed origins, methods and headers.
             *
             * @param registry the CORS registry to configure
             */
            @Override
            public void addCorsMappings(final CorsRegistry registry) {
                registry.addMapping("/api/**")
                        .allowedOrigins("*")
                        .allowedMethods(
                                "GET", "POST", "PUT", "DELETE")
                        .allowedHeaders("*");
            }
        };
    }
}