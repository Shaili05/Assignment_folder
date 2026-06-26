import { useState } from "react"
import LoginPage from "./pages/login-page"
import RegisterPage from "./pages/register-page"
import "./App.css"

function App() {
  const [currentPage, setCurrentPage] = useState("login")

  return (
    <div>
      {currentPage === "login" && (
        <LoginPage onNavigate={setCurrentPage} />
      )}
      {currentPage === "register" && (
        <RegisterPage onNavigate={setCurrentPage} />
      )}
    </div>
  )
}

export default App