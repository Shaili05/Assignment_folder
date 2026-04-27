package com.example.session3.service;

import com.example.session3.model.User;
import com.example.session3.repository.UserRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> searchUsers(String name, Integer age, String role) {
        return userRepository.findAll().stream()
            .filter(u -> name == null || u.getName().equalsIgnoreCase(name))
            .filter(u -> age == null || u.getAge() == age)
            .filter(u -> role == null || u.getRole().equalsIgnoreCase(role))
            .collect(Collectors.toList());
    }

    public Optional<User> findById(int id) {
        return userRepository.findById(id);
    }

    public boolean deleteUser(int id, boolean confirm) {
        if (!confirm) return false;
        Optional<User> user = userRepository.findById(id);
        if (user.isEmpty()) return false;
        userRepository.deleteById(id);
        return true;
    }

    public User submitUser(User user) {
        return userRepository.save(user);
    }
}