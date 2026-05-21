package com.example.broker.deadletter;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "dead_letter")
public class DeadLetter {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "subscription_id", nullable = false)
  private UUID subscriptionId;

  @Column(name = "message_id", nullable = false)
  private Long messageId;

  @Column(name = "last_error", columnDefinition = "text")
  private String lastError;

  @Column(name = "moved_at", nullable = false)
  private OffsetDateTime movedAt;

  protected DeadLetter() {}

  public DeadLetter(UUID subscriptionId, Long messageId, String lastError) {
    this.subscriptionId = subscriptionId;
    this.messageId = messageId;
    this.lastError = lastError;
    this.movedAt = OffsetDateTime.now();
  }

  public Long getId() {
    return id;
  }

  public UUID getSubscriptionId() {
    return subscriptionId;
  }

  public Long getMessageId() {
    return messageId;
  }

  public String getLastError() {
    return lastError;
  }

  public OffsetDateTime getMovedAt() {
    return movedAt;
  }
}
