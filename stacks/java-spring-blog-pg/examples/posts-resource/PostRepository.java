package com.example.blog.posts;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

interface PostRepository {
    List<Post> findAll();

    Optional<Post> findById(UUID id);

    Post save(Post post);

    boolean deleteById(UUID id);
}
