package com.example.broker.topics;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.time.OffsetDateTime;
import java.util.UUID;

public class TopicDto {
  public record CreateRequest(
      @NotBlank
          @Pattern(
              regexp = "^[a-z0-9][a-z0-9._-]{0,127}$",
              message = "lowercase, digits, dot, underscore, hyphen; 1-128 chars")
          String name) {}

  public record Response(UUID id, String name, OffsetDateTime createdAt) {}
}
