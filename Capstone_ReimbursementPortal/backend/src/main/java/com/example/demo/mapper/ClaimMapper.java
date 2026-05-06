package com.example.demo.mapper;

import com.example.demo.dto.ClaimResponseDto;
import com.example.demo.entity.Claim;
import org.springframework.stereotype.Component;

/**
 * Mapper class for converting between Claim entity and DTOs.
 * Keeps mapping logic out of service classes.
 */
@Component
public final class ClaimMapper {

    /**
     * Private constructor to prevent instantiation.
     * This is a utility-style mapper used as a Spring component.
     */
    public ClaimMapper() {
    }

    /**
     * Converts a Claim entity to a ClaimResponseDto.
     * Entity is never returned directly to avoid exposing DB fields.
     * Handles null employee and reviewer gracefully.
     *
     * @param claim the claim entity from database
     * @return response DTO safe to return to client
     */
    public ClaimResponseDto toResponseDto(final Claim claim) {
        final String employeeName = claim.getEmployee() != null
                ? claim.getEmployee().getName()
                : "(Deleted)";

        final String reviewerName = claim.getReviewer() != null
                ? claim.getReviewer().getName()
                : null;

        return ClaimResponseDto.builder()
                .id(claim.getId())
                .amount(claim.getAmount())
                .date(claim.getDate())
                .description(claim.getDescription())
                .status(claim.getStatus())
                .reviewerComment(claim.getReviewerComment())
                .employeeName(employeeName)
                .reviewerName(reviewerName)
                .build();
    }
}