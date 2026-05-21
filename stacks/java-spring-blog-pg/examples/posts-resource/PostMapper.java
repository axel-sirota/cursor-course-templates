package com.example.blog.posts;

import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface PostMapper {
    PostDto toDto(Post post);
}
