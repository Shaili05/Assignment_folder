package com.example.session4.service;

import com.example.session4.dto.TodoDTO;
import com.example.session4.exception.TodoNotFoundException;
import com.example.session4.model.Todo;
import com.example.session4.repository.TodoRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class TodoService {

    private final TodoRepository todoRepository;

    public TodoService(TodoRepository todoRepository) {
        this.todoRepository = todoRepository;
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
        Todo todo = convertToEntity(dto);
        Todo saved = todoRepository.save(todo);
        return convertToDTO(saved);
    }

    public List<TodoDTO> getAllTodos() {
        return todoRepository.findAll()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    public TodoDTO getTodoById(Long id) {
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));
        return convertToDTO(todo);
    }

    public TodoDTO updateTodo(Long id, TodoDTO dto) {
        Todo todo = todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));

        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());
        todo.setStatus(dto.getStatus());

        Todo updated = todoRepository.save(todo);
        return convertToDTO(updated);
    }

    public void deleteTodo(Long id) {
        todoRepository.findById(id)
                .orElseThrow(() -> new TodoNotFoundException(id));
        todoRepository.deleteById(id);
    }
}