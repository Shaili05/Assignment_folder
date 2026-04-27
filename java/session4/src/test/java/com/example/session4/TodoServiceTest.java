package com.example.session4;

import com.example.session4.client.NotificationServiceClient;
import com.example.session4.dto.TodoDTO;
import com.example.session4.exception.TodoNotFoundException;
import com.example.session4.model.Todo;
import com.example.session4.repository.TodoRepository;
import com.example.session4.service.TodoService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class TodoServiceTest {

    private TodoRepository todoRepository;
    private NotificationServiceClient notificationServiceClient;
    private TodoService todoService;

    @BeforeEach
    void setup() {
        todoRepository = Mockito.mock(TodoRepository.class);
        notificationServiceClient = Mockito.mock(NotificationServiceClient.class);
        todoService = new TodoService(todoRepository, notificationServiceClient);
    }

    private Todo makeTodo(Long id, String title, String description, Todo.Status status) {
        Todo todo = new Todo();
        todo.setId(id);
        todo.setTitle(title);
        todo.setDescription(description);
        todo.setStatus(status);
        todo.setCreatedAt(LocalDateTime.now());
        return todo;
    }

    @Test
    void createTodo_shouldReturnSavedTodo() {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Buy milk");
        dto.setDescription("From the store");
        dto.setStatus(Todo.Status.PENDING);

        Todo saved = makeTodo(1L, "Buy milk", "From the store", Todo.Status.PENDING);
        when(todoRepository.save(any(Todo.class))).thenReturn(saved);

        TodoDTO result = todoService.createTodo(dto);

        assertEquals("Buy milk", result.getTitle());
        assertEquals(Todo.Status.PENDING, result.getStatus());
        verify(notificationServiceClient).sendNotification(any(String.class));
    }

    @Test
    void createTodo_shouldDefaultToPending_whenStatusNotGiven() {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Read book");
        dto.setDescription("Java basics");

        Todo saved = makeTodo(2L, "Read book", "Java basics", Todo.Status.PENDING);
        when(todoRepository.save(any(Todo.class))).thenReturn(saved);

        TodoDTO result = todoService.createTodo(dto);

        assertEquals(Todo.Status.PENDING, result.getStatus());
    }

    @Test
    void getAllTodos_shouldReturnList() {
        Todo t1 = makeTodo(1L, "Task one", "desc one", Todo.Status.PENDING);
        Todo t2 = makeTodo(2L, "Task two", "desc two", Todo.Status.COMPLETED);
        when(todoRepository.findAll()).thenReturn(List.of(t1, t2));

        List<TodoDTO> result = todoService.getAllTodos();

        assertEquals(2, result.size());
        assertEquals("Task one", result.get(0).getTitle());
    }

    @Test
    void getTodoById_shouldReturnTodo_whenExists() {
        Todo todo = makeTodo(1L, "Buy milk", "From store", Todo.Status.PENDING);
        when(todoRepository.findById(1L)).thenReturn(Optional.of(todo));

        TodoDTO result = todoService.getTodoById(1L);

        assertEquals("Buy milk", result.getTitle());
    }

    @Test
    void getTodoById_shouldThrowException_whenNotFound() {
        when(todoRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(TodoNotFoundException.class, () -> todoService.getTodoById(99L));
    }

    @Test
    void updateTodo_shouldUpdateFields() {
        Todo existing = makeTodo(1L, "Old title", "Old desc", Todo.Status.PENDING);
        when(todoRepository.findById(1L)).thenReturn(Optional.of(existing));

        Todo updated = makeTodo(1L, "New title", "New desc", Todo.Status.COMPLETED);
        when(todoRepository.save(any(Todo.class))).thenReturn(updated);

        TodoDTO dto = new TodoDTO();
        dto.setTitle("New title");
        dto.setDescription("New desc");
        dto.setStatus(Todo.Status.COMPLETED);

        TodoDTO result = todoService.updateTodo(1L, dto);

        assertEquals("New title", result.getTitle());
        assertEquals(Todo.Status.COMPLETED, result.getStatus());
    }

    @Test
    void updateTodo_shouldThrowException_whenNotFound() {
        when(todoRepository.findById(50L)).thenReturn(Optional.empty());

        TodoDTO dto = new TodoDTO();
        dto.setTitle("Something");

        assertThrows(TodoNotFoundException.class, () -> todoService.updateTodo(50L, dto));
    }

    @Test
    void deleteTodo_shouldDelete_whenExists() {
        Todo todo = makeTodo(1L, "Buy milk", "desc", Todo.Status.PENDING);
        when(todoRepository.findById(1L)).thenReturn(Optional.of(todo));

        todoService.deleteTodo(1L);

        verify(todoRepository).deleteById(1L);
    }

    @Test
    void deleteTodo_shouldThrowException_whenNotFound() {
        when(todoRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(TodoNotFoundException.class, () -> todoService.deleteTodo(99L));
    }
}