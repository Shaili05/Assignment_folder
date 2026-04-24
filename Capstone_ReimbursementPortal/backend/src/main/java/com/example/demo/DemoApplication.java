package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;

/**
 * Main class to start the application.
 * I excluded UserDetailsServiceAutoConfiguration because we don't
 * want Spring to generate a default password on startup.
 */
@SpringBootApplication(exclude = {UserDetailsServiceAutoConfiguration.class})
public class DemoApplication {

	/**
	 * Entry point of the app.
	 *
	 * @param args command line arguments
	 */
	public static void main(final String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}
}