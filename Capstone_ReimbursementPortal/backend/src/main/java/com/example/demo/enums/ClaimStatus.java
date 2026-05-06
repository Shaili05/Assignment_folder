package com.example.demo.enums;

/**
 * Represents the possible states of a reimbursement claim
 * throughout its lifecycle in the approval workflow.
 */
public enum ClaimStatus {

    /** Claim has been submitted by the employee and awaits review. */
    SUBMITTED,

    /** Claim has been approved by the assigned reviewer. */
    APPROVED,

    /** Claim has been rejected by the assigned reviewer. */
    REJECTED,

    CANCELLED
}