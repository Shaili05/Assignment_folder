package com.example.demo.service;

import com.example.demo.formatter.LongMessageFormatter;
import com.example.demo.formatter.ShortMessageFormatter;
import org.springframework.stereotype.Service;

@Service
public class MessageService {

    private final ShortMessageFormatter shortFormatter;
    private final LongMessageFormatter longFormatter;

    public MessageService(ShortMessageFormatter shortFormatter, 
                          LongMessageFormatter longFormatter) {
        this.shortFormatter = shortFormatter;
        this.longFormatter = longFormatter;
    }

    public String getMessage(String type) {
        return type.equalsIgnoreCase("SHORT") 
               ? shortFormatter.format() 
               : longFormatter.format();
    }
}