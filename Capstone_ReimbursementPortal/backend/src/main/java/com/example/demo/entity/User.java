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
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * User entity - maps to the users table in database.
 * Can be ADMIN, MANAGER or EMPLOYEE depending on the role.
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {

    /** Auto generated primary key. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Name of the user. */
    @Column(nullable = false)
    private String name;

    /** Email must be unique across all users. */
    @Column(nullable = false, unique = true)
    private String email;

    /** Stored as BCrypt hash, never plain text. */
    @Column(nullable = false)
    private String password;

    /** Role decides what the user can do in the system. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    /**
     * Manager assigned to this user.
     * Will be null for admins and managers.
     */
    @ManyToOne
    @JoinColumn(name = "manager_id")
    private User manager;
}