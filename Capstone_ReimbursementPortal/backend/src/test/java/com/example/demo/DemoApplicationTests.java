package com.example.demo;

import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import com.example.demo.entity.User;
import com.example.demo.enums.Role;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.exception.UserValidator;
import com.example.demo.repository.UserRepository;
import com.example.demo.service.UserServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.lenient;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Unit tests for UserServiceImpl.
 * Using Mockito to mock dependencies so we only test service logic.
 */
@ExtendWith(MockitoExtension.class)
class DemoApplicationTests {

	/** Mocked repository - does not hit real database. */
	@Mock
	private UserRepository userRepository;

	/** Mocked validator - we control what it does in each test. */
	@Mock
	private UserValidator userValidator;

	/** Mocked password encoder - returns predictable value. */
	@Mock
	private PasswordEncoder passwordEncoder;

	/** The actual class we are testing. */
	@InjectMocks
	private UserServiceImpl userService;

	/** Sample user used across multiple tests. */
	private User sampleUser;

	/** Sample request DTO used across multiple tests. */
	private UserRequestDto sampleRequest;

	/**
	 * Runs before each test to set up common test data.
	 */
	@BeforeEach
	void setUp() {
		sampleUser = new User();
		sampleUser.setId(1L);
		sampleUser.setName("Test User");
		sampleUser.setEmail("test@company.com");
		sampleUser.setPassword("encoded_password");
		sampleUser.setRole(Role.EMPLOYEE);

		sampleRequest = new UserRequestDto();
		sampleRequest.setName("Test User");
		sampleRequest.setEmail("test@company.com");
		sampleRequest.setPassword("Test@1234");
		sampleRequest.setRole("EMPLOYEE");
	}

	/**
	 * Test createUser returns correct response with valid data.
	 */
	@Test
	void createUser_validData_returnsResponse() {
		doNothing().when(userValidator).validateCreateUser(any());
		when(passwordEncoder.encode(anyString()))
				.thenReturn("encoded_password");
		when(userRepository.save(any(User.class))).thenReturn(sampleUser);

		UserResponseDto result = userService.createUser(sampleRequest);

		assertNotNull(result);
		assertEquals("Test User", result.getName());
		assertEquals("test@company.com", result.getEmail());
		assertEquals("EMPLOYEE", result.getRole());
	}

	/**
	 * Test deleteUser calls repository delete when user exists.
	 */
	@Test
	void deleteUser_existingId_deletesSuccessfully() {
		doNothing().when(userValidator).validateUserExists(anyLong());
		doNothing().when(userRepository).deleteById(anyLong());

		userService.deleteUser(1L);

		verify(userRepository, times(1)).deleteById(1L);
	}

	/**
	 * Test getAllUsers returns paginated results correctly.
	 */
	@Test
	void getAllUsers_returnsPagedResults() {
		Page<User> page = new PageImpl<>(List.of(sampleUser));
		when(userRepository.findAll(any(PageRequest.class)))
				.thenReturn(page);

		Page<UserResponseDto> result =
				userService.getAllUsers(PageRequest.of(0, 10));

		assertNotNull(result);
		assertEquals(1, result.getTotalElements());
		assertEquals("Test User",
				result.getContent().get(0).getName());
	}

	/**
	 * Test assignManager throws error when user has wrong role.
	 */
	@Test
	void assignManager_wrongRole_throwsException() {
		User employee = new User();
		employee.setId(2L);
		employee.setRole(Role.EMPLOYEE);

		User notAManager = new User();
		notAManager.setId(3L);
		notAManager.setRole(Role.EMPLOYEE);

		lenient().doNothing()
				.when(userValidator).validateUserExists(anyLong());
		when(userRepository.findById(2L))
				.thenReturn(Optional.of(employee));
		when(userRepository.findById(3L))
				.thenReturn(Optional.of(notAManager));

		assertThrows(IllegalArgumentException.class, () ->
				userService.assignManager(2L, 3L));
	}

	/**
	 * Test assignManager works correctly with valid manager role.
	 */
	@Test
	void assignManager_validManager_assignsSuccessfully() {
		User employee = new User();
		employee.setId(2L);
		employee.setName("Employee");
		employee.setEmail("emp@company.com");
		employee.setRole(Role.EMPLOYEE);

		User manager = new User();
		manager.setId(3L);
		manager.setName("Manager");
		manager.setRole(Role.MANAGER);

		lenient().doNothing()
				.when(userValidator).validateUserExists(anyLong());
		when(userRepository.findById(2L))
				.thenReturn(Optional.of(employee));
		when(userRepository.findById(3L))
				.thenReturn(Optional.of(manager));

		employee.setManager(manager);
		when(userRepository.save(any(User.class)))
				.thenReturn(employee);

		UserResponseDto result = userService.assignManager(2L, 3L);

		assertNotNull(result);
		assertEquals("Employee", result.getName());
	}

	/**
	 * Test deleteUser throws exception when user does not exist.
	 */
	@Test
	void deleteUser_nonExistingId_throwsException() {
		doThrow(new ResourceNotFoundException("User not found"))
				.when(userValidator).validateUserExists(99L);

		assertThrows(ResourceNotFoundException.class, () ->
				userService.deleteUser(99L));
	}
}