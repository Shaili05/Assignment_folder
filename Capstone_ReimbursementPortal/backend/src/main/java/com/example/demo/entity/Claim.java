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
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Claim entity mapped to the claims table in the database.
 * Each claim is submitted by an employee and reviewed
 * by an assigned manager or admin.
 */
@Entity
@Table(name = "claims")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Claim {

    /** Auto generated primary key for each claim. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Amount of money being claimed by the employee. */
    @Column(nullable = false)
    private BigDecimal amount;

    /** Date when the expense was incurred. */
    @Column(nullable = false)
    private LocalDate date;

    /** Description of what the expense was for. */
    @Column(nullable = false)
    private String description;

    /** Current status of the claim in the workflow. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ClaimStatus status;

    /** Comment added by the reviewer during approval or rejection. */
    private String reviewerComment;

    /** Employee who submitted this claim. */
    @ManyToOne
    @JoinColumn(name = "employee_id")
    private User employee;

    /** Reviewer assigned to evaluate this claim. */
    @ManyToOne
    @JoinColumn(name = "reviewer_id")
    private User reviewer;

    /** Timestamp when the claim was first created. */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /** Timestamp of the last update to this claim. */
    private LocalDateTime updatedAt;

    /**
     * Sets timestamps before the entity is first persisted.
     */
    @PrePersist
    public void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    /**
     * Updates the updatedAt timestamp before every update.
     */
    @PreUpdate
    public void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}