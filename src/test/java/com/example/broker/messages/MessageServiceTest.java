package com.example.broker.messages;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.example.broker.TestcontainersConfig;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import jakarta.persistence.EntityNotFoundException;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import({TestcontainersConfig.class, MessageService.class})
class MessageServiceTest {

  @Autowired MessageService service;

  @Autowired TopicRepository topics;

  @BeforeEach
  void seed() {
    topics.save(new Topic("orders"));
  }

  @Test
  void publish_returns_response_with_id() {
    MessageDto.Response response =
        service.publish("orders", new MessageDto.PublishRequest(Map.of("orderId", "42"), Map.of()));

    assertThat(response.id()).isNotNull().isGreaterThan(0L);
    assertThat(response.topic()).isEqualTo("orders");
    assertThat(response.publishedAt()).isNotNull();
  }

  @Test
  void publish_to_unknown_topic_throws() {
    assertThatThrownBy(
            () ->
                service.publish(
                    "does-not-exist", new MessageDto.PublishRequest(Map.of("k", "v"), Map.of())))
        .isInstanceOf(EntityNotFoundException.class);
  }

  @Test
  void publish_assigns_strictly_increasing_ids() {
    MessageDto.Response first =
        service.publish("orders", new MessageDto.PublishRequest(Map.of("n", 1), Map.of()));
    MessageDto.Response second =
        service.publish("orders", new MessageDto.PublishRequest(Map.of("n", 2), Map.of()));

    assertThat(second.id()).isGreaterThan(first.id());
  }
}
