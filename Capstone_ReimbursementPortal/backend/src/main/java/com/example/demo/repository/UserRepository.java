package com.example.demo.repository;

import com.example.demo.entity.User;
import com.example.demo.enums.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for User entity database operations.
 * Extends JpaRepository to inherit standard CRUD operations.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Finds a user by their email address.
     *
     * @param email the email address to search for
     * @return Optional containing the user if found, empty otherwise
     */
    Optional<User> findByEmail(String email);

    /**
     * Checks whether a user exists with the given email address.
     *
     * @param email the email address to check
     * @return true if a user with this email exists, false otherwise
     */
    boolean existsByEmail(String email);

    /**
     * Finds all users assigned a specific role.
     *
     * @param role the role to filter users by
     * @return list of users with the specified role
     */
    List<User> findByRole(Role role);

    /**
     * Finds all employees assigned to a specific manager.
     *
     * @param manager the manager user entity
     * @return list of employees assigned to this manager
     */
    List<User> findByManager(User manager);
}