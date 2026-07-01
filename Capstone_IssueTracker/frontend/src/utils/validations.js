export function validateLogin(email, password) {
  const errors = {}
  if (!email.trim()) {
    errors.email = "Email is required."
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter a valid email address."
  }
  if (!password) {
    errors.password = "Password is required."
  }
  return errors
}

export function validateRegister(name, email, password) {
  const errors = {}
  if (!name.trim()) {
    errors.name = "Full name is required."
  }
  if (!email.trim()) {
    errors.email = "Email is required."
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter a valid email address."
  }
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