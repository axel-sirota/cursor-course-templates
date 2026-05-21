package com.example.blog.posts;

import com.example.blog.shared.NotFoundException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class PostService {

    private final PostRepository repo;
    private final PostMapper mapper;

    @Transactional(readOnly = true)
    public List<PostDto> list() {
        return repo.findAll().stream().map(mapper::toDto).toList();
    }

    @Transactional
    public PostDto create(PostDto in) {
        Post post = new Post(UUID.randomUUID(), in.title(), in.body(), in.author(), Instant.now());
        return mapper.toDto(repo.save(post));
    }

    @Transactional(readOnly = true)
    public PostDto get(UUID id) {
        return repo.findById(id)
                .map(mapper::toDto)
                .orElseThrow(() -> new NotFoundException("post " + id));
    }

    @Transactional
    public PostDto update(UUID id, PostDto in) {
        Post existing = repo.findById(id)
                .orElseThrow(() -> new NotFoundException("post " + id));
        existing.setTitle(in.title());
        existing.setBody(in.body());
        existing.setAuthor(in.author());
        return mapper.toDto(repo.save(existing));
    }

    @Transactional
    public void delete(UUID id) {
        if (!repo.deleteById(id)) {
            throw new NotFoundException("post " + id);
        }
    }
}
