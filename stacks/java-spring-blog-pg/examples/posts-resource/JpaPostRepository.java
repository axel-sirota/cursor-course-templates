package com.example.blog.posts;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

interface JpaPostRepository extends JpaRepository<Post, UUID>, PostRepository {

    @Override
    default boolean deleteById(UUID id) {
        if (!existsById(id)) {
            return false;
        }
        deleteById((Object) id);
        return true;
    }
}
