package com.example.demo.notification;

import org.springframework.stereotype.Component;

@Component
public class NotificationComponent {

    public String generateMessage(String event) {
        return "Notification sent for event: " + event;
    }
}