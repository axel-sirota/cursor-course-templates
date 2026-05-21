package com.example.broker.messages;

import com.example.broker.topics.Topic;
import com.example.broker.topics.TopicRepository;
import jakarta.persistence.EntityNotFoundException;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class MessageService {
  private final MessageRepository repository;
  private final TopicRepository topicRepository;

  public MessageService(MessageRepository repository, TopicRepository topicRepository) {
    this.repository = repository;
    this.topicRepository = topicRepository;
  }

  @Transactional
  public MessageDto.Response publish(String topicName, MessageDto.PublishRequest request) {
    Topic topic =
        topicRepository
            .findByName(topicName)
            .orElseThrow(() -> new EntityNotFoundException("Topic not found: " + topicName));
    Map<String, Object> headers = request.headers() == null ? Map.of() : request.headers();
    Message message = new Message(topic.getId(), request.payload(), headers);
    Message saved = repository.save(message);
    return new MessageDto.Response(saved.getId(), topic.getName(), saved.getPublishedAt());
  }
}
