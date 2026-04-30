package com.example.demo;

import com.example.demo.dto.ClaimActionRequestDto;
import com.example.demo.dto.ClaimRequestDto;
import com.example.demo.dto.ClaimResponseDto;
import com.example.demo.dto.UserRequestDto;
import com.example.demo.dto.UserResponseDto;
import com.example.demo.entity.Claim;
import com.example.demo.entity.User;
import com.example.demo.enums.ClaimStatus;
import com.example.demo.enums.Role;
import com.example.demo.exception.ClaimValidator;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.exception.UserValidator;
import com.example.demo.repository.ClaimRepository;
import com.example.demo.repository.UserRepository;
import com.example.demo.service.ClaimServiceImpl;
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

import java.math.BigDecimal;
import java.time.LocalDate;
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
 * Unit tests for UserServiceImpl and ClaimServiceImpl.
 * Using Mockito to mock dependencies so we only test service logic.
 */
@ExtendWith(MockitoExtension.class)
class DemoApplicationTests {

	/** Mocked user repository. */
	@Mock
	private UserRepository userRepository;

	/** Mocked claim repository. */
	@Mock
	private ClaimRepository claimRepository;

	/** Mocked user validator. */
	@Mock
	private UserValidator userValidator;

	/** Mocked claim validator. */
	@Mock
	private ClaimValidator claimValidator;

	/** Mocked password encoder. */
	@Mock
	private PasswordEncoder passwordEncoder;

	/** UserServiceImpl under test. */
	@InjectMocks
	private UserServiceImpl userService;

	/** ClaimServiceImpl under test. */
	@InjectMocks
	private ClaimServiceImpl claimService;

	/** Sample user for tests. */
	private User sampleUser;

	/** Sample admin user for tests. */
	private User adminUser;

	/** Sample claim for tests. */
	private Claim sampleClaim;

	/** Sample user request DTO. */
	private UserRequestDto sampleRequest;

	/**
	 * Sets up test data before each test.
	 */
	@BeforeEach
	void setUp() {
		sampleUser = new User();
		sampleUser.setId(1L);
		sampleUser.setName("Test User");
		sampleUser.setEmail("test@company.com");
		sampleUser.setPassword("encoded_password");
		sampleUser.setRole(Role.EMPLOYEE);

		adminUser = new User();
		adminUser.setId(2L);
		adminUser.setName("Admin User");
		adminUser.setEmail("admin@company.com");
		adminUser.setRole(Role.ADMIN);

		sampleClaim = new Claim();
		sampleClaim.setId(1L);
		sampleClaim.setAmount(new BigDecimal("5000"));
		sampleClaim.setDate(LocalDate.now());
		sampleClaim.setDescription("Travel expenses");
		sampleClaim.setStatus(ClaimStatus.SUBMITTED);
		sampleClaim.setEmployee(sampleUser);
		sampleClaim.setReviewer(adminUser);

		sampleRequest = new UserRequestDto();
		sampleRequest.setName("Test User");
		sampleRequest.setEmail("test@company.com");
		sampleRequest.setPassword("Test@1234");
		sampleRequest.setRole("EMPLOYEE");
	}

	/**
	 * Test createUser returns correct response.
	 */
	@Test
	void createUser_validData_returnsResponse() {
		doNothing().when(userValidator).validateCreateUser(any());
		when(passwordEncoder.encode(anyString()))
				.thenReturn("encoded_password");
		when(userRepository.save(any(User.class)))
				.thenReturn(sampleUser);

		UserResponseDto result = userService.createUser(sampleRequest);

		assertNotNull(result);
		assertEquals("Test User", result.getName());
		assertEquals("test@company.com", result.getEmail());
		assertEquals("EMPLOYEE", result.getRole());
	}

	/**
	 * Test deleteUser calls repository delete.
	 */
	@Test
	void deleteUser_existingId_deletesSuccessfully() {
		doNothing().when(userValidator).validateUserExists(anyLong());
		doNothing().when(userRepository).deleteById(anyLong());

		userService.deleteUser(1L);

		verify(userRepository, times(1)).deleteById(1L);
	}

	/**
	 * Test getAllUsers returns paginated results.
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
	 * Test assignManager throws error for wrong role.
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
	 * Test assignManager works with valid manager.
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
	 * Test deleteUser throws exception for non existing user.
	 */
	@Test
	void deleteUser_nonExistingId_throwsException() {
		doThrow(new ResourceNotFoundException("User not found"))
				.when(userValidator).validateUserExists(99L);

		assertThrows(ResourceNotFoundException.class, () ->
				userService.deleteUser(99L));
	}

	/**
	 * Test submitClaim saves claim and returns response.
	 */
	@Test
	void submitClaim_validData_returnsResponse() {
		ClaimRequestDto dto = new ClaimRequestDto();
		dto.setEmployeeId(1L);
		dto.setAmount(new BigDecimal("5000"));
		dto.setDate(LocalDate.now());
		dto.setDescription("Travel expenses");

		doNothing().when(claimValidator).validateCreateClaim(any());
		when(userRepository.findById(1L))
				.thenReturn(Optional.of(sampleUser));
		when(userRepository.findAll())
				.thenReturn(List.of(adminUser));
		when(claimRepository.save(any(Claim.class)))
				.thenReturn(sampleClaim);

		ClaimResponseDto result = claimService.submitClaim(dto);

		assertNotNull(result);
		assertEquals("Travel expenses", result.getDescription());
		assertEquals("SUBMITTED", result.getStatus());
	}

	/**
	 * Test approveClaim updates status to APPROVED.
	 */
	@Test
	void approveClaim_validData_returnsApproved() {
		ClaimActionRequestDto dto = new ClaimActionRequestDto();
		dto.setReviewerId(2L);
		dto.setComment("Looks good");

		Claim freshClaim = new Claim();
		freshClaim.setId(1L);
		freshClaim.setAmount(new BigDecimal("5000"));
		freshClaim.setDate(LocalDate.now());
		freshClaim.setDescription("Travel expenses");
		freshClaim.setStatus(ClaimStatus.SUBMITTED);
		freshClaim.setEmployee(sampleUser);
		freshClaim.setReviewer(adminUser);

		Claim approvedClaim = new Claim();
		approvedClaim.setId(1L);
		approvedClaim.setAmount(new BigDecimal("5000"));
		approvedClaim.setDate(LocalDate.now());
		approvedClaim.setDescription("Travel expenses");
		approvedClaim.setStatus(ClaimStatus.APPROVED);
		approvedClaim.setEmployee(sampleUser);
		approvedClaim.setReviewer(adminUser);
		approvedClaim.setReviewerComment("Looks good");

		when(claimRepository.findById(1L))
				.thenReturn(Optional.of(freshClaim));
		when(claimRepository.save(any(Claim.class)))
				.thenReturn(approvedClaim);

		ClaimResponseDto result = claimService.approveClaim(1L, dto);

		assertNotNull(result);
		assertEquals("APPROVED", result.getStatus());
	}

	/**
	 * Test rejectClaim updates status to REJECTED.
	 */
	@Test
	void rejectClaim_validData_returnsRejected() {
		ClaimActionRequestDto dto = new ClaimActionRequestDto();
		dto.setReviewerId(2L);
		dto.setComment("Missing receipt");

		Claim freshClaim = new Claim();
		freshClaim.setId(1L);
		freshClaim.setAmount(new BigDecimal("5000"));
		freshClaim.setDate(LocalDate.now());
		freshClaim.setDescription("Travel expenses");
		freshClaim.setStatus(ClaimStatus.SUBMITTED);
		freshClaim.setEmployee(sampleUser);
		freshClaim.setReviewer(adminUser);

		Claim rejectedClaim = new Claim();
		rejectedClaim.setId(1L);
		rejectedClaim.setAmount(new BigDecimal("5000"));
		rejectedClaim.setDate(LocalDate.now());
		rejectedClaim.setDescription("Travel expenses");
		rejectedClaim.setStatus(ClaimStatus.REJECTED);
		rejectedClaim.setEmployee(sampleUser);
		rejectedClaim.setReviewer(adminUser);
		rejectedClaim.setReviewerComment("Missing receipt");

		when(claimRepository.findById(1L))
				.thenReturn(Optional.of(freshClaim));
		when(claimRepository.save(any(Claim.class)))
				.thenReturn(rejectedClaim);

		ClaimResponseDto result = claimService.rejectClaim(1L, dto);

		assertNotNull(result);
		assertEquals("REJECTED", result.getStatus());
	}

