package com.example.demo.formatter;

import org.springframework.stereotype.Component;

@Component
public class LongMessageFormatter {

    public String format() {
        return "Hello! Long message with complete information for the user.";
    }
}