package com.example.blogapi.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.example.blogapi.model.Comment;
import com.example.blogapi.repository.CommentRepository;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreateCommentRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class CommentServiceTest {

    @Mock private CommentRepository commentRepository;
    @Mock private PostRepository postRepository;
    @InjectMocks private CommentService commentService;

    @Test
    void createComment_postExists_success() {
        UUID postId = UUID.randomUUID();
        UUID authorId = UUID.randomUUID();
        CreateCommentRequest request = new CreateCommentRequest("Nice post!");
        Comment saved = new Comment();
        saved.setId(UUID.randomUUID());
        saved.setPostId(postId);
        saved.setAuthorId(authorId);
        saved.setContent("Nice post!");

        when(postRepository.existsById(postId)).thenReturn(true);
        when(commentRepository.save(any(Comment.class))).thenReturn(saved);

        Comment result = commentService.createComment(postId, request, authorId);

        assertThat(result.getContent()).isEqualTo("Nice post!");
        assertThat(result.getPostId()).isEqualTo(postId);
    }

    @Test
    void createComment_postMissing_throwsEntityNotFound() {
        UUID missingPostId = UUID.randomUUID();
        CreateCommentRequest request = new CreateCommentRequest("Nice post!");
        when(postRepository.existsById(missingPostId)).thenReturn(false);

        assertThatThrownBy(() -> commentService.createComment(missingPostId, request, UUID.randomUUID()))
            .isInstanceOf(EntityNotFoundException.class)
            .hasMessageContaining(missingPostId.toString());
    }

    @Test
    void listComments_postExists_returnsComments() {
        UUID postId = UUID.randomUUID();
        Comment comment = new Comment();
        comment.setId(UUID.randomUUID());
        comment.setPostId(postId);
        when(postRepository.existsById(postId)).thenReturn(true);
        when(commentRepository.findByPostIdOrderByCreatedAtAsc(postId)).thenReturn(List.of(comment));

        List<Comment> result = commentService.listComments(postId);

        assertThat(result).hasSize(1);
    }

    @Test
    void listComments_postMissing_throwsEntityNotFound() {
        UUID missingPostId = UUID.randomUUID();
        when(postRepository.existsById(missingPostId)).thenReturn(false);

        assertThatThrownBy(() -> commentService.listComments(missingPostId))
            .isInstanceOf(EntityNotFoundException.class);
    }
}
