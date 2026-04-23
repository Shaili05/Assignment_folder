package com.example.demo.repository;

import com.example.demo.entity.User;
import com.example.demo.enums.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for User entity database operations.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Find a user by their email address.
     * @param email the email to search for
     * @return Optional containing the user if found
     */
    Optional<User> findByEmail(String email);

    /**
     * Check if a user exists with the given email.
     * @param email the email to check
     * @return true if user exists
     */
    boolean existsByEmail(String email);

    /**
     * Find all users with a specific role.
     * @param role the role to filter by
     * @return list of users with that role
     */
    List<User> findByRole(Role role);

    /**
     * Find all employees assigned to a specific manager.
     * @param manager the manager user
     * @return list of employees under that manager
     */
    List<User> findByManager(User manager);
}