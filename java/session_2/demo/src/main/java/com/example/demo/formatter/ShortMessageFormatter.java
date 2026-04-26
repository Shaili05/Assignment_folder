package com.example.demo.formatter;

import org.springframework.stereotype.Component;

@Component
public class ShortMessageFormatter {

    public String format() {
        return "Hello! Here comes the Short msg.";
    }
}