package com.example.blogapi.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.blogapi.config.SecurityConfig;
import com.example.blogapi.model.Post;
import com.example.blogapi.security.JwtAuthFilter;
import com.example.blogapi.service.PostService;
import jakarta.persistence.EntityNotFoundException;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PostController.class)
@Import(SecurityConfig.class)
class PostControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private PostService postService;
    @MockBean private JwtAuthFilter jwtAuthFilter;
    @MockBean private UserDetailsService userDetailsService;

    @Test
    void createPost_successCase_returnsCreatedPost() throws Exception {
        UUID authorId = UUID.randomUUID();
        Post saved = new Post();
        saved.setId(UUID.randomUUID());
        saved.setTitle("Test Resource");
        saved.setContent("Test description");
        saved.setAuthorId(authorId);
        saved.setCreatedAt(Instant.now());
        saved.setUpdatedAt(Instant.now());
        given(postService.createPost(any(), eq(authorId))).willReturn(saved);

        mockMvc.perform(post("/api/posts")
                .with(user(authorId.toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title":"Test Resource","content":"Test description"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.postId").exists())
            .andExpect(jsonPath("$.title").value("Test Resource"))
            .andExpect(jsonPath("$.authorId").value(authorId.toString()));
    }

    @Test
    void createPost_validationCase_blankTitleReturns400() throws Exception {
        mockMvc.perform(post("/api/posts")
                .with(user(UUID.randomUUID().toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title":"","content":"Body"}
                    """))
            .andExpect(status().isBadRequest());
    }

    @Test
    void createPost_authenticationCase_returns401WithoutUser() throws Exception {
        mockMvc.perform(post("/api/posts")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title":"Test","content":"Body"}
                    """))
            .andExpect(status().isUnauthorized());
    }

    @Test
    void getPost_successCase_returnsPost() throws Exception {
        UUID postId = UUID.randomUUID();
        Post found = new Post();
        found.setId(postId);
        found.setTitle("Existing Post");
        found.setContent("Body");
        found.setAuthorId(UUID.randomUUID());
        found.setCreatedAt(Instant.now());
        found.setUpdatedAt(Instant.now());
        given(postService.getPost(postId)).willReturn(found);

        mockMvc.perform(get("/api/posts/{id}", postId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.postId").value(postId.toString()));
    }

    @Test
    void getPost_errorCase_returns404WhenMissing() throws Exception {
        UUID missingId = UUID.randomUUID();
        given(postService.getPost(missingId))
            .willThrow(new EntityNotFoundException("Post not found: " + missingId));

        mockMvc.perform(get("/api/posts/{id}", missingId))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.detail").value("Post not found: " + missingId));
    }

    @Test
    void listPosts_successCase_returnsPagedResults() throws Exception {
        Post post = new Post();
        post.setId(UUID.randomUUID());
        post.setTitle("Paged Post");
        post.setContent("Body");
        post.setAuthorId(UUID.randomUUID());
        post.setCreatedAt(Instant.now());
        post.setUpdatedAt(Instant.now());
        Page<Post> page = new PageImpl<>(java.util.List.of(post), PageRequest.of(0, 20), 1);
        given(postService.listPosts(any())).willReturn(page);

        mockMvc.perform(get("/api/posts").param("page", "0").param("size", "20"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content[0].title").value("Paged Post"))
            .andExpect(jsonPath("$.totalElements").value(1));
    }
}
