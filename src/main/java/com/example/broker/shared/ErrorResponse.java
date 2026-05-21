package com.example.broker.shared;

import java.time.OffsetDateTime;
import java.util.List;

public record ErrorResponse(
    OffsetDateTime timestamp, int status, String error, String message, List<String> details) {
  public static ErrorResponse of(int status, String error, String message) {
    return new ErrorResponse(OffsetDateTime.now(), status, error, message, List.of());
  }

  public static ErrorResponse of(int status, String error, String message, List<String> details) {
    return new ErrorResponse(OffsetDateTime.now(), status, error, message, details);
  }
}
