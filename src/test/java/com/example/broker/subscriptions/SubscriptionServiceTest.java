package com.example.broker.subscriptions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.example.broker.TestcontainersConfig;
import com.example.broker.messages.MessageDto;
import com.example.broker.messages.MessageService;
import com.example.broker.shared.SubscriptionAlreadyExistsException;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import jakarta.persistence.EntityNotFoundException;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import({TestcontainersConfig.class, SubscriptionService.class, MessageService.class})
class SubscriptionServiceTest {

  @Autowired SubscriptionService service;
  @Autowired MessageService messageService;
  @Autowired TopicRepository topics;

  @BeforeEach
  void seed() {
    topics.save(new Topic("orders"));
  }

  @Test
  void create_seedsCursorToMaxMessageId() {
    Long lastId = null;
    for (int i = 1; i <= 5; i++) {
      MessageDto.Response r =
          messageService.publish(
              "orders", new MessageDto.PublishRequest(Map.of("n", i), Map.of()));
      lastId = r.id();
    }

    SubscriptionDto.Response response =
        service.create(
            "orders", new SubscriptionDto.CreateRequest("billing", "https://example.test/hook"));

    assertThat(response.lastDeliveredMessageId()).isEqualTo(lastId);
    assertThat(response.active()).isTrue();
    assertThat(response.id()).isNotNull();
  }

  @Test
  void create_duplicateNameThrowsConflict() {
    service.create(
        "orders", new SubscriptionDto.CreateRequest("billing", "https://example.test/hook"));

    assertThatThrownBy(
            () ->
                service.create(
                    "orders",
                    new SubscriptionDto.CreateRequest("billing", "https://other.test/hook")))
        .isInstanceOf(SubscriptionAlreadyExistsException.class);
  }

  @Test
  void get_missingIdThrowsEntityNotFound() {
    assertThatThrownBy(() -> service.get(UUID.randomUUID()))
        .isInstanceOf(EntityNotFoundException.class);
  }

  @Test
  void deactivate_flipsActiveFlag() {
    SubscriptionDto.Response created =
        service.create(
            "orders", new SubscriptionDto.CreateRequest("billing", "https://example.test/hook"));

    service.deactivate(created.id());

    SubscriptionDto.Response after = service.get(created.id());
    assertThat(after.active()).isFalse();
  }
}
