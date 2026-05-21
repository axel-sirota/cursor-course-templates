package com.example.broker.messages;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.broker.TestcontainersConfig;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import java.util.List;
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
class PublishIntegrationTest {

  @Autowired TestRestTemplate http;
  @Autowired TopicRepository topics;
  @Autowired MessageRepository messages;

  @BeforeEach
  void seed() {
    messages.deleteAll();
    topics.deleteAll();
    topics.save(new Topic("orders"));
  }

  @Test
  void posts_three_messages_then_repository_has_three_rows() {
    for (int i = 1; i <= 3; i++) {
      ResponseEntity<MessageDto.Response> response =
          http.postForEntity(
              "/topics/orders/messages",
              Map.of("payload", Map.of("n", i)),
              MessageDto.Response.class);
      assertThat(response.getStatusCode()).isEqualTo(HttpStatus.ACCEPTED);
      assertThat(response.getBody()).isNotNull();
      assertThat(response.getBody().id()).isNotNull();
    }

    List<Message> all = messages.findAll();
    assertThat(all).hasSize(3);
    assertThat(all).isSortedAccordingTo((a, b) -> Long.compare(a.getId(), b.getId()));
  }
}
