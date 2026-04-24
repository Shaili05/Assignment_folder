package com.example.demo.entity;

import com.example.demo.enums.ClaimStatus;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Claim entity - maps to the claims table.
 * Each claim is submitted by an employee and reviewed by manager or admin.
 */
@Entity
@Table(name = "claims")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Claim {

    /** Auto generated id for each claim. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** How much money the employee is claiming. */
    @Column(nullable = false)
    private BigDecimal amount;

    /** Date when the expense happened. */
    @Column(nullable = false)
    private LocalDate date;

    /** What the expense was for. */
    @Column(nullable = false)
    private String description;

    /** Tracks where the claim is in the workflow. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ClaimStatus status;

    /** Manager or admin can add a comment when approving or rejecting. */
    private String reviewerComment;

    /** Who submitted this claim. */
    @ManyToOne
    @JoinColumn(name = "employee_id", nullable = false)
    private User employee;

    /** Who will review this claim - assigned automatically. */
    @ManyToOne
    @JoinColumn(name = "reviewer_id")
    private User reviewer;

    /** Set automatically when claim is first created. */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /** Updates every time claim is modified. */
    private LocalDateTime updatedAt;

    /** Runs before first save to set timestamps. */
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    /** Runs before every update to refresh updatedAt. */
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}