package com.example.broker.dispatch;

import com.example.broker.subscriptions.Subscription;
import com.example.broker.subscriptions.SubscriptionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class DispatcherScheduler {
  private static final Logger log = LoggerFactory.getLogger(DispatcherScheduler.class);

  private final SubscriptionRepository subscriptionRepository;
  private final DeliveryService deliveryService;

  public DispatcherScheduler(
      SubscriptionRepository subscriptionRepository, DeliveryService deliveryService) {
    this.subscriptionRepository = subscriptionRepository;
    this.deliveryService = deliveryService;
  }

  @Scheduled(fixedDelayString = "${broker.dispatcher.poll-interval-ms:500}")
  public void pollAndDispatch() {
    // Phase 3: iterate active subscriptions and call deliveryService.deliverPending(sub).
    // Phase 4: also call deliveryService.retryFailed() on a slower schedule.
    for (Subscription sub : subscriptionRepository.findByActiveTrue()) {
      log.trace("Skeleton: would dispatch for subscription {}", sub.getId());
    }
  }
}
