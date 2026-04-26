package com.example.demo.repository;

import com.example.demo.model.User;
import org.springframework.stereotype.Repository;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class UserRepository {

    private final List<User> users = new ArrayList<>(List.of(
        new User(1, "Shaili", "shaili@example.com"),
        new User(2, "Ratna", "ratna@example.com"),
        new User(3, "Mihir", "mihir@example.com")
    ));

    public List<User> findAll() {
        return users;
    }

    public Optional<User> findById(int id) {
        return users.stream().filter(u -> u.getId() == id).findFirst();
    }

    public User save(User user) {
        users.add(user);
        return user;
    }
}