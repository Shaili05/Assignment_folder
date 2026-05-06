package com.example.demo.entity;

import com.example.demo.enums.Role;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * User entity mapped to the users table in the database.
 * Supports three roles - ADMIN, MANAGER, and EMPLOYEE.
 * An employee can have one manager assigned by the admin.
 */
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class User {

    /** Auto generated primary key for the user. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Full name of the user. */
    @Column(nullable = false)
    private String name;

    /** Unique email address used for login and identification. */
    @Column(nullable = false, unique = true)
    private String email;

    /** BCrypt hashed password, never stored as plain text. */
    @Column(nullable = false)
    private String password;

    /** Role assigned to this user, determines system access. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    /**
     * Manager assigned to this employee.
     * Null for admin and manager role users.
     */
    @ManyToOne
    @JoinColumn(name = "manager_id")
    private User manager;
}