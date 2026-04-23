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
 * Entity representing a user in the reimbursement system.
 * A user can be an Admin, Manager, or Employee.
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {

    /** Unique identifier for the user. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Full name of the user. */
    @Column(nullable = false)
    private String name;

    /** Company email address - must be unique. */
    @Column(nullable = false, unique = true)
    private String email;

    /** Encrypted password of the user. */
    @Column(nullable = false)
    private String password;

    /** Role of the user in the system. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    /**
     * The manager assigned to this employee.
     * Null if user is Admin or Manager.
     */
    @ManyToOne
    @JoinColumn(name = "manager_id")
    private User manager;
}