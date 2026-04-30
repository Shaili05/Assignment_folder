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
 * Handles all HTTP requests for claim operations.
 * Delegates actual work to ClaimService.
 */
@RestController
@RequestMapping("/api/claims")
@RequiredArgsConstructor
public class ClaimController {

    /** Logger for tracking incoming requests. */
    private static final Logger logger =
            LoggerFactory.getLogger(ClaimController.class);

    /** Service that handles claim business logic. */
    private final ClaimService claimService;

    /**
     * POST /api/claims
     * Employee submits a new claim.
     *
     * @param dto claim details from request body
     * @return created claim with 201 status
     */
    @PostMapping
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> submitClaim(
            @Valid @RequestBody final ClaimRequestDto dto) {
        logger.info("Received claim submission request for employee ID: {}",
                dto.getEmployeeId());
        ClaimResponseDto response = claimService.submitClaim(dto);
        logger.info("Claim submission completed. Claim ID: {}",
                response.getId());
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponseDto.success(response,
                        "Claim submitted successfully"));
    }

    /**
     * GET /api/claims/employee-claims?employeeId=1&page=0&size=10
     * Employee views their own submitted claims.
     *
     * @param employeeId the employee ID
     * @param page page number
     * @param size page size
     * @return paginated list of claims
     */
    @GetMapping("/employee-claims")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getEmployeeClaims(
            @RequestParam final Long employeeId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        logger.info("Fetching claims for employee ID: {}", employeeId);
        Page<ClaimResponseDto> claims =
                claimService.getClaimsByEmployee(
                        employeeId, PageRequest.of(page, size));
        logger.info("Fetched {} claims for employee ID: {}",
                claims.getTotalElements(), employeeId);
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Claims fetched successfully"));
    }

    /**
     * PUT /api/claims/{id}/approve
     * Reviewer approves a claim.
     *
     * @param id the claim ID
     * @param dto reviewer ID and optional comment
     * @return updated claim
     */
    @PutMapping("/{id}/approve")
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> approveClaim(
            @PathVariable final Long id,
            @RequestBody final ClaimActionRequestDto dto) {
        logger.info("Approve request received for claim ID: {}", id);
        ClaimResponseDto response = claimService.approveClaim(id, dto);
        logger.info("Claim ID: {} approved successfully", id);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Claim approved successfully"));
    }

    /**
     * PUT /api/claims/{id}/reject
     * Reviewer rejects a claim.
     *
     * @param id the claim ID
     * @param dto reviewer ID and comment
     * @return updated claim
     */
    @PutMapping("/{id}/reject")
    public ResponseEntity<ApiResponseDto<ClaimResponseDto>> rejectClaim(
            @PathVariable final Long id,
            @RequestBody final ClaimActionRequestDto dto) {
        logger.info("Reject request received for claim ID: {}", id);
        ClaimResponseDto response = claimService.rejectClaim(id, dto);
        logger.info("Claim ID: {} rejected successfully", id);
        return ResponseEntity.ok(
                ApiResponseDto.success(response,
                        "Claim rejected successfully"));
    }

    /**
     * GET /api/claims/reviewer-claims?reviewerId=1&page=0&size=10
     * Reviewer views all claims assigned to them.
     *
     * @param reviewerId the reviewer ID
     * @param page page number
     * @param size page size
     * @return paginated list of claims
     */
    @GetMapping("/reviewer-claims")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getReviewerClaims(
            @RequestParam final Long reviewerId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        logger.info("Fetching claims for reviewer ID: {}", reviewerId);
        Page<ClaimResponseDto> claims =
                claimService.getClaimsByReviewer(
                        reviewerId, PageRequest.of(page, size));
        logger.info("Fetched {} claims for reviewer ID: {}",
                claims.getTotalElements(), reviewerId);
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Claims fetched successfully"));
    }
}