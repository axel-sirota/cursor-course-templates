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
import com.example.blogapi.model.Comment;
import com.example.blogapi.security.JwtAuthFilter;
import com.example.blogapi.service.CommentService;
import jakarta.persistence.EntityNotFoundException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(CommentController.class)
@Import(SecurityConfig.class)
class CommentControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private CommentService commentService;
    @MockBean private JwtAuthFilter jwtAuthFilter;
    @MockBean private UserDetailsService userDetailsService;

    @Test
    void createComment_successCase_returnsCreatedComment() throws Exception {
        UUID postId = UUID.randomUUID();
        UUID authorId = UUID.randomUUID();
        Comment saved = new Comment();
        saved.setId(UUID.randomUUID());
        saved.setPostId(postId);
        saved.setAuthorId(authorId);
        saved.setContent("Great post!");
        saved.setCreatedAt(Instant.now());
        given(commentService.createComment(eq(postId), any(), eq(authorId))).willReturn(saved);

        mockMvc.perform(post("/api/posts/{postId}/comments", postId)
                .with(user(authorId.toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"content":"Great post!"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content").value("Great post!"))
            .andExpect(jsonPath("$.postId").value(postId.toString()));
    }

    @Test
    void createComment_errorCase_returns404WhenPostMissing() throws Exception {
        UUID missingPostId = UUID.randomUUID();
        given(commentService.createComment(eq(missingPostId), any(), any()))
            .willThrow(new EntityNotFoundException("Post not found: " + missingPostId));

        mockMvc.perform(post("/api/posts/{postId}/comments", missingPostId)
                .with(user(UUID.randomUUID().toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"content":"Great post!"}
                    """))
            .andExpect(status().isNotFound());
    }

    @Test
    void createComment_validationCase_blankContentReturns400() throws Exception {
        mockMvc.perform(post("/api/posts/{postId}/comments", UUID.randomUUID())
                .with(user(UUID.randomUUID().toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"content":""}
                    """))
            .andExpect(status().isBadRequest());
    }

    @Test
    void listComments_successCase_returnsComments() throws Exception {
        UUID postId = UUID.randomUUID();
        Comment comment = new Comment();
        comment.setId(UUID.randomUUID());
        comment.setPostId(postId);
        comment.setAuthorId(UUID.randomUUID());
        comment.setContent("Nice!");
        comment.setCreatedAt(Instant.now());
        given(commentService.listComments(postId)).willReturn(List.of(comment));

        mockMvc.perform(get("/api/posts/{postId}/comments", postId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].content").value("Nice!"));
    }
}
