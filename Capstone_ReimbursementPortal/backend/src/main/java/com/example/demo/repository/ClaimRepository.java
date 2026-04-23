package com.example.demo.repository;

import com.example.demo.entity.Claim;
import com.example.demo.entity.User;
import com.example.demo.enums.ClaimStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Repository interface for Claim entity database operations.
 */
@Repository
public interface ClaimRepository extends JpaRepository<Claim, Long> {

    /**
     * Find all claims submitted by a specific employee with pagination.
     * @param employee the employee user
     * @param pageable pagination information
     * @return paginated list of claims
     */
    Page<Claim> findByEmployee(User employee, Pageable pageable);

    /**
     * Find all claims assigned to a specific reviewer with pagination.
     * @param reviewer the reviewer user
     * @param pageable pagination information
     * @return paginated list of claims
     */
    Page<Claim> findByReviewer(User reviewer, Pageable pageable);

    /**
     * Find all claims with a specific status with pagination.
     * @param status the claim status
     * @param pageable pagination information
     * @return paginated list of claims
     */
    Page<Claim> findByStatus(ClaimStatus status, Pageable pageable);
}