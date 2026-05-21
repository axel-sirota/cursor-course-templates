package com.example.broker;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

@SpringBootTest
@Import(TestcontainersConfig.class)
class BrokerApplicationTests {

  @Test
  void contextLoads() {
    // Smoke: Spring context wires up, Flyway runs V1__init.sql against Postgres testcontainer.
  }
}
