package com.example.demo.service;

import com.example.demo.dto.ClaimActionRequestDto;
import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import com.example.demo.entity.Claim;
import com.example.demo.entity.User;
import com.example.demo.enums.ClaimStatus;
import com.example.demo.enums.Role;
import com.example.demo.exception.ClaimValidator;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.mapper.ClaimMapper;
import com.example.demo.repository.ClaimRepository;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

/**
 * Service implementation for claim related business operations.
 * Handles submission, retrieval, approval and rejection of claims.
 */
@Service
@RequiredArgsConstructor
public class ClaimServiceImpl implements ClaimService {

    /** Logger for tracking service operations. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(ClaimServiceImpl.class);

    /** Repository for claim database operations. */
    private final ClaimRepository claimRepository;

    /** Repository for user database operations. */
    private final UserRepository userRepository;

    /** Validator for claim business rules. */
    private final ClaimValidator claimValidator;

    /** Mapper for converting Claim entity to response DTO. */
    private final ClaimMapper claimMapper;

    /**
     * Submits a new claim for an employee.
     * Auto assigns reviewer based on whether employee has a manager.
     * Falls back to admin if no manager is assigned.
     *
     * @param dto claim details from the request
     * @return saved claim as response DTO
     */
    @Override
    public ClaimResponseDto submitClaim(final ClaimRequestDto dto) {
        LOGGER.info("Submitting claim for employee ID: {}",
                dto.getEmployeeId());
        claimValidator.validateCreateClaim(dto);
        final User employee = userRepository.findById(dto.getEmployeeId())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: "
                                + dto.getEmployeeId()));
        final User reviewer = resolveReviewer(employee);
        final Claim claim = new Claim();
        claim.setAmount(dto.getAmount());
        claim.setDate(dto.getDate());
        claim.setDescription(dto.getDescription());
        claim.setEmployee(employee);
        claim.setReviewer(reviewer);
        claim.setStatus(ClaimStatus.SUBMITTED);
        final Claim saved = claimRepository.save(claim);
        LOGGER.info("Claim saved with ID: {}", saved.getId());
        return claimMapper.toResponseDto(saved);
    }

    /**
     * Retrieves all claims submitted by a specific employee.
     *
     * @param employeeId the ID of the employee
     * @param pageable page and size configuration
     * @return paginated list of claims
     */
    @Override
    public Page<ClaimResponseDto> getClaimsByEmployee(
            final Long employeeId, final Pageable pageable) {
        LOGGER.info("Fetching claims for employee ID: {}", employeeId);
        final User employee = userRepository.findById(employeeId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: " + employeeId));
        return claimRepository.findByEmployee(employee, pageable)
                .map(claimMapper::toResponseDto);
    }

    /**
     * Approves a submitted claim.
     * Only the assigned reviewer can approve it.
     * Comment is optional for approval.
     *
     * @param claimId ID of the claim to approve
     * @param dto reviewer ID and optional comment
     * @return updated claim with approved status
     */
    @Override
    public ClaimResponseDto approveClaim(
            final Long claimId,
            final ClaimActionRequestDto dto) {
        LOGGER.info("Approving claim ID: {}", claimId);
        final Claim claim = findSubmittedClaim(claimId);
        validateReviewer(claim, dto.getReviewerId());
        claim.setStatus(ClaimStatus.APPROVED);
        if (dto.getComment() != null
                && !dto.getComment().trim().isEmpty()) {
            claim.setReviewerComment(dto.getComment().trim());
        }
        final Claim updated = claimRepository.save(claim);
        LOGGER.info("Claim ID: {} approved successfully", claimId);
        return claimMapper.toResponseDto(updated);
    }

    /**
     * Rejects a submitted claim.
     * Only the assigned reviewer can reject it.
     * Comment is mandatory for rejection.
     *
     * @param claimId ID of the claim to reject
     * @param dto reviewer ID and rejection comment
     * @return updated claim with rejected status
     */
    @Override
    public ClaimResponseDto rejectClaim(
            final Long claimId,
            final ClaimActionRequestDto dto) {
        LOGGER.info("Rejecting claim ID: {}", claimId);
        final Claim claim = findSubmittedClaim(claimId);
        validateReviewer(claim, dto.getReviewerId());
        if (dto.getComment() == null
                || dto.getComment().trim().isEmpty()) {
            throw new IllegalArgumentException(
                    "Comment is required when rejecting a claim");
        }
        claim.setStatus(ClaimStatus.REJECTED);
        claim.setReviewerComment(dto.getComment().trim());
        final Claim updated = claimRepository.save(claim);
        LOGGER.info("Claim ID: {} rejected successfully", claimId);
        return claimMapper.toResponseDto(updated);
    }

    /**
     * Retrieves all claims assigned to a specific reviewer.
     *
     * @param reviewerId the ID of the reviewer
     * @param pageable page and size configuration
     * @return paginated list of assigned claims
     */
    @Override
    public Page<ClaimResponseDto> getClaimsByReviewer(
            final Long reviewerId, final Pageable pageable) {
        LOGGER.info("Fetching claims for reviewer ID: {}", reviewerId);
        final User reviewer = userRepository.findById(reviewerId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Reviewer not found with ID: " + reviewerId));
        return claimRepository.findByReviewer(reviewer, pageable)
                .map(claimMapper::toResponseDto);
    }

    /**
     * Resolves the reviewer for a claim.
     * Uses employee manager if assigned otherwise finds first admin.
     *
     * @param employee the employee submitting the claim
     * @return the resolved reviewer user
     */
    private User resolveReviewer(final User employee) {
        if (employee.getManager() != null) {
            return employee.getManager();
        }
        return userRepository.findByRole(Role.ADMIN)
                .stream()
                .findFirst()
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No admin found to assign as reviewer"));
    }

    /**
     * Finds a claim by ID and validates it is in SUBMITTED status.
     *
     * @param claimId the ID of the claim to find
     * @return the claim entity if found and in SUBMITTED status
     */
    private Claim findSubmittedClaim(final Long claimId) {
        final Claim claim = claimRepository.findById(claimId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Claim not found with ID: " + claimId));
        if (claim.getStatus() != ClaimStatus.SUBMITTED) {
            throw new IllegalArgumentException(
                    "Only SUBMITTED claims can be actioned");
        }
        return claim;
    }

    /**
     * Validates that the given reviewer is assigned to the claim.
     *
     * @param claim the claim being actioned
     * @param reviewerId the ID of the reviewer attempting the action
     */
    private void validateReviewer(
            final Claim claim, final Long reviewerId) {
        if (!claim.getReviewer().getId().equals(reviewerId)) {
            throw new IllegalArgumentException(
                    "You are not assigned to review this claim");
        }
    }
}