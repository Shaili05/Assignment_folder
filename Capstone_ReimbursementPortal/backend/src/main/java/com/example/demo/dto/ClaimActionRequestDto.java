package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Request DTO used when a reviewer approves or rejects a claim.
 * Comment is mandatory for rejection and optional for approval.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ClaimActionRequestDto {

    /** ID of the reviewer taking action on the claim. */
    private Long reviewerId;

    /** Comment explaining the approval or rejection decision. */
    private String comment;
}