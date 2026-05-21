package com.example.broker.topics;

import com.example.broker.shared.TopicAlreadyExistsException;
import java.util.List;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class TopicService {
  private final TopicRepository repository;

  public TopicService(TopicRepository repository) {
    this.repository = repository;
  }

  @Transactional
  public TopicDto.Response create(TopicDto.CreateRequest request) {
    if (repository.existsByName(request.name())) {
      throw new TopicAlreadyExistsException(request.name());
    }
    Topic saved = repository.save(new Topic(request.name()));
    return toResponse(saved);
  }

  public List<TopicDto.Response> list() {
    return repository.findAll(Sort.by("name")).stream().map(TopicService::toResponse).toList();
  }

  private static TopicDto.Response toResponse(Topic topic) {
    return new TopicDto.Response(topic.getId(), topic.getName(), topic.getCreatedAt());
  }
}
