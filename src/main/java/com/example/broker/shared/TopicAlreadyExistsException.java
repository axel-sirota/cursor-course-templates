package com.example.broker.shared;

public class TopicAlreadyExistsException extends RuntimeException {
  private final String name;

  public TopicAlreadyExistsException(String name) {
    super("Topic already exists: " + name);
    this.name = name;
  }

  public String getName() {
    return name;
  }
}
