package com.example.demo.controller;

import com.example.demo.dto.ApiResponseDto;
import com.example.demo.dto.ClaimActionRequestDto;
import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import com.example.demo.service.ClaimService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller for claim management operations.
 * Handles submission, retrieval, approval and rejection of claims.
 */
@RestController
@RequestMapping("/api/claims")
@RequiredArgsConstructor
public class ClaimController {

    /** Logger for tracking incoming requests and responses. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(ClaimController.class);

    /** Default page size for paginated responses. */
    private static final int DEFAULT_PAGE_SIZE = 10;

    /** Service layer handling claim business logic. */
    private final ClaimService claimService;

    /**
     * POST /api/claims
     * Submits a new reimbursement claim for an employee.
     *
     * @param dto claim details from the request body
     * @return 201 response with the created claim details
     */
    @PostMapping
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> submitClaim(
            @Valid @RequestBody final ClaimRequestDto dto) {
        LOGGER.info("Request received - POST /api/claims for employee: {}",
                dto.getEmployeeId());
        final ClaimResponseDto response = claimService.submitClaim(dto);
        LOGGER.info("Request completed - Claim created with ID: {}",
                response.getId());
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponseDto.success(response,
                        "Claim submitted successfully"));
    }

    /**
     * GET /api/claims/employee-claims?employeeId=1 and page=0 and size=10
     * Retrieves all claims submitted by a specific employee.
     *
     * @param employeeId the employee ID to filter claims by
     * @param page page number to fetch, defaults to 0
     * @param size number of records per page, defaults to 10
     * @return paginated list of employee claims
     */
    @GetMapping("/employee-claims")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getEmployeeClaims(
            @RequestParam final Long employeeId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(
                    defaultValue = "10") final int size) {
        LOGGER.info("Request received - GET employee-claims"
                + " for employee: {}", employeeId);
        final Page<ClaimResponseDto> claims =
                claimService.getClaimsByEmployee(
                        employeeId, PageRequest.of(page, size));
        LOGGER.info("Request completed - Returned {} claims",
                claims.getTotalElements());
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Claims fetched successfully"));
    }

    /**
     * PUT /api/claims/{id}/approve
     * Approves a submitted claim.
     *
     * @param id the claim ID from the URL path
     * @param dto reviewer ID and optional comment
     * @return updated claim with approved status
     */
    @PutMapping("/{id}/approve")
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> approveClaim(
            @PathVariable final Long id,
            @RequestBody final ClaimActionRequestDto dto) {
        LOGGER.info("Request received - PUT approve claim ID: {}", id);
        final ClaimResponseDto response =
                claimService.approveClaim(id, dto);
        LOGGER.info("Request completed - Claim ID: {} approved", id);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Claim approved successfully"));
    }

    /**
     * PUT /api/claims/{id}/reject
     * Rejects a submitted claim.
     *
     * @param id the claim ID from the URL path
     * @param dto reviewer ID and rejection comment
     * @return updated claim with rejected status
     */
    @PutMapping("/{id}/reject")
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> rejectClaim(
            @PathVariable final Long id,
            @RequestBody final ClaimActionRequestDto dto) {
        LOGGER.info("Request received - PUT reject claim ID: {}", id);
        final ClaimResponseDto response =
                claimService.rejectClaim(id, dto);
        LOGGER.info("Request completed - Claim ID: {} rejected", id);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Claim rejected successfully"));
    }

    /**
     * GET /api/claims/reviewer-claims?reviewerId=1 and page=0 and size=10
     * Retrieves all claims assigned to a specific reviewer.
     *
     * @param reviewerId the reviewer ID to filter claims by
     * @param page page number to fetch, defaults to 0
     * @param size number of records per page, defaults to 10
     * @return paginated list of reviewer assigned claims
     */
    @GetMapping("/reviewer-claims")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getReviewerClaims(
            @RequestParam final Long reviewerId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(
                    defaultValue = "10") final int size) {
        LOGGER.info("Request received - GET reviewer-claims"
                + " for reviewer: {}", reviewerId);
        final Page<ClaimResponseDto> claims =
                claimService.getClaimsByReviewer(
                        reviewerId, PageRequest.of(page, size));
        LOGGER.info("Request completed - Returned {} claims",
                claims.getTotalElements());
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Claims fetched successfully"));
    }

    /**
     * GET /api/claims/manager-own-claims?managerId=1
     * Retrieves claims submitted by the manager themselves as employee.
     *
     * @param managerId the manager ID
     * @param page page number
     * @param size page size
     * @return paginated list of manager own claims
     */
    @GetMapping("/manager-own-claims")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getManagerOwnClaims(
            @RequestParam final Long managerId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        LOGGER.info("Request received - GET manager-own-claims"
                + " for manager: {}", managerId);
        final Page<ClaimResponseDto> claims =
                claimService.getClaimsByEmployee(
                        managerId, PageRequest.of(page, size));
        LOGGER.info("Request completed - Returned {} claims",
                claims.getTotalElements());
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Manager own claims fetched successfully"));
    }
}