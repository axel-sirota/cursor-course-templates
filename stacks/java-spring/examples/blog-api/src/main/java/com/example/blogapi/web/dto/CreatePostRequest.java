package com.example.blogapi.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreatePostRequest(
    @NotBlank @Size(min = 3, max = 200) String title,
    @NotBlank @Size(max = 10000) String content
) {}
