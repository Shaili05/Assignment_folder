package com.example.session4.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class NotificationServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(NotificationServiceClient.class);

    public void sendNotification(String message) {
        logger.info("Notification sent: {}", message);
        System.out.println("Notification sent: " + message);
    }
}