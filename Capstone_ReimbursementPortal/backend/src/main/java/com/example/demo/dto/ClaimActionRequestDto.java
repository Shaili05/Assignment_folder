package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Used when a reviewer approves or rejects a claim.
 * Comment is optional for approval but required for rejection.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ClaimActionRequestDto {

    /** Reviewer ID who is taking action on the claim. */
    private Long reviewerId;

    /** Optional comment explaining the decision. */
    private String comment;
}