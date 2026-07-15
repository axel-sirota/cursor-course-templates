package com.example.blogapi.service;

import com.example.blogapi.model.User;
import com.example.blogapi.repository.UserRepository;
import com.example.blogapi.web.dto.RegisterRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Registers a new user.
     *
     * @param request the registration payload
     * @return the persisted user with a generated id
     * @throws IllegalArgumentException if the email is already registered
     */
    @Transactional
    public User register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new IllegalArgumentException("Email already registered: " + request.email());
        }

        User user = new User();
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());

        User saved = userRepository.save(user);
        log.info("Registered user {}", saved.getId());
        return saved;
    }

    /**
     * Finds a user by email.
     *
     * @param email the user's email
     * @return the matching user
     * @throws IllegalArgumentException if no user has that email
     */
    public User findByEmailOrThrow(String email) {
        return userRepository.findByEmail(email)
            .orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));
    }
}
