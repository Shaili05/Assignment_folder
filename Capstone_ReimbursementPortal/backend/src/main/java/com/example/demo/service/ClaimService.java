package com.example.demo.service;

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
}