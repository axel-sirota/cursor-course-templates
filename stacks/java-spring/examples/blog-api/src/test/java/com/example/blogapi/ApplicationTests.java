package com.example.blogapi;

import com.example.blogapi.integration.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/** Smoke test: the full Spring application context loads without errors against a real Postgres. */
@SpringBootTest
class ApplicationTests extends AbstractIntegrationTest {

    @Test
    void contextLoads() {
        // If the context fails to load, this test fails with the underlying cause.
    }
}
