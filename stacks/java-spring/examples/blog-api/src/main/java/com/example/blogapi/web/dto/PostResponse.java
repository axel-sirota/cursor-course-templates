package com.example.blogapi.web.dto;

import com.example.blogapi.model.Post;
import java.time.Instant;
import java.util.UUID;

public record PostResponse(
    UUID postId,
    String title,
    String content,
    UUID authorId,
    Instant createdAt,
    Instant updatedAt
) {
    public static PostResponse from(Post post) {
        return new PostResponse(
            post.getId(),
            post.getTitle(),
            post.getContent(),
            post.getAuthorId(),
            post.getCreatedAt(),
            post.getUpdatedAt());
    }
}