	/**
	 * Test approveClaim throws error when claim is not SUBMITTED.
	 */
	@Test
	void approveClaim_alreadyApproved_throwsException() {
		sampleClaim.setStatus(ClaimStatus.APPROVED);

		ClaimActionRequestDto dto = new ClaimActionRequestDto();
		dto.setReviewerId(2L);

		when(claimRepository.findById(1L))
				.thenReturn(Optional.of(sampleClaim));

		assertThrows(IllegalArgumentException.class, () ->
				claimService.approveClaim(1L, dto));
	}

	/**
	 * Test getClaimsByEmployee returns paginated claims.
	 */
	@Test
	void getClaimsByEmployee_returnsPagedClaims() {
		Page<Claim> page = new PageImpl<>(List.of(sampleClaim));

		when(userRepository.findById(1L))
				.thenReturn(Optional.of(sampleUser));
		when(claimRepository.findByEmployee(
				any(User.class), any(PageRequest.class)))
				.thenReturn(page);

		Page<ClaimResponseDto> result =
				claimService.getClaimsByEmployee(
						1L, PageRequest.of(0, 10));

		assertNotNull(result);
		assertEquals(1, result.getTotalElements());
	}

	/**
	 * Test getClaimsByReviewer returns paginated claims.
	 */
	@Test
	void getClaimsByReviewer_returnsPagedClaims() {
		Page<Claim> page = new PageImpl<>(List.of(sampleClaim));

		when(userRepository.findById(2L))
				.thenReturn(Optional.of(adminUser));
		when(claimRepository.findByReviewer(
				any(User.class), any(PageRequest.class)))
				.thenReturn(page);

		Page<ClaimResponseDto> result =
				claimService.getClaimsByReviewer(
						2L, PageRequest.of(0, 10));

		assertNotNull(result);
		assertEquals(1, result.getTotalElements());
	}

	/**
	 * Test ClaimValidator throws exception when amount exceeds limit.
	 */
	@Test
	void claimValidator_amountExceedsLimit_throwsException() {
		ClaimValidator validator = new ClaimValidator(userRepository);
		ClaimRequestDto dto = new ClaimRequestDto();
		dto.setEmployeeId(1L);
		dto.setAmount(new BigDecimal("200000"));
		dto.setDate(LocalDate.now());
		dto.setDescription("Too expensive");

		assertThrows(IllegalArgumentException.class, () ->
				validator.validateCreateClaim(dto));
	}

	/**
	 * Test ClaimValidator throws exception when employee not found.
	 */
	@Test
	void claimValidator_employeeNotFound_throwsException() {
		ClaimValidator validator = new ClaimValidator(userRepository);
		ClaimRequestDto dto = new ClaimRequestDto();
		dto.setEmployeeId(99L);
		dto.setAmount(new BigDecimal("5000"));
		dto.setDate(LocalDate.now());
		dto.setDescription("Test");

		when(userRepository.existsById(99L)).thenReturn(false);

		assertThrows(ResourceNotFoundException.class, () ->
				validator.validateCreateClaim(dto));
	}

