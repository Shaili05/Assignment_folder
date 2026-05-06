package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;

/**
 * Main entry point for the Reimbursement Portal application.
 * Excludes default Spring Security auto-configuration to prevent
 * auto-generated login page and default password on startup.
 */
@SpringBootApplication(exclude = {UserDetailsServiceAutoConfiguration.class})
public class DemoApplication {

	/**
	 * Starts the Spring Boot application.
	 *
	 * @param args command line arguments passed at startup
	 */
	public static void main(final String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}
}