package com.example.broker.topics;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.broker.TestcontainersConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestcontainersConfig.class)
class TopicRepositoryTest {

  @Autowired TopicRepository repository;

  @Autowired TestEntityManager em;

  @Test
  void findByName_whenTopicPersisted_thenReturnsTopic() {
    Topic topic = new Topic("orders");
    em.persistAndFlush(topic);

    assertThat(repository.findByName("orders"))
        .isPresent()
        .get()
        .extracting(Topic::getName)
        .isEqualTo("orders");
  }

  @Test
  void existsByName_whenTopicSaved_thenReturnsTrue() {
    em.persistAndFlush(new Topic("orders"));

    assertThat(repository.existsByName("orders")).isTrue();
    assertThat(repository.existsByName("missing")).isFalse();
  }
}
