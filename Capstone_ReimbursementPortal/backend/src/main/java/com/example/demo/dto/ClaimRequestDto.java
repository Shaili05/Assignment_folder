package com.example.demo.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * This is what the API receives when an employee submits a claim.
 * I added basic validations so invalid data gets rejected early.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ClaimRequestDto {

    /** Amount must be provided and greater than 0. */
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    private BigDecimal amount;

    /** Date when the expense happened. */
    @NotNull(message = "Date is required")
    private LocalDate date;

    /** What the expense was for. */
    @NotBlank(message = "Description is required")
    private String description;

    /**
     * The employee ID who is submitting this claim.
     * For now we pass it in the request manually
     * since we don't have login/session yet.
     */
    @NotNull(message = "Employee ID is required")
    private Long employeeId;
}