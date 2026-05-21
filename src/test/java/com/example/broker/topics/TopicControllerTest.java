package com.example.broker.topics;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willThrow;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.broker.shared.TopicAlreadyExistsException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(TopicController.class)
class TopicControllerTest {

  @Autowired MockMvc mockMvc;

  @Autowired ObjectMapper objectMapper;

  @MockitoBean TopicService service;

  @Test
  void create_whenValidRequest_thenReturns201() throws Exception {
    TopicDto.Response response =
        new TopicDto.Response(UUID.randomUUID(), "orders", OffsetDateTime.now());
    given(service.create(any())).willReturn(response);

    mockMvc
        .perform(
            post("/topics")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"orders\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.name").value("orders"))
        .andExpect(jsonPath("$.id").exists());
  }

  @Test
  void create_whenBlankName_thenReturns400() throws Exception {
    mockMvc
        .perform(post("/topics").contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"\"}"))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.details").isArray());
  }

  @Test
  void create_whenPatternViolation_thenReturns400() throws Exception {
    mockMvc
        .perform(
            post("/topics")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"BAD NAME\"}"))
        .andExpect(status().isBadRequest());
  }

  @Test
  void create_whenDuplicate_thenReturns409() throws Exception {
    willThrow(new TopicAlreadyExistsException("orders")).given(service).create(any());

    mockMvc
        .perform(
            post("/topics")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"orders\"}"))
        .andExpect(status().isConflict());
  }

  @Test
  void list_whenTopicsExist_thenReturnsArray() throws Exception {
    given(service.list())
        .willReturn(
            List.of(
                new TopicDto.Response(UUID.randomUUID(), "alpha", OffsetDateTime.now()),
                new TopicDto.Response(UUID.randomUUID(), "zeta", OffsetDateTime.now())));

    mockMvc
        .perform(get("/topics"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(2))
        .andExpect(jsonPath("$[0].name").value("alpha"))
        .andExpect(jsonPath("$[1].name").value("zeta"));
  }
}
