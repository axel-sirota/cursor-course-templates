package com.example.broker.deadletter;

import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/dead-letter")
public class DeadLetterController {
  private final DeadLetterService service;

  public DeadLetterController(DeadLetterService service) {
    this.service = service;
  }

  @GetMapping
  public List<DeadLetter> list() {
    return service.list();
  }

  @PostMapping("/{id}/replay")
  @ResponseStatus(HttpStatus.ACCEPTED)
  public void replay(@PathVariable Long id) {
    service.replay(id);
  }
}
