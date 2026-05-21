package com.example.broker.messages;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willThrow;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import jakarta.persistence.EntityNotFoundException;
import java.time.OffsetDateTime;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PublishController.class)
class PublishControllerTest {

  @Autowired MockMvc mockMvc;

  @MockBean MessageService service;

  @Test
  void post_message_returns_202() throws Exception {
    given(service.publish(eq("orders"), any()))
        .willReturn(new MessageDto.Response(1L, "orders", OffsetDateTime.now()));

    mockMvc
        .perform(
            post("/topics/orders/messages")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"payload\":{\"orderId\":\"42\"}}"))
        .andExpect(status().isAccepted())
        .andExpect(jsonPath("$.id").value(1))
        .andExpect(jsonPath("$.topic").value("orders"));
  }

  @Test
  void post_message_unknown_topic_returns_404() throws Exception {
    willThrow(new EntityNotFoundException("Topic not found: ghost"))
        .given(service)
        .publish(eq("ghost"), any());

    mockMvc
        .perform(
            post("/topics/ghost/messages")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"payload\":{\"x\":1}}"))
        .andExpect(status().isNotFound());
  }

  @Test
  void post_message_missing_payload_returns_400() throws Exception {
    mockMvc
        .perform(
            post("/topics/orders/messages").contentType(MediaType.APPLICATION_JSON).content("{}"))
        .andExpect(status().isBadRequest());
  }
}
