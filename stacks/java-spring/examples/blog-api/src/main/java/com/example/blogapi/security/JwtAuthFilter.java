package com.example.blogapi.security;

import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Reads a {@code Bearer} JWT from the {@code Authorization} header and, if valid, populates the
 * {@link SecurityContextHolder} with the authenticated user's id as the principal name.
 *
 * <p>Teaching-scale simplification: this does not load a full {@code UserDetails} from the
 * database on every request — the principal name is the raw user UUID string, read back out via
 * {@code @AuthenticationPrincipal} in controllers. See {@code examples/SETUP_COMPLETE.md}.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            try {
                UUID userId = jwtService.extractUserId(header.substring(7));
                var auth = new UsernamePasswordAuthenticationToken(userId.toString(), null, List.of());
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (JwtException | IllegalArgumentException e) {
                log.debug("Rejected invalid JWT: {}", e.getMessage());
                // Leave SecurityContext empty; request falls through as unauthenticated.
            }
        }
        chain.doFilter(request, response);
    }
}
