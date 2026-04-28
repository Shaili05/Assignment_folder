package com.example.demo.controller;

import com.example.demo.dto.ApiResponseDto;
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
import org.springframework.web.bind.annotation.PostMapping;
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
        logger.info("Received claim submission request");
        ClaimResponseDto response = claimService.submitClaim(dto);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponseDto.success(response,
                        "Claim submitted successfully"));
    }

    /**
     * GET /api/claims/my?employeeId=1 and page=0 and size=10
     * Employee views their own claims.
     *
     * @param employeeId the employee ID
     * @param page page number
     * @param size page size
     * @return paginated list of claims
     */
    @GetMapping("/my")
    public ResponseEntity<ApiResponseDto<Page<ClaimResponseDto>>>
    getMyClaims(
            @RequestParam final Long employeeId,
            @RequestParam(defaultValue = "0") final int page,
            @RequestParam(defaultValue = "10") final int size) {
        logger.info("Fetching claims for employee ID: {}", employeeId);
        Page<ClaimResponseDto> claims =
                claimService.getClaimsByEmployee(
                        employeeId, PageRequest.of(page, size));
        return ResponseEntity.ok(
                ApiResponseDto.success(claims,
                        "Claims fetched successfully"));
    }
}