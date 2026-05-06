package com.example.demo.dto;

import com.example.demo.enums.ClaimStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Response DTO returned after a claim is created or fetched.
 * Entity is never returned directly to avoid exposing database internals.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ClaimResponseDto {

    /** Unique identifier of the claim. */
    private Long id;

    /** Amount that was claimed by the employee. */
    private BigDecimal amount;

    /** Date when the expense was incurred. */
    private LocalDate date;

    /** Description of the expense submitted by the employee. */
    private String description;

    /** Current status of the claim in the workflow. */
    private ClaimStatus status;

    /** Comment added by the reviewer upon approval or rejection. */
    private String reviewerComment;

    /** Full name of the employee who submitted this claim. */
    private String employeeName;

    /** Full name of the reviewer assigned to this claim. */
    private String reviewerName;
}