package com.example.broker.messages;

import io.hypersistence.utils.hibernate.type.json.JsonBinaryType;
import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.UUID;
import org.hibernate.annotations.Type;

@Entity
@Table(name = "messages")
public class Message {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(name = "topic_id", nullable = false)
  private UUID topicId;

  @Type(JsonBinaryType.class)
  @Column(columnDefinition = "jsonb", nullable = false)
  private Map<String, Object> payload;

  @Type(JsonBinaryType.class)
  @Column(columnDefinition = "jsonb", nullable = false)
  private Map<String, Object> headers;

  @Column(name = "published_at", nullable = false)
  private OffsetDateTime publishedAt;

  protected Message() {}

  public Message(UUID topicId, Map<String, Object> payload, Map<String, Object> headers) {
    this.topicId = topicId;
    this.payload = payload;
    this.headers = headers;
    this.publishedAt = OffsetDateTime.now();
  }

  public Long getId() {
    return id;
  }

  public UUID getTopicId() {
    return topicId;
  }

  public Map<String, Object> getPayload() {
    return payload;
  }

  public Map<String, Object> getHeaders() {
    return headers;
  }

  public OffsetDateTime getPublishedAt() {
    return publishedAt;
  }
}
