package com.example.session3.repository;

import com.example.session3.model.User;
import org.springframework.stereotype.Repository;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class UserRepository {

    private final List<User> users = new ArrayList<>(List.of(
        new User(1, "Shaili Tiwari", 22, "ADMIN"),
        new User(2, "Ratna Pandey", 30, "USER"),
        new User(3, "Arpit Verma", 30, "USER"),
        new User(4, "Raj Grover", 25, "MANAGER"),
        new User(5, "Neelam Gupta", 28, "USER"),
        new User(6, "Mihir Jain", 35, "ADMIN"),
        new User(7, "Palak Shete", 22, "USER")
    ));

    public List<User> findAll() { return users; }

    public Optional<User> findById(int id) {
        return users.stream().filter(u -> u.getId() == id).findFirst();
    }

    public void deleteById(int id) {
        users.removeIf(u -> u.getId() == id);
    }

    public User save(User user) {
        users.add(user);
        return user;
    }
}