package com.example.demo.service;

import com.example.demo.dto.ClaimActionRequestDto;
import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Interface defining the contract for claim business operations.
 * Implemented by ClaimServiceImpl.
 */
public interface ClaimService {

    /**
     * Submits a new reimbursement claim for an employee.
     *
     * @param dto claim details from the request
     * @return saved claim details as response DTO
     */
    ClaimResponseDto submitClaim(ClaimRequestDto dto);

    /**
     * Retrieves all claims submitted by a specific employee.
     *
     * @param employeeId the ID of the employee
     * @param pageable page number and size configuration
     * @return paginated list of employee claims
     */
    Page<ClaimResponseDto> getClaimsByEmployee(
            Long employeeId, Pageable pageable);

    /**
     * Approves a submitted claim.
     *
     * @param claimId the ID of the claim to approve
     * @param dto reviewer ID and optional comment
     * @return updated claim with approved status
     */
    ClaimResponseDto approveClaim(
            Long claimId, ClaimActionRequestDto dto);

    /**
     * Rejects a submitted claim.
     *
     * @param claimId the ID of the claim to reject
     * @param dto reviewer ID and rejection comment
     * @return updated claim with rejected status
     */
    ClaimResponseDto rejectClaim(
            Long claimId, ClaimActionRequestDto dto);

    /**
     * Retrieves all claims assigned to a specific reviewer.
     *
     * @param reviewerId the ID of the reviewer
     * @param pageable page number and size configuration
     * @return paginated list of claims assigned to reviewer
     */
    Page<ClaimResponseDto> getClaimsByReviewer(
            Long reviewerId, Pageable pageable);
}