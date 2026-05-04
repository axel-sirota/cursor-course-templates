package com.example.app.users;

import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

  private final UserRepository userRepository;

  public UserDto create(UserDto dto) {
    User user = new User(dto.name(), dto.email());
    User saved = userRepository.save(user);
    return toDto(saved);
  }

  @Transactional(readOnly = true)
  public List<UserDto> findAll() {
    return userRepository.findAll().stream().map(this::toDto).toList();
  }

  @Transactional(readOnly = true)
  public UserDto findById(Long id) {
    User user =
        userRepository
            .findById(id)
            .orElseThrow(() -> new EntityNotFoundException("User not found: " + id));
    return toDto(user);
  }

  private UserDto toDto(User user) {
    return new UserDto(user.getId(), user.getName(), user.getEmail());
  }
}
