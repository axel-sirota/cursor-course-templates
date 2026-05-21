package com.example.broker.subscriptions;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.time.OffsetDateTime;
import java.util.UUID;

public class SubscriptionDto {
  public record CreateRequest(
      @NotBlank String name,
      @NotBlank @Pattern(regexp = "^https?://.+", message = "webhookUrl must be http(s)://...")
          String webhookUrl) {}

  public record Response(
      UUID id,
      UUID topicId,
      String name,
      String webhookUrl,
      Long lastDeliveredMessageId,
      boolean active,
      OffsetDateTime createdAt) {}
}