	/**
	 * Test UserValidator throws exception when email already exists.
	 */
	@Test
	void userValidator_emailAlreadyExists_throwsException() {
		UserValidator validator = new UserValidator(userRepository);
		UserRequestDto dto = new UserRequestDto();
		dto.setName("Test");
		dto.setEmail("existing@company.com");
		dto.setPassword("Test@1234");
		dto.setRole("EMPLOYEE");

		when(userRepository.existsByEmail("existing@company.com"))
				.thenReturn(true);

		assertThrows(IllegalArgumentException.class, () ->
				validator.validateCreateUser(dto));
	}

	/**
	 * Test UserValidator throws exception when user does not exist.
	 */
	@Test
	void userValidator_userNotFound_throwsException() {
		UserValidator validator = new UserValidator(userRepository);

		when(userRepository.existsById(99L)).thenReturn(false);

		assertThrows(ResourceNotFoundException.class, () ->
				validator.validateUserExists(99L));
	}

	/**
	 * Test submitClaim with manager assigned to employee.
	 */
	@Test
	void submitClaim_employeeHasManager_assignsManager() {
		User manager = new User();
		manager.setId(5L);
		manager.setName("Manager");
		manager.setRole(Role.MANAGER);

		User employeeWithManager = new User();
		employeeWithManager.setId(6L);
		employeeWithManager.setName("Employee With Manager");
		employeeWithManager.setEmail("empwm@company.com");
		employeeWithManager.setRole(Role.EMPLOYEE);
		employeeWithManager.setManager(manager);

		Claim claimWithManager = new Claim();
		claimWithManager.setId(10L);
		claimWithManager.setAmount(new BigDecimal("3000"));
		claimWithManager.setDate(LocalDate.now());
		claimWithManager.setDescription("Office supplies");
		claimWithManager.setStatus(ClaimStatus.SUBMITTED);
		claimWithManager.setEmployee(employeeWithManager);
		claimWithManager.setReviewer(manager);

		ClaimRequestDto dto = new ClaimRequestDto();
		dto.setEmployeeId(6L);
		dto.setAmount(new BigDecimal("3000"));
		dto.setDate(LocalDate.now());
		dto.setDescription("Office supplies");

		doNothing().when(claimValidator).validateCreateClaim(any());
		when(userRepository.findById(6L))
				.thenReturn(Optional.of(employeeWithManager));
		when(claimRepository.save(any(Claim.class)))
				.thenReturn(claimWithManager);

		ClaimResponseDto result = claimService.submitClaim(dto);

		assertNotNull(result);
		assertEquals("Office supplies", result.getDescription());
	}

	/**
	 * Test rejectClaim throws exception when wrong reviewer.
	 */
	@Test
	void rejectClaim_wrongReviewer_throwsException() {
		ClaimActionRequestDto dto = new ClaimActionRequestDto();
		dto.setReviewerId(99L);
		dto.setComment("Reject");

		Claim freshClaim = new Claim();
		freshClaim.setId(1L);
		freshClaim.setStatus(ClaimStatus.SUBMITTED);
		freshClaim.setEmployee(sampleUser);
		freshClaim.setReviewer(adminUser);

		when(claimRepository.findById(1L))
				.thenReturn(Optional.of(freshClaim));

		assertThrows(IllegalArgumentException.class, () ->
				claimService.rejectClaim(1L, dto));
	}

	/**
	 * Test approveClaim throws exception when wrong reviewer.
	 */
	@Test
	void approveClaim_wrongReviewer_throwsException() {
		ClaimActionRequestDto dto = new ClaimActionRequestDto();
		dto.setReviewerId(99L);
		dto.setComment("Approve");

		Claim freshClaim = new Claim();
		freshClaim.setId(1L);
		freshClaim.setStatus(ClaimStatus.SUBMITTED);
		freshClaim.setEmployee(sampleUser);
		freshClaim.setReviewer(adminUser);

		when(claimRepository.findById(1L))
				.thenReturn(Optional.of(freshClaim));

		assertThrows(IllegalArgumentException.class, () ->
				claimService.approveClaim(1L, dto));
	}

}