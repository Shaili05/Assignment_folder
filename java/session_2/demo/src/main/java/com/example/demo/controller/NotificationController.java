package com.example.demo.controller;

import com.example.demo.service.NotificationService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/notify")
public class NotificationController {

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @GetMapping
    public String notify(@RequestParam(defaultValue = "UserLogin") String event) {
        return notificationService.notify(event);
    }
}