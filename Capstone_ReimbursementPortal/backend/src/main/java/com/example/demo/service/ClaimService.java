package com.example.demo.service;

import com.example.demo.dto.ClaimActionRequestDto;
import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Interface for claim operations.
 * Defines what methods ClaimServiceImpl must implement.
 */
public interface ClaimService {

    /**
     * Submit a new claim.
     *
     * @param dto claim details from request
     * @return saved claim details
     */
    ClaimResponseDto submitClaim(ClaimRequestDto dto);

    /**
     * Get all claims submitted by one employee.
     *
     * @param employeeId the employee ID
     * @param pageable page and size
     * @return paginated list of claims
     */
    Page<ClaimResponseDto> getClaimsByEmployee(
            Long employeeId, Pageable pageable);

    /**
     * Approve a claim.
     *
     * @param claimId the claim to approve
     * @param dto reviewer details and optional comment
     * @return updated claim
     */
    ClaimResponseDto approveClaim(
            Long claimId, ClaimActionRequestDto dto);

    /**
     * Reject a claim.
     *
     * @param claimId the claim to reject
     * @param dto reviewer details and comment
     * @return updated claim
     */
    ClaimResponseDto rejectClaim(
            Long claimId, ClaimActionRequestDto dto);

    /**
     * Get all claims assigned to a reviewer.
     *
     * @param reviewerId the reviewer ID
     * @param pageable page and size
     * @return paginated list of claims
     */
    Page<ClaimResponseDto> getClaimsByReviewer(
            Long reviewerId, Pageable pageable);
}