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
 * Extends JpaRepository to inherit standard CRUD operations.
 */
@Repository
public interface ClaimRepository extends JpaRepository<Claim, Long> {

    /**
     * Finds all claims submitted by a specific employee with pagination.
     *
     * @param employee the employee whose claims to retrieve
     * @param pageable pagination configuration
     * @return paginated list of claims for the employee
     */
    Page<Claim> findByEmployee(User employee, Pageable pageable);

    /**
     * Finds all claims assigned to a specific reviewer with pagination.
     *
     * @param reviewer the reviewer whose assigned claims to retrieve
     * @param pageable pagination configuration
     * @return paginated list of claims assigned to the reviewer
     */
    Page<Claim> findByReviewer(User reviewer, Pageable pageable);

    /**
     * Finds all claims with a specific status with pagination.
     *
     * @param status the claim status to filter by
     * @param pageable pagination configuration
     * @return paginated list of claims with the given status
     */
    Page<Claim> findByStatus(ClaimStatus status, Pageable pageable);
}