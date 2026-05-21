package com.example.broker.dispatch;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "delivery_attempts")
public class DeliveryAttempt {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "subscription_id", nullable = false)
  private UUID subscriptionId;

  @Column(name = "message_id", nullable = false)
  private Long messageId;

  @Column(name = "attempt_no", nullable = false)
  private int attemptNo;

  @Column(nullable = false)
  private String status;

  @Column(name = "http_status")
  private Integer httpStatus;

  @Column(columnDefinition = "text")
  private String error;

  @Column(name = "attempted_at")
  private OffsetDateTime attemptedAt;

  @Column(name = "next_attempt_at", nullable = false)
  private OffsetDateTime nextAttemptAt;

  protected DeliveryAttempt() {}

  public DeliveryAttempt(
      UUID subscriptionId, Long messageId, int attemptNo, OffsetDateTime nextAttemptAt) {
    this.subscriptionId = subscriptionId;
    this.messageId = messageId;
    this.attemptNo = attemptNo;
    this.status = "PENDING";
    this.nextAttemptAt = nextAttemptAt;
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

  public int getAttemptNo() {
    return attemptNo;
  }

  public String getStatus() {
    return status;
  }

  public Integer getHttpStatus() {
    return httpStatus;
  }

  public String getError() {
    return error;
  }

  public OffsetDateTime getAttemptedAt() {
    return attemptedAt;
  }

  public OffsetDateTime getNextAttemptAt() {
    return nextAttemptAt;
  }

  public void markSuccess(int httpStatus) {
    this.status = "SUCCESS";
    this.httpStatus = httpStatus;
    this.attemptedAt = OffsetDateTime.now();
  }

  public void markFailed(Integer httpStatus, String error, OffsetDateTime nextAttemptAt) {
    this.status = "FAILED";
    this.httpStatus = httpStatus;
    this.error = error;
    this.attemptedAt = OffsetDateTime.now();
    this.nextAttemptAt = nextAttemptAt;
  }
}
