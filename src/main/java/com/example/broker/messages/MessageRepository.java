package com.example.broker.messages;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MessageRepository extends JpaRepository<Message, Long> {
  List<Message> findTop100ByTopicIdAndIdGreaterThanOrderByIdAsc(UUID topicId, Long afterId);

  Optional<Message> findTopByTopicIdOrderByIdDesc(UUID topicId);
}
