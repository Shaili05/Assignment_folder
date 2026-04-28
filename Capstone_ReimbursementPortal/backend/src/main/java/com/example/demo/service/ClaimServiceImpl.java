package com.example.demo.service;

import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import com.example.demo.entity.Claim;
import com.example.demo.entity.User;
import com.example.demo.enums.ClaimStatus;
import com.example.demo.enums.Role;
import com.example.demo.exception.ClaimValidator;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.repository.ClaimRepository;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

/**
 * Business logic for claim operations.
 * Validator is always called before touching the database.
 */
@Service
@RequiredArgsConstructor
public class ClaimServiceImpl implements ClaimService {

    /** Logger for tracking what happens in each method. */
    private static final Logger logger =
            LoggerFactory.getLogger(ClaimServiceImpl.class);

    /** Database operations for claims. */
    private final ClaimRepository claimRepository;

    /** Database operations for users. */
    private final UserRepository userRepository;

    /** Validates business rules before processing. */
    private final ClaimValidator claimValidator;

    /**
     * Submits a new claim for an employee.
     * Auto assigns reviewer based on whether employee has a manager.
     *
     * @param dto claim details from request
     * @return saved claim response
     */
    @Override
    public ClaimResponseDto submitClaim(final ClaimRequestDto dto) {
        logger.info("Submitting claim for employee ID: {}",
                dto.getEmployeeId());

        // validate first
        claimValidator.validateCreateClaim(dto);

        // get the employee
        User employee = userRepository.findById(dto.getEmployeeId())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: "
                                + dto.getEmployeeId()));

        // auto assign reviewer
        // if employee has a manager use that manager
        // otherwise find an admin
        User reviewer = employee.getManager();
        if (reviewer == null) {
            reviewer = userRepository.findAll()
                    .stream()
                    .filter(u -> u.getRole() == Role.ADMIN)
                    .findFirst()
                    .orElseThrow(() -> new ResourceNotFoundException(
                            "No admin found to assign as reviewer"));
        }

        // build the claim
        Claim claim = new Claim();
        claim.setAmount(dto.getAmount());
        claim.setDate(dto.getDate());
        claim.setDescription(dto.getDescription());
        claim.setEmployee(employee);
        claim.setReviewer(reviewer);
        claim.setStatus(ClaimStatus.SUBMITTED);

        Claim saved = claimRepository.save(claim);
        logger.info("Claim saved with ID: {}", saved.getId());

        return mapToResponse(saved);
    }

    /**
     * Gets all claims submitted by a specific employee.
     *
     * @param employeeId the employee ID
     * @param pageable page and size
     * @return paginated claims
     */
    @Override
    public Page<ClaimResponseDto> getClaimsByEmployee(
            final Long employeeId, final Pageable pageable) {
        logger.info("Fetching claims for employee ID: {}", employeeId);

        User employee = userRepository.findById(employeeId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: " + employeeId));

        return claimRepository.findByEmployee(employee, pageable)
                .map(this::mapToResponse);
    }

    /**
     * Converts Claim entity to ClaimResponseDto.
     * Never return entity directly to avoid exposing DB fields.
     *
     * @param claim the claim entity
     * @return response DTO
     */
    private ClaimResponseDto mapToResponse(final Claim claim) {
        return ClaimResponseDto.builder()
                .id(claim.getId())
                .amount(claim.getAmount())
                .date(claim.getDate())
                .description(claim.getDescription())
                .status(claim.getStatus().name())
                .reviewerComment(claim.getReviewerComment())
                .employeeName(claim.getEmployee().getName())
                .reviewerName(claim.getReviewer().getName())
                .build();
    }
}