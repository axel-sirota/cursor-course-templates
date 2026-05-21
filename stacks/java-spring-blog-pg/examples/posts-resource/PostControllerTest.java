package com.example.blog.posts;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.blog.shared.NotFoundException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PostController.class)
class PostControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;
    @MockBean PostService service;

    private PostDto sample(UUID id) {
        return new PostDto(id, "T", "B", "A", Instant.parse("2024-01-01T00:00:00Z"));
    }

    @Test
    void list_whenServiceReturnsPosts_thenReturns200WithBody() throws Exception {
        UUID id = UUID.randomUUID();
        when(service.list()).thenReturn(List.of(sample(id)));

        mvc.perform(get("/api/posts"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(id.toString()));
    }

    @Test
    void create_whenValidRequest_thenReturns201() throws Exception {
        UUID id = UUID.randomUUID();
        PostDto in = new PostDto(null, "T", "B", "A", null);
        when(service.create(any(PostDto.class))).thenReturn(sample(id));

        mvc.perform(post("/api/posts")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(in)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(id.toString()));
    }

    @Test
    void create_whenBlankFields_thenReturns400() throws Exception {
        PostDto bad = new PostDto(null, "", "", "", null);

        mvc.perform(post("/api/posts")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(bad)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void get_whenMissing_thenReturns404() throws Exception {
        UUID id = UUID.randomUUID();
        when(service.get(id)).thenThrow(new NotFoundException("post " + id));

        mvc.perform(get("/api/posts/{id}", id))
                .andExpect(status().isNotFound());
    }

    @Test
    void update_whenFound_thenReturns200WithUpdated() throws Exception {
        UUID id = UUID.randomUUID();
        PostDto in = new PostDto(null, "T2", "B2", "A2", null);
        when(service.update(eq(id), any(PostDto.class))).thenReturn(sample(id));

        mvc.perform(put("/api/posts/{id}", id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(in)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id.toString()));
    }

    @Test
    void delete_whenInvoked_thenReturns204AndDelegates() throws Exception {
        UUID id = UUID.randomUUID();

        mvc.perform(delete("/api/posts/{id}", id))
                .andExpect(status().isNoContent());

        verify(service).delete(id);
    }
}
