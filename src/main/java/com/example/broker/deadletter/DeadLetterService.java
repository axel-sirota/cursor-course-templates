package com.example.broker.deadletter;

import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class DeadLetterService {
  private final DeadLetterRepository repository;

  public DeadLetterService(DeadLetterRepository repository) {
    this.repository = repository;
  }

  public List<DeadLetter> list() {
    throw new UnsupportedOperationException("Phase 4: list dead-letter entries");
  }

  @Transactional
  public void replay(Long id) {
    throw new UnsupportedOperationException("Phase 4: replay dead-letter entry");
  }
}
