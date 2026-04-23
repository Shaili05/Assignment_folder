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
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Entity representing a reimbursement claim in the system.
 */
@Entity
@Table(name = "claims")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Claim {

    /** Unique identifier for the claim. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Amount requested for reimbursement. */
    @Column(nullable = false)
    private BigDecimal amount;

    /** Date of the expense. */
    @Column(nullable = false)
    private LocalDate date;

    /** Description of the expense. */
    @Column(nullable = false)
    private String description;

    /** Current status of the claim. */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ClaimStatus status;

    /** Comments added by the reviewer. */
    private String reviewerComment;

    /** Employee who submitted the claim. */
    @ManyToOne
    @JoinColumn(name = "employee_id", nullable = false)
    private User employee;

    /** Manager or Admin who reviews the claim. */
    @ManyToOne
    @JoinColumn(name = "reviewer_id")
    private User reviewer;

    /** Date and time when the claim was created. */
    @Column(nullable = false, updatable = false)
    private java.time.LocalDateTime createdAt;

    /** Date and time when the claim was last updated. */
    private java.time.LocalDateTime updatedAt;

    /** Sets createdAt and updatedAt before first save. */
    @jakarta.persistence.PrePersist
    protected void onCreate() {
        createdAt = java.time.LocalDateTime.now();
        updatedAt = java.time.LocalDateTime.now();
    }

    /** Updates updatedAt before every update. */
    @jakarta.persistence.PreUpdate
    protected void onUpdate() {
        updatedAt = java.time.LocalDateTime.now();
    }
}