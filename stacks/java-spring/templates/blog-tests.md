# Blog API — Tests Template

Test layers for the posts/comments/users domain: `@WebMvcTest` controller tests, Mockito
service unit tests, and a Testcontainers-backed integration test.

## src/test/java/.../web/PostControllerTest.java

```java
package com.example.blogapi.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.example.blogapi.model.Post;
import com.example.blogapi.service.PostService;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PostController.class)
class PostControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private PostService postService;

    @Test
    void createPost_successCase_returnsCreatedPost() throws Exception {
        UUID authorId = UUID.randomUUID();
        Post saved = new Post();
        saved.setId(UUID.randomUUID());
        saved.setTitle("Test Resource");
        saved.setContent("Test description");
        saved.setAuthorId(authorId);
        saved.setCreatedAt(Instant.now());
        given(postService.createPost(any(), eq(authorId))).willReturn(saved);

        mockMvc.perform(post("/api/posts")
                .with(user(authorId.toString()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"title":"Test Resource","content":"Test description"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.postId").exists())
            .andExpect(jsonPath("$.title").value("Test Resource"));
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
    void getPost_errorCase_returns404WhenMissing() throws Exception {
        UUID missingId = UUID.randomUUID();
        given(postService.getPost(missingId))
            .willThrow(new jakarta.persistence.EntityNotFoundException("Post not found: " + missingId));

        mockMvc.perform(get("/api/posts/{id}", missingId))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.detail").value("Post not found: " + missingId));
    }
}
```

## src/test/java/.../service/PostServiceTest.java

```java
package com.example.blogapi.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.blogapi.model.Post;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreatePostRequest;
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
        CreatePostRequest request = new CreatePostRequest("Test", "Description");
        Post saved = new Post();
        saved.setId(UUID.randomUUID());
        saved.setTitle("Test");
        saved.setAuthorId(authorId);

        when(postRepository.save(any(Post.class))).thenReturn(saved);

        Post result = postService.createPost(request, authorId);

        assertThat(result.getId()).isNotNull();
        assertThat(result.getTitle()).isEqualTo("Test");
        verify(postRepository).save(any(Post.class));
    }

    @Test
    void createPost_titleTooShort_throwsIllegalArgument() {
        CreatePostRequest request = new CreatePostRequest("ab", "Description");

        assertThatThrownBy(() -> postService.createPost(request, UUID.randomUUID()))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("at least 3 characters");
    }
}
```

## src/test/java/.../integration/PostIntegrationTest.java

```java
package com.example.blogapi.integration;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.blogapi.web.dto.CreatePostRequest;
import com.example.blogapi.web.dto.PostResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.UUID;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class PostIntegrationTest extends AbstractIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createPost_persistsToDatabase() {
        CreatePostRequest request = new CreatePostRequest("Integration Test", "Body");

        ResponseEntity<PostResponse> response = restTemplate
            .withBasicAuth("test-user", "n/a")
            .postForEntity("/api/posts", request, PostResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().postId()).isNotNull();
    }
}
```

## src/test/java/.../integration/AbstractIntegrationTest.java

A shared base class (analog of `conftest.py`) so every integration test class shares one
Testcontainers instance instead of booting Postgres per class:

```java
package com.example.blogapi.integration;

import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
public abstract class AbstractIntegrationTest {

    @Container
    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
    }
}
```

## Test Layer Summary

| File | Layer | DB | Purpose |
|------|-------|----|---------|
| `PostControllerTest` | `@WebMvcTest` | Mocked (`@MockBean`) | Request/response mapping, validation, auth, status codes |
| `PostServiceTest` | Mockito unit | Mocked (`@Mock`) | Business rule branches without a Spring context |
| `PostIntegrationTest` | `@SpringBootTest` + Testcontainers | Real Postgres | Full stack: controller → service → repository → DB |

Run everything with `./mvnw test`; run only the fast layers during active development with
`./mvnw test -Dtest=PostControllerTest,PostServiceTest`.
