package com.example.demo.enums;

/**
 * Defines the roles available in the reimbursement system.
 * Each role controls what actions a user can perform.
 */
public enum Role {

    /** Administrator role with full system access. */
    ADMIN,

    /** Manager role that can review and action claims. */
    MANAGER,

    /** Employee role that can submit and track claims. */
    EMPLOYEE
}