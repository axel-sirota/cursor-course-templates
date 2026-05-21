package com.example.broker.subscriptions;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "subscriptions")
public class Subscription {
  @Id @GeneratedValue private UUID id;

  @Column(name = "topic_id", nullable = false)
  private UUID topicId;

  @Column(nullable = false)
  private String name;

  @Column(name = "webhook_url", nullable = false)
  private String webhookUrl;

  @Column(name = "last_delivered_message_id", nullable = false)
  private Long lastDeliveredMessageId = 0L;

  @Column(nullable = false)
  private boolean active = true;

  @Column(name = "created_at", nullable = false)
  private OffsetDateTime createdAt;

  protected Subscription() {}

  public Subscription(UUID topicId, String name, String webhookUrl) {
    this.topicId = topicId;
    this.name = name;
    this.webhookUrl = webhookUrl;
    this.createdAt = OffsetDateTime.now();
  }

  public UUID getId() {
    return id;
  }

  public UUID getTopicId() {
    return topicId;
  }

  public String getName() {
    return name;
  }

  public String getWebhookUrl() {
    return webhookUrl;
  }

  public Long getLastDeliveredMessageId() {
    return lastDeliveredMessageId;
  }

  public boolean isActive() {
    return active;
  }

  public OffsetDateTime getCreatedAt() {
    return createdAt;
  }

  public void advanceCursor(Long messageId) {
    this.lastDeliveredMessageId = messageId;
  }

  public void deactivate() {
    this.active = false;
  }
}
