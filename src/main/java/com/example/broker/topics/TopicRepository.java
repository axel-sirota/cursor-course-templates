package com.example.broker.topics;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TopicRepository extends JpaRepository<Topic, UUID> {
  Optional<Topic> findByName(String name);

  boolean existsByName(String name);
}
