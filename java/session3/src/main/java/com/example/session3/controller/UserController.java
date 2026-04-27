package com.example.session3.controller;

import com.example.session3.model.User;
import com.example.session3.service.UserService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/users/search")
    public ResponseEntity<List<User>> searchUsers(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Integer age,
            @RequestParam(required = false) String role) {
        return ResponseEntity.ok(userService.searchUsers(name, age, role));
    }

    @PostMapping("/submit")
    public ResponseEntity<String> submit(@RequestBody User user) {
        if (user.getName() == null || user.getName().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Name is required");
        }
        if (user.getRole() == null || user.getRole().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Role is required");
        }
        if (user.getAge() <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Age must be greater than 0");
        }
        userService.submitUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body("User submitted successfully");
    }

    @DeleteMapping("/users/{id}")
    public ResponseEntity<String> deleteUser(
            @PathVariable int id,
            @RequestParam(required = false) Boolean confirm) {
        if (confirm == null || !confirm) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Confirmation required");
        }
        boolean deleted = userService.deleteUser(id, confirm);
        if (!deleted) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("User not found");
        }
        return ResponseEntity.ok("User deleted successfully");
    }
}