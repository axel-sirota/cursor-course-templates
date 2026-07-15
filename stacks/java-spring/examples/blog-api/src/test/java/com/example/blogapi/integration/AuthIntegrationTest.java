package com.example.blogapi.integration;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.blogapi.web.dto.AuthResponse;
import com.example.blogapi.web.dto.LoginRequest;
import com.example.blogapi.web.dto.RegisterRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

/**
 * Full-stack test: real Postgres via Testcontainers, real Flyway migrations, real BCrypt
 * password hashing. Exercises the register → login round trip end to end.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AuthIntegrationTest extends AbstractIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void register_thenLogin_bothSucceed() {
        // Input: a new user registration payload
        RegisterRequest registerRequest = new RegisterRequest(
            "integration-test@example.com", "supersecretpassword", "Integration Tester");

        // Register
        ResponseEntity<AuthResponse> registerResponse =
            restTemplate.postForEntity("/api/auth/register", registerRequest, AuthResponse.class);

        // Output: 200 OK with a non-empty access token and matching profile fields
        assertThat(registerResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(registerResponse.getBody()).isNotNull();
        assertThat(registerResponse.getBody().accessToken()).isNotBlank();
        assertThat(registerResponse.getBody().email()).isEqualTo("integration-test@example.com");

        // Input: correct credentials for the just-registered user
        LoginRequest loginRequest = new LoginRequest("integration-test@example.com", "supersecretpassword");

        ResponseEntity<AuthResponse> loginResponse =
            restTemplate.postForEntity("/api/auth/login", loginRequest, AuthResponse.class);

        // Output: 200 OK with a fresh access token for the same user
        assertThat(loginResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(loginResponse.getBody()).isNotNull();
        assertThat(loginResponse.getBody().userId()).isEqualTo(registerResponse.getBody().userId());
    }

    @Test
    void register_duplicateEmail_returns400() {
        RegisterRequest first = new RegisterRequest("dup@example.com", "supersecretpassword", "First User");
        restTemplate.postForEntity("/api/auth/register", first, AuthResponse.class);

        RegisterRequest duplicate = new RegisterRequest("dup@example.com", "anotherpassword", "Second User");
        ResponseEntity<String> response = restTemplate.postForEntity("/api/auth/register", duplicate, String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
    }

    @Test
    void login_wrongPassword_returns401() {
        RegisterRequest registerRequest = new RegisterRequest(
            "wrongpass@example.com", "correctpassword", "Wrong Pass Tester");
        restTemplate.postForEntity("/api/auth/register", registerRequest, AuthResponse.class);

        LoginRequest badLogin = new LoginRequest("wrongpass@example.com", "incorrectpassword");
        ResponseEntity<String> response = restTemplate.postForEntity("/api/auth/login", badLogin, String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }
}
