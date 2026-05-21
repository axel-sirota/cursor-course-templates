package com.example.broker.subscriptions;

import com.example.broker.messages.MessageRepository;
import com.example.broker.shared.SubscriptionAlreadyExistsException;
import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import jakarta.persistence.EntityNotFoundException;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class SubscriptionService {
  private final SubscriptionRepository repository;
  private final TopicRepository topicRepository;
  private final MessageRepository messageRepository;

  public SubscriptionService(
      SubscriptionRepository repository,
      TopicRepository topicRepository,
      MessageRepository messageRepository) {
    this.repository = repository;
    this.topicRepository = topicRepository;
    this.messageRepository = messageRepository;
  }

  @Transactional
  public SubscriptionDto.Response create(String topicName, SubscriptionDto.CreateRequest request) {
    Topic topic =
        topicRepository
            .findByName(topicName)
            .orElseThrow(() -> new EntityNotFoundException("Topic not found: " + topicName));
    if (repository.existsByTopicIdAndName(topic.getId(), request.name())) {
      throw new SubscriptionAlreadyExistsException(topicName, request.name());
    }
    Long seed =
        messageRepository
            .findTopByTopicIdOrderByIdDesc(topic.getId())
            .map(m -> m.getId())
            .orElse(0L);
    Subscription subscription = new Subscription(topic.getId(), request.name(), request.webhookUrl());
    subscription.advanceCursor(seed);
    return toResponse(repository.save(subscription));
  }

  public SubscriptionDto.Response get(UUID id) {
    return repository
        .findById(id)
        .map(SubscriptionService::toResponse)
        .orElseThrow(() -> new EntityNotFoundException("Subscription not found: " + id));
  }

  @Transactional
  public void deactivate(UUID id) {
    Subscription subscription =
        repository
            .findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Subscription not found: " + id));
    subscription.deactivate();
    repository.save(subscription);
  }

  private static SubscriptionDto.Response toResponse(Subscription s) {
    return new SubscriptionDto.Response(
        s.getId(),
        s.getTopicId(),
        s.getName(),
        s.getWebhookUrl(),
        s.getLastDeliveredMessageId(),
        s.isActive(),
        s.getCreatedAt());
  }
}
