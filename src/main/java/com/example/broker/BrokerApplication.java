package com.example.broker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class BrokerApplication {
  public static void main(String[] args) {
    SpringApplication.run(BrokerApplication.class, args);
  }
}
