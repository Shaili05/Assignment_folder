export function validateEmail(email) {
  if (!email.trim()) return "Email is required."
  const strictRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z]+\.com$/
  if (!strictRegex.test(email)) {
    return "Enter a valid email address (letters only after @, must end in .com)."
  }
  return null
}

export function validateLogin(email, password) {
  const errors = {}
  const emailError = validateEmail(email)
  if (emailError) errors.email = emailError
  if (!password) {
    errors.password = "Password is required."
  }
  return errors
}

export function validateRegister(name, email, password) {
  const errors = {}
  if (!name.trim()) {
    errors.name = "Full name is required."
  } else if (!/^[a-zA-Z\s]+$/.test(name.trim())) {
    errors.name = "Name should only contain letters and spaces."
  }
  const emailError = validateEmail(email)
  if (emailError) errors.email = emailError
  if (!password) {
    errors.password = "Password is required."
  } else if (password.length < 6) {
    errors.password = "Password must be at least 6 characters long."
  } else if (!/[A-Z]/.test(password)) {
    errors.password = "Password must contain one uppercase letter."
  } else if (!/[a-z]/.test(password)) {
    errors.password = "Password must contain one lowercase letter."
  } else if (!/[0-9]/.test(password)) {
    errors.password = "Password must contain one digit."
  } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.password = "Password must contain one special character."
  }
  return errors
}