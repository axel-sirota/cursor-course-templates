package com.example.broker.subscriptions;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willThrow;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import jakarta.persistence.EntityNotFoundException;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(SubscriptionController.class)
class SubscriptionControllerTest {

  @Autowired MockMvc mockMvc;

  @MockBean SubscriptionService service;

  @Test
  void post_subscription_returns_201() throws Exception {
    UUID id = UUID.randomUUID();
    UUID topicId = UUID.randomUUID();
    given(service.create(eq("orders"), any()))
        .willReturn(
            new SubscriptionDto.Response(
                id, topicId, "billing", "https://hook.test", 5L, true, OffsetDateTime.now()));

    mockMvc
        .perform(
            post("/topics/orders/subscriptions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"billing\",\"webhookUrl\":\"https://hook.test\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").value(id.toString()))
        .andExpect(jsonPath("$.name").value("billing"))
        .andExpect(jsonPath("$.lastDeliveredMessageId").value(5));
  }

  @Test
  void post_subscription_invalidWebhookUrl_returns_400() throws Exception {
    mockMvc
        .perform(
            post("/topics/orders/subscriptions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"billing\",\"webhookUrl\":\"ftp://nope\"}"))
        .andExpect(status().isBadRequest());
  }

  @Test
  void post_subscription_unknownTopic_returns_404() throws Exception {
    willThrow(new EntityNotFoundException("Topic not found: ghost"))
        .given(service)
        .create(eq("ghost"), any());

    mockMvc
        .perform(
            post("/topics/ghost/subscriptions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"billing\",\"webhookUrl\":\"https://hook.test\"}"))
        .andExpect(status().isNotFound());
  }

  @Test
  void get_subscription_returns_200() throws Exception {
    UUID id = UUID.randomUUID();
    UUID topicId = UUID.randomUUID();
    given(service.get(id))
        .willReturn(
            new SubscriptionDto.Response(
                id, topicId, "billing", "https://hook.test", 0L, true, OffsetDateTime.now()));

    mockMvc
        .perform(get("/subscriptions/" + id))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.id").value(id.toString()));
  }

  @Test
  void delete_subscription_returns_204() throws Exception {
    UUID id = UUID.randomUUID();

    mockMvc.perform(delete("/subscriptions/" + id)).andExpect(status().isNoContent());

    verify(service).deactivate(id);
  }
}
