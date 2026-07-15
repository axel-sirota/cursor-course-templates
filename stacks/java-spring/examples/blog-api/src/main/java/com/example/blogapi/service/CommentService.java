package com.example.blogapi.service;

import com.example.blogapi.model.Comment;
import com.example.blogapi.repository.CommentRepository;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreateCommentRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;

    /**
     * Creates a comment on an existing post.
     *
     * @param postId the post being commented on
     * @param request the comment payload
     * @param authorId the authenticated commenter's identifier
     * @return the persisted comment
     * @throws EntityNotFoundException if the post does not exist
     */
    @Transactional
    public Comment createComment(UUID postId, CreateCommentRequest request, UUID authorId) {
        if (!postRepository.existsById(postId)) {
            throw new EntityNotFoundException("Post not found: " + postId);
        }

        Comment comment = new Comment();
        comment.setPostId(postId);
        comment.setAuthorId(authorId);
        comment.setContent(request.content());

        Comment saved = commentRepository.save(comment);
        log.info("Created comment {} on post {}", saved.getId(), postId);
        return saved;
    }

    /**
     * Lists all comments for a post, oldest first.
     *
     * @param postId the post identifier
     * @return the post's comments
     * @throws EntityNotFoundException if the post does not exist
     */
    public List<Comment> listComments(UUID postId) {
        if (!postRepository.existsById(postId)) {
            throw new EntityNotFoundException("Post not found: " + postId);
        }
        return commentRepository.findByPostIdOrderByCreatedAtAsc(postId);
    }
}
