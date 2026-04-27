package com.example.session4.service;

import com.example.session4.client.NotificationServiceClient;
import com.example.session4.dto.TodoDTO;
import com.example.session4.exception.TodoNotFoundException;
import com.example.session4.model.Todo;
import com.example.session4.repository.TodoRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class TodoService {

    private static final Logger logger = LoggerFactory.getLogger(TodoService.class);

    private final TodoRepository todoRepository;
    private final NotificationServiceClient notificationServiceClient;

    public TodoService(TodoRepository todoRepository, NotificationServiceClient notificationServiceClient) {
        this.todoRepository = todoRepository;
        this.notificationServiceClient = notificationServiceClient;
    }

    private TodoDTO convertToDTO(Todo todo) {
        TodoDTO dto = new TodoDTO();
        dto.setTitle(todo.getTitle());
        dto.setDescription(todo.getDescription());
        dto.setStatus(todo.getStatus());
        return dto;
    }

    private Todo convertToEntity(TodoDTO dto) {
        Todo todo = new Todo();
        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());
        todo.setStatus(dto.getStatus() != null ? dto.getStatus() : Todo.Status.PENDING);
        todo.setCreatedAt(LocalDateTime.now());
        return todo;
    }

    public TodoDTO createTodo(TodoDTO dto) {
        logger.info("Creating new todo with title: {}", dto.getTitle());
        Todo todo = convertToEntity(dto);
        Todo saved = todoRepository.save(todo);
        notificationServiceClient.sendNotification("New TODO created: " + saved.getTitle());
        logger.info("Todo created successfully with id: {}", saved.getId());
        return convertToDTO(saved);
    }

    public List<TodoDTO> getAllTodos() {
        logger.info("Fetching all todos");
        return todoRepository.findAll()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public TodoDTO getTodoById(Long id) {
        logger.info("Fetching todo with id: {}", id);
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));
        return convertToDTO(todo);
    }

    public TodoDTO updateTodo(Long id, TodoDTO dto) {
        logger.info("Updating todo with id: {}", id);
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));
        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());
        todo.setStatus(dto.getStatus());
        Todo updated = todoRepository.save(todo);
        logger.info("Todo updated successfully with id: {}", id);
        return convertToDTO(updated);
    }

    public void deleteTodo(Long id) {
        logger.info("Deleting todo with id: {}", id);
        todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));
        todoRepository.deleteById(id);
        logger.info("Todo deleted successfully with id: {}", id);
    }
}