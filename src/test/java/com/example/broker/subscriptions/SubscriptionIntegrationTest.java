package com.example.broker.subscriptions;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.broker.TestcontainersConfig;
import com.example.broker.messages.MessageRepository;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Import(TestcontainersConfig.class)
class SubscriptionIntegrationTest {

  @Autowired TestRestTemplate http;
  @Autowired TopicRepository topics;
  @Autowired MessageRepository messages;
  @Autowired SubscriptionRepository subscriptions;

  @BeforeEach
  void seed() {
    subscriptions.deleteAll();
    messages.deleteAll();
    topics.deleteAll();
    topics.save(new Topic("orders"));
  }

  @Test
  void subscribeFromNow_seedsCursorToLatestMessageId() {
    Long lastPublishedId = null;
    for (int i = 1; i <= 5; i++) {
      ResponseEntity<?> r =
          http.postForEntity(
              "/topics/orders/messages",
              Map.of("payload", Map.of("n", i)),
              Map.class);
      assertThat(r.getStatusCode()).isEqualTo(HttpStatus.ACCEPTED);
      Object idValue = ((Map<?, ?>) r.getBody()).get("id");
      lastPublishedId = ((Number) idValue).longValue();
    }

    ResponseEntity<SubscriptionDto.Response> created =
        http.postForEntity(
            "/topics/orders/subscriptions",
            Map.of("name", "billing", "webhookUrl", "https://example.test/hook"),
            SubscriptionDto.Response.class);

    assertThat(created.getStatusCode()).isEqualTo(HttpStatus.CREATED);
    assertThat(created.getBody()).isNotNull();
    assertThat(created.getBody().lastDeliveredMessageId()).isEqualTo(lastPublishedId);

    ResponseEntity<SubscriptionDto.Response> fetched =
        http.getForEntity(
            "/subscriptions/" + created.getBody().id(), SubscriptionDto.Response.class);
    assertThat(fetched.getStatusCode()).isEqualTo(HttpStatus.OK);
    assertThat(fetched.getBody().active()).isTrue();
  }
}
