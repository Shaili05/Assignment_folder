package com.example.demo.service;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import com.example.demo.entity.Claim;
import com.example.demo.entity.User;
import com.example.demo.enums.ClaimStatus;
import com.example.demo.enums.Role;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.exception.UserValidator;
import com.example.demo.mapper.UserMapper;
import com.example.demo.repository.ClaimRepository;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Service implementation for user related business operations.
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    /** Logger for tracking service operations. */
    private static final Logger LOGGER =
            LoggerFactory.getLogger(UserServiceImpl.class);

    /** Repository for user database operations. */
    private final UserRepository userRepository;

    /** Repository for claim database operations. */
    private final ClaimRepository claimRepository;

    /** Validator for user business rules. */
    private final UserValidator userValidator;

    /** Encoder for hashing passwords before storage. */
    private final PasswordEncoder passwordEncoder;

    /** Mapper for converting User entity to response DTO. */
    private final UserMapper userMapper;

    /**
     * Creates a new user after validating input.
     * Only one admin is allowed in the system.
     *
     * @param dto incoming request data with user details
     * @return saved user details without password
     */
    @Override
    public UserResponseDto createUser(final UserRequestDto dto) {
        LOGGER.info("Creating user with email: {}", dto.getEmail());
        userValidator.validateCreateUser(dto);

        final Role role = Role.valueOf(dto.getRole().toUpperCase());

        if (role == Role.ADMIN) {
            final boolean adminExists = !userRepository
                    .findByRole(Role.ADMIN).isEmpty();
            if (adminExists) {
                throw new IllegalArgumentException(
                        "An admin already exists. "
                                + "Only one admin is allowed.");
            }
        }

        final User user = new User();
        user.setName(dto.getName());
        user.setEmail(dto.getEmail());
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setRole(role);
        final User savedUser = userRepository.save(user);
        LOGGER.info("User created with ID: {}", savedUser.getId());
        return userMapper.toResponseDto(savedUser);
    }

    /**
     * Deletes a user by ID.
     * Manager: reassigns employees to admin, reassigns pending
     * reviewer claims to admin, deletes manager's own claims,
     * then deletes the manager.
     * Employee: deletes all their claims, then deletes employee.
     *
     * @param id user ID to delete
     */
    @Override
    @Transactional
    public void deleteUser(final Long id) {
        LOGGER.info("Deleting user with ID: {}", id);

        final User userToDelete = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "User not found with ID: " + id));

        if (userToDelete.getRole() == Role.ADMIN) {
            throw new IllegalArgumentException(
                    "Admin cannot be deleted.");
        }

        final User admin = userRepository
                .findByRole(Role.ADMIN)
                .stream()
                .findFirst()
                .orElse(null);

        if (userToDelete.getRole() == Role.MANAGER) {

            // Reassign all employees of this manager to admin
            final List<User> employees =
                    userRepository.findByManager(userToDelete);
            for (User emp : employees) {
                emp.setManager(admin);
            }
            userRepository.saveAll(employees);
            userRepository.flush();

            // Reassign pending reviewer claims to admin
            final List<Claim> reviewerClaims =
                    claimRepository.findByReviewer(
                                    userToDelete,
                                    PageRequest.of(0, Integer.MAX_VALUE))
                            .getContent()
                            .stream()
                            .filter(c -> c.getStatus()
                                    == ClaimStatus.SUBMITTED)
                            .toList();

            if (admin != null) {
                for (Claim claim : reviewerClaims) {
                    claim.setReviewer(admin);
                }
                claimRepository.saveAll(reviewerClaims);
                claimRepository.flush();
            }

            LOGGER.info("Manager ID {} - {} employees and "
                            + "{} reviewer claims reassigned to admin.",
                    id, employees.size(), reviewerClaims.size());
        }

        // Delete all claims where this user is the employee
        // Works for both MANAGER and EMPLOYEE roles
        final List<Claim> ownClaims =
                claimRepository.findByEmployee(
                                userToDelete,
                                PageRequest.of(0, Integer.MAX_VALUE))
                        .getContent();

        claimRepository.deleteAll(ownClaims);
        claimRepository.flush();
        LOGGER.info("User ID {} - {} own claims deleted.",
                id, ownClaims.size());

        userRepository.deleteById(id);
        LOGGER.info("User deleted with ID: {}", id);
    }

    /**
     * Retrieves all users with pagination.
     *
     * @param pageable page number and size configuration
     * @return one page of user response DTOs
     */
    @Override
    public Page<UserResponseDto> getAllUsers(final Pageable pageable) {
        LOGGER.info("Fetching users - page: {}, size: {}",
                pageable.getPageNumber(), pageable.getPageSize());
        return userRepository.findAll(pageable)
                .map(userMapper::toResponseDto);
    }

    /**
     * Assigns a manager to an employee.
     * Moves all pending claims to new manager automatically.
     *
     * @param employeeId ID of the employee to update
     * @param managerId  ID of the manager to assign
     * @return updated employee response DTO
     */
    @Override
    public UserResponseDto assignManager(
            final Long employeeId, final Long managerId) {
        LOGGER.info("Assigning manager {} to employee {}",
                managerId, employeeId);

        final User employee = userRepository.findById(employeeId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Employee not found with ID: "
                                + employeeId));

        final User manager = userRepository.findById(managerId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Manager not found with ID: "
                                + managerId));

        if (manager.getRole() != Role.MANAGER) {
            throw new IllegalArgumentException(
                    "Only a user with MANAGER role can be assigned.");
        }

        employee.setManager(manager);
        final User updated = userRepository.save(employee);

        final List<Claim> pendingClaims =
                claimRepository.findByEmployee(
                                employee,
                                PageRequest.of(0, Integer.MAX_VALUE))
                        .getContent()
                        .stream()
                        .filter(c -> c.getStatus()
                                == ClaimStatus.SUBMITTED)
                        .toList();

        for (Claim claim : pendingClaims) {
            claim.setReviewer(manager);
        }
        claimRepository.saveAll(pendingClaims);

        LOGGER.info("Manager assigned to employee ID: {}",
                employeeId);
        return userMapper.toResponseDto(updated);
    }
}