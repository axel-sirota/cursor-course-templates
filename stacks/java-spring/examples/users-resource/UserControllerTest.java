package com.example.app.users;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(UserController.class)
class UserControllerTest {

  @Autowired private MockMvc mockMvc;

  @MockBean private UserService userService;

  @Test
  void createUser_whenValidRequest_thenReturns201() throws Exception {
    UserDto created = new UserDto(1L, "Alice", "alice@example.com");
    given(userService.create(any())).willReturn(created);

    mockMvc
        .perform(
            post("/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"name":"Alice","email":"alice@example.com"}
                    """))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").value(1))
        .andExpect(jsonPath("$.name").value("Alice"))
        .andExpect(jsonPath("$.email").value("alice@example.com"));
  }

  @Test
  void findAll_whenUsersExist_thenReturns200WithList() throws Exception {
    List<UserDto> users =
        List.of(
            new UserDto(1L, "Alice", "alice@example.com"),
            new UserDto(2L, "Bob", "bob@example.com"));
    given(userService.findAll()).willReturn(users);

    mockMvc
        .perform(get("/users"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(2))
        .andExpect(jsonPath("$[0].name").value("Alice"))
        .andExpect(jsonPath("$[1].name").value("Bob"));
  }

  @Test
  void findById_whenUserExists_thenReturns200WithUser() throws Exception {
    UserDto user = new UserDto(1L, "Alice", "alice@example.com");
    given(userService.findById(1L)).willReturn(user);

    mockMvc
        .perform(get("/users/{id}", 1L))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.id").value(1))
        .andExpect(jsonPath("$.name").value("Alice"))
        .andExpect(jsonPath("$.email").value("alice@example.com"));
  }
}
