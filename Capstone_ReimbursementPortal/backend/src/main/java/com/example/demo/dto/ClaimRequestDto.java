package com.example.demo.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Request DTO received when an employee submits a reimbursement claim.
 * Validation annotations ensure invalid data is rejected before processing.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ClaimRequestDto {

    /** Claim amount, must be greater than zero. */
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;

    /** Date when the expense was incurred. */
    @NotNull(message = "Date is required")
    private LocalDate date;

    /** Description of what the expense was for. */
    @NotBlank(message = "Description is required")
    private String description;

    /** ID of the employee submitting this claim. */
    @NotNull(message = "Employee ID is required")
    private Long employeeId;
}