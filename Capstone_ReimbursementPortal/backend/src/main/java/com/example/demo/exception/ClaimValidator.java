package com.example.demo.exception;

import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

/**
 * Validates business rules before processing a claim submission.
 * Separated from service layer to maintain single responsibility.
 */
@Component
@RequiredArgsConstructor
public class ClaimValidator {

    /** Maximum amount allowed for a single reimbursement claim. */
    private static final BigDecimal MAX_AMOUNT =
            new BigDecimal("100000");

    /** Repository used to verify employee existence. */
    private final UserRepository userRepository;

    /**
     * Validates a claim submission request.
     * Checks that the amount is within the allowed limit
     * and that the submitting employee exists in the system.
     *
     * @param dto the incoming claim submission request
     * @throws IllegalArgumentException if amount exceeds the limit
     * @throws ResourceNotFoundException if employee is not found
     */
    public void validateCreateClaim(final ClaimRequestDto dto) {
        if (dto.getAmount().compareTo(MAX_AMOUNT) > 0) {
            throw new IllegalArgumentException(
                    "Claim amount cannot exceed 100000");
        }
        if (!userRepository.existsById(dto.getEmployeeId())) {
            throw new ResourceNotFoundException(
                    "Employee not found with ID: "
                            + dto.getEmployeeId());
        }
    }
}