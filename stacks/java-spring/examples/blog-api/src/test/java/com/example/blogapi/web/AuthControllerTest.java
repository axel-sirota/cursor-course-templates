package com.example.blogapi.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.blogapi.config.SecurityConfig;
import com.example.blogapi.model.User;
import com.example.blogapi.security.JwtAuthFilter;
import com.example.blogapi.security.JwtService;
import com.example.blogapi.service.UserService;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(AuthController.class)
@Import(SecurityConfig.class)
class AuthControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private UserService userService;
    @MockBean private JwtService jwtService;
    @MockBean private AuthenticationManager authenticationManager;
    @MockBean private JwtAuthFilter jwtAuthFilter;
    @MockBean private UserDetailsService userDetailsService;

    @Test
    void register_successCase_returnsAccessToken() throws Exception {
        User saved = new User();
        saved.setId(UUID.randomUUID());
        saved.setEmail("new@example.com");
        saved.setFullName("New User");
        saved.setCreatedAt(Instant.now());
        given(userService.register(any())).willReturn(saved);
        given(jwtService.generateToken(saved.getId())).willReturn("fake-jwt-token");

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"new@example.com","password":"supersecret","fullName":"New User"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.accessToken").value("fake-jwt-token"))
            .andExpect(jsonPath("$.email").value("new@example.com"));
    }

    @Test
    void register_validationCase_shortPasswordReturns400() throws Exception {
        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"new@example.com","password":"short","fullName":"New User"}
                    """))
            .andExpect(status().isBadRequest());
    }

    @Test
    void register_errorCase_duplicateEmailReturns400() throws Exception {
        given(userService.register(any()))
            .willThrow(new IllegalArgumentException("Email already registered: dup@example.com"));

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"dup@example.com","password":"supersecret","fullName":"Dup User"}
                    """))
            .andExpect(status().isBadRequest());
    }

    @Test
    void login_errorCase_invalidCredentialsReturns401() throws Exception {
        given(authenticationManager.authenticate(any())).willThrow(new BadCredentialsException("bad creds"));

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"nope@example.com","password":"wrongpassword"}
                    """))
            .andExpect(status().isUnauthorized());
    }
}
