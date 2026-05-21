package com.example.broker.dispatch;

import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DeliveryAttemptRepository extends JpaRepository<DeliveryAttempt, Long> {
  List<DeliveryAttempt> findByStatusAndNextAttemptAtBefore(String status, OffsetDateTime cutoff);
}
