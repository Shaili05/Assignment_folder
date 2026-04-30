package com.example.demo.dto;

import com.example.demo.enums.ClaimStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Response DTO returned after a claim is created or fetched.
 * Entity is never returned directly to avoid exposing database fields.
 */
@Getter
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

    /** Description of the expense. */
    private String description;

    /** Current status of the claim. */
    private ClaimStatus status;

    /** Comment added by reviewer when approving or rejecting. */
    private String reviewerComment;

    /** Name of the employee who submitted this claim. */
    private String employeeName;

    /** Name of the reviewer assigned to this claim. */
    private String reviewerName;
}