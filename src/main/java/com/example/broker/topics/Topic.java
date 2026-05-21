package com.example.broker.topics;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "topics")
public class Topic {
  @Id @GeneratedValue private UUID id;

  @Column(nullable = false, unique = true)
  private String name;

  @Column(name = "created_at", nullable = false)
  private OffsetDateTime createdAt;

  protected Topic() {}

  public Topic(String name) {
    this.name = name;
    this.createdAt = OffsetDateTime.now();
  }

  public UUID getId() {
    return id;
  }

  public String getName() {
    return name;
  }

  public OffsetDateTime getCreatedAt() {
    return createdAt;
  }
}
