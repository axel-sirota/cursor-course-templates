package com.example.blogapi.service;

import com.example.blogapi.model.Post;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreatePostRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {

    private final PostRepository postRepository;

    /**
     * Creates a new blog post.
     *
     * @param request the post creation payload
     * @param authorId the authenticated author's identifier
     * @return the persisted post with generated id and timestamps
     * @throws IllegalArgumentException if the title is too short
     */
    @Transactional
    public Post createPost(CreatePostRequest request, UUID authorId) {
        if (request.title().length() < 3) {
            throw new IllegalArgumentException("Title must be at least 3 characters");
        }

        Post post = new Post();
        post.setTitle(request.title());
        post.setContent(request.content());
        post.setAuthorId(authorId);

        Post saved = postRepository.save(post);
        log.info("Created post {} for author {}", saved.getId(), authorId);
        return saved;
    }

    /**
     * Fetches a single post by id.
     *
     * @param postId the post identifier
     * @return the matching post
     * @throws EntityNotFoundException if no post has that id
     */
    public Post getPost(UUID postId) {
        return postRepository.findById(postId)
            .orElseThrow(() -> new EntityNotFoundException("Post not found: " + postId));
    }

    /**
     * Lists posts newest-first, paginated.
     *
     * @param pageable page number/size
     * @return a page of posts
     */
    public Page<Post> listPosts(Pageable pageable) {
        return postRepository.findAllByOrderByCreatedAtDesc(pageable);
    }
}
