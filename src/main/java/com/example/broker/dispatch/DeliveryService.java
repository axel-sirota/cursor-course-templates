package com.example.broker.dispatch;

import com.example.broker.subscriptions.Subscription;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class DeliveryService {

  public void deliverPending(Subscription subscription) {
    throw new UnsupportedOperationException("Phase 3: implement webhook POST + cursor advance");
  }

  public void retryFailed() {
    throw new UnsupportedOperationException(
        "Phase 4: implement retry-with-backoff and DLQ promotion");
  }
}
