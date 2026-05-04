package com.example.app.users;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record UserDto(
    Long id,
    @NotBlank(message = "Name must not be blank") String name,
    @Email(message = "Email must be valid") @NotBlank(message = "Email must not be blank")
        String email) {}
