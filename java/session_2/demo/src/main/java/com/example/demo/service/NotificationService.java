package com.example.demo.service;

import com.example.demo.notification.NotificationComponent;
import org.springframework.stereotype.Service;

@Service
public class NotificationService {

    private final NotificationComponent notificationComponent;

    public NotificationService(NotificationComponent notificationComponent) {
        this.notificationComponent = notificationComponent;
    }

    public String notify(String event) {
        return notificationComponent.generateMessage(event);
    }
}