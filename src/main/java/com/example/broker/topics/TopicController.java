package com.example.broker.topics;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/topics")
public class TopicController {
  private final TopicService service;

  public TopicController(TopicService service) {
    this.service = service;
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public TopicDto.Response create(@Valid @RequestBody TopicDto.CreateRequest request) {
    return service.create(request);
  }

  @GetMapping
  public List<TopicDto.Response> list() {
    return service.list();
  }
}
