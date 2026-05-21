package com.example.broker.messages;

import jakarta.validation.constraints.NotNull;
import java.time.OffsetDateTime;
import java.util.Map;

public class MessageDto {
  public record PublishRequest(@NotNull Map<String, Object> payload, Map<String, Object> headers) {}

  public record Response(Long id, String topic, OffsetDateTime publishedAt) {}
}
