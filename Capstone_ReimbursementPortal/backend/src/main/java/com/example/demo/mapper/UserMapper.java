package com.example.demo.mapper;

import com.example.demo.dto.UserResponseDto;
import com.example.demo.entity.User;
import org.springframework.stereotype.Component;

/**
 * Mapper class for converting between User entity and DTOs.
 * Keeps mapping logic out of service classes.
 */
@Component
public final class UserMapper {

    /**
     * Private constructor to prevent instantiation.
     * This is a utility-style mapper used as a Spring component.
     */
    public UserMapper() {
    }

    /**
     * Converts a User entity to a UserResponseDto.
     * Password is never included in the response.
     *
     * @param user the user entity from database
     * @return response DTO safe to return to client
     */
    public UserResponseDto toResponseDto(final User user) {
        return UserResponseDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .role(user.getRole().name())
                .managerName(user.getManager() != null
                        ? user.getManager().getName() : null)
                .build();
    }
}