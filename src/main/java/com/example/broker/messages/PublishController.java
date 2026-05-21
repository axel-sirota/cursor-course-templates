package com.example.broker.messages;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/topics/{topicName}/messages")
public class PublishController {
  private final MessageService service;

  public PublishController(MessageService service) {
    this.service = service;
  }

  @PostMapping
  @ResponseStatus(HttpStatus.ACCEPTED)
  public MessageDto.Response publish(
      @PathVariable String topicName, @Valid @RequestBody MessageDto.PublishRequest request) {
    return service.publish(topicName, request);
  }
}
