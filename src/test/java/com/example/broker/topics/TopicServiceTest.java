package com.example.broker.topics;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.example.broker.TestcontainersConfig;
import com.example.broker.shared.TopicAlreadyExistsException;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import({TestcontainersConfig.class, TopicService.class})
class TopicServiceTest {

  @Autowired TopicService service;

  @Test
  void create_whenValidRequest_thenReturnsResponseWithId() {
    TopicDto.Response response = service.create(new TopicDto.CreateRequest("orders"));

    assertThat(response.id()).isNotNull();
    assertThat(response.name()).isEqualTo("orders");
    assertThat(response.createdAt()).isNotNull();
  }

  @Test
  void create_whenDuplicateName_thenThrowsTopicAlreadyExistsException() {
    service.create(new TopicDto.CreateRequest("orders"));

    assertThatThrownBy(() -> service.create(new TopicDto.CreateRequest("orders")))
        .isInstanceOf(TopicAlreadyExistsException.class);
  }

  @Test
  void list_whenMultipleTopics_thenReturnsSortedByName() {
    service.create(new TopicDto.CreateRequest("zeta"));
    service.create(new TopicDto.CreateRequest("alpha"));
    service.create(new TopicDto.CreateRequest("mike"));

    List<String> names = service.list().stream().map(TopicDto.Response::name).toList();

    assertThat(names).containsExactly("alpha", "mike", "zeta");
  }
}
