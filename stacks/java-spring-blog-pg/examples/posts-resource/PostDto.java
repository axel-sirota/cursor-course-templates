package com.example.blog.posts;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.time.Instant;
import java.util.UUID;

public record PostDto(
        UUID id,
        @NotBlank @Size(max = 200) String title,
        @NotBlank String body,
        @NotBlank String author,
        Instant createdAt) {}
