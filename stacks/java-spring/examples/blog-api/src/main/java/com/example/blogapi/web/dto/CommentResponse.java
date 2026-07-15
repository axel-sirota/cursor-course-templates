package com.example.blogapi.web.dto;

import com.example.blogapi.model.Comment;
import java.time.Instant;
import java.util.UUID;

public record CommentResponse(UUID commentId, UUID postId, String content, UUID authorId, Instant createdAt) {
    public static CommentResponse from(Comment comment) {
        return new CommentResponse(
            comment.getId(),
            comment.getPostId(),
            comment.getContent(),
            comment.getAuthorId(),
            comment.getCreatedAt());
    }
}
