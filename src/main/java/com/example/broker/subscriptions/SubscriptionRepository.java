package com.example.broker.subscriptions;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SubscriptionRepository extends JpaRepository<Subscription, UUID> {
  List<Subscription> findByActiveTrue();

  List<Subscription> findByTopicIdAndActiveTrue(UUID topicId);

  boolean existsByTopicIdAndName(UUID topicId, String name);
}
