package com.example.broker.shared;

public class SubscriptionAlreadyExistsException extends RuntimeException {
  private final String name;

  public SubscriptionAlreadyExistsException(String topicName, String name) {
    super("Subscription already exists: " + topicName + "/" + name);
    this.name = name;
  }

  public String getName() {
    return name;
  }
}
