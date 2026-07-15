package com.example.blogapi.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.blogapi.model.Post;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreatePostRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PostServiceTest {

    @Mock private PostRepository postRepository;
    @InjectMocks private PostService postService;

    @Test
    void createPost_success() {
        UUID authorId = UUID.randomUUID();
        CreatePostRequest request = new CreatePostRequest("Test Title", "Description");
        Post saved = new Post();
        saved.setId(UUID.randomUUID());
        saved.setTitle("Test Title");
        saved.setAuthorId(authorId);

        when(postRepository.save(any(Post.class))).thenReturn(saved);

        Post result = postService.createPost(request, authorId);

        assertThat(result.getId()).isNotNull();
        assertThat(result.getTitle()).isEqualTo("Test Title");
        verify(postRepository).save(any(Post.class));
    }

    @Test
    void createPost_titleTooShort_throwsIllegalArgument() {
        CreatePostRequest request = new CreatePostRequest("ab", "Description");

        assertThatThrownBy(() -> postService.createPost(request, UUID.randomUUID()))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("at least 3 characters");
    }

    @Test
    void getPost_found_returnsPost() {
        UUID postId = UUID.randomUUID();
        Post post = new Post();
        post.setId(postId);
        when(postRepository.findById(postId)).thenReturn(Optional.of(post));

        Post result = postService.getPost(postId);

        assertThat(result.getId()).isEqualTo(postId);
    }

    @Test
    void getPost_notFound_throwsEntityNotFound() {
        UUID missingId = UUID.randomUUID();
        when(postRepository.findById(missingId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> postService.getPost(missingId))
            .isInstanceOf(EntityNotFoundException.class)
            .hasMessageContaining(missingId.toString());
    }
}
