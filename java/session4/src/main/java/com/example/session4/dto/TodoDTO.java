package com.example.session4.dto;

import com.example.session4.model.Todo.Status;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class TodoDTO {

    @NotNull(message = "Title cannot be null")
    @Size(min = 3, message = "Title must have at least 3 characters")
    private String title;

    private String description;

    private Status status;

    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public Status getStatus() { return status; }

    public void setTitle(String title) { this.title = title; }
    public void setDescription(String description) { this.description = description; }
    public void setStatus(Status status) { this.status = status; }
}