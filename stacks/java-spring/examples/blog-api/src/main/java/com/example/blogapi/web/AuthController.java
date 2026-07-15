package com.example.blogapi.web;

import com.example.blogapi.model.User;
import com.example.blogapi.security.JwtService;
import com.example.blogapi.service.UserService;
import com.example.blogapi.web.dto.AuthResponse;
import com.example.blogapi.web.dto.LoginRequest;
import com.example.blogapi.web.dto.RegisterRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    /** Registers a new user and returns an access token. */
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        User user = userService.register(request);
        String token = jwtService.generateToken(user.getId());
        return ResponseEntity.ok(new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName()));
    }

    /** Authenticates an existing user and returns an access token. */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.email(), request.password()));
        User user = userService.findByEmailOrThrow(request.email());
        String token = jwtService.generateToken(user.getId());
        return ResponseEntity.ok(new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName()));
    }
}
