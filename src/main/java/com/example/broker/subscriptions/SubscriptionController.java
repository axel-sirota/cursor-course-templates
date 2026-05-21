package com.example.broker.subscriptions;

import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
public class SubscriptionController {
  private final SubscriptionService service;

  public SubscriptionController(SubscriptionService service) {
    this.service = service;
  }

  @PostMapping("/topics/{topicName}/subscriptions")
  @ResponseStatus(HttpStatus.CREATED)
  public SubscriptionDto.Response create(
      @PathVariable String topicName, @Valid @RequestBody SubscriptionDto.CreateRequest request) {
    return service.create(topicName, request);
  }

  @GetMapping("/subscriptions/{id}")
  public SubscriptionDto.Response get(@PathVariable UUID id) {
    return service.get(id);
  }

  @DeleteMapping("/subscriptions/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void deactivate(@PathVariable UUID id) {
    service.deactivate(id);
  }
}
