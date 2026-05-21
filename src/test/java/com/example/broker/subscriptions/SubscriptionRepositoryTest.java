package com.example.broker.subscriptions;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.broker.TestcontainersConfig;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestcontainersConfig.class)
class SubscriptionRepositoryTest {

  @Autowired SubscriptionRepository subscriptions;
  @Autowired TopicRepository topics;

  @Test
  void findByActiveTrue_returnsOnlyActive() {
    Topic orders = topics.save(new Topic("orders"));
    Subscription a = subscriptions.save(new Subscription(orders.getId(), "a", "https://a.test"));
    Subscription b = subscriptions.save(new Subscription(orders.getId(), "b", "https://b.test"));
    b.deactivate();
    subscriptions.save(b);

    List<Subscription> active = subscriptions.findByActiveTrue();

    assertThat(active).extracting(Subscription::getId).containsExactly(a.getId());
  }

  @Test
  void findByTopicIdAndActiveTrue_scopesByTopic() {
    Topic orders = topics.save(new Topic("orders"));
    Topic shipments = topics.save(new Topic("shipments"));
    subscriptions.save(new Subscription(orders.getId(), "billing", "https://x.test"));
    subscriptions.save(new Subscription(shipments.getId(), "audit", "https://y.test"));

    List<Subscription> result = subscriptions.findByTopicIdAndActiveTrue(orders.getId());

    assertThat(result).hasSize(1);
    assertThat(result.get(0).getName()).isEqualTo("billing");
  }

  @Test
  void existsByTopicIdAndName_reportsPresence() {
    Topic orders = topics.save(new Topic("orders"));
    subscriptions.save(new Subscription(orders.getId(), "billing", "https://x.test"));

    assertThat(subscriptions.existsByTopicIdAndName(orders.getId(), "billing")).isTrue();
    assertThat(subscriptions.existsByTopicIdAndName(orders.getId(), "audit")).isFalse();
  }
}
