package com.example.demo.exception;

import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

/**
 * Validates business rules before processing a claim.
 * Kept separate from service just like UserValidator.
 */
@Component
@RequiredArgsConstructor
public class ClaimValidator {

    /** Max amount allowed for a single claim. */
    private static final BigDecimal MAX_AMOUNT
            = new BigDecimal("100000");

    /** Used to check if employee exists. */
    private final UserRepository userRepository;

    /**
     * Validates claim before submission.
     * Checks amount limit and employee existence.
     *
     * @param dto the incoming claim request
     */
    public void validateCreateClaim(final ClaimRequestDto dto) {

        // check amount is within limit
        if (dto.getAmount().compareTo(MAX_AMOUNT) > 0) {
            throw new IllegalArgumentException(
                    "Claim amount cannot exceed 100000");
        }

        // check employee exists
        if (!userRepository.existsById(dto.getEmployeeId())) {
            throw new ResourceNotFoundException(
                    "Employee not found with ID: "
                            + dto.getEmployeeId());
        }
    }
}