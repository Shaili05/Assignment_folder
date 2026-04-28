package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * This is what the API sends back after a claim is created or fetched.
 * I don't return the entity directly to keep things clean.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ClaimResponseDto {

    /** Unique ID of the claim. */
    private Long id;

    /** Amount that was claimed. */
    private BigDecimal amount;

    /** Date of the expense. */
    private LocalDate date;

    /** What the expense was for. */
    private String description;

    /** Current status - SUBMITTED, APPROVED or REJECTED. */
    private String status;

    /** Comment added by reviewer when approving or rejecting. */
    private String reviewerComment;

    /** Name of employee who submitted this claim. */
    private String employeeName;

    /** Name of reviewer assigned to this claim. */
    private String reviewerName;
}