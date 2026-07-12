import { useState, useEffect } from "react"
import Layout from "../components/Layout"
import { getMyProfile, updateMyProfile, changeMyPassword } from "../services/api"
import "./my-profile-page.css"

function EyeIcon({ open }) {
  return open ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.5 18.5 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
      <line x1="1" y1="1" x2="23" y2="23"></line>
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    </svg>
  )
}

function MyProfilePage() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [role, setRole] = useState("")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [pwErrors, setPwErrors] = useState({})
  const [pwMessage, setPwMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [showPw, setShowPw] = useState({})

  useEffect(() => { fetchProfile() }, [])

  async function fetchProfile() {
    try {
      const p = await getMyProfile()
      setName(p.name); setEmail(p.email); setRole(p.role)
    } catch (err) {}
    setLoading(false)
  }

  function validateProfile() {
    const e = {}
    if (!name.trim()) e.name = "Name is required."
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSaveProfile() {
    setMessage("")
    if (!validateProfile()) return
    try {
      const updated = await updateMyProfile({ name })
      const userStr = localStorage.getItem("user")
      if (userStr) {
        const stored = JSON.parse(userStr)
        localStorage.setItem("user", JSON.stringify({ ...stored, name: updated.name }))
      }
      setMessage("Profile updated successfully!")
    } catch (err) {
      setMessage(err.message || "Failed to update profile")
    }
  }

  function validatePassword() {
    const e = {}
    if (!currentPassword) e.currentPassword = "Current password is required."
    if (!newPassword) e.newPassword = "New password is required."
    else if (newPassword.length < 6) e.newPassword = "New password must be at least 6 characters."
    if (newPassword !== confirmPassword) e.confirmPassword = "Passwords do not match."
    setPwErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleChangePassword() {
    setPwMessage("")
    if (!validatePassword()) return
    try {
      await changeMyPassword({
        current_password: btoa(currentPassword),
        new_password: btoa(newPassword)
      })
      setPwMessage("Password changed successfully!")
      setCurrentPassword(""); setNewPassword(""); setConfirmPassword("")
    } catch (err) {
      setPwMessage(err.message || "Failed to change password")
    }
  }

  function toggleShow(key) {
    setShowPw(p => ({ ...p, [key]: !p[key] }))
  }

  if (loading) return <Layout><p className="muted-text">Loading...</p></Layout>

  return (
    <Layout>
      <div className="profile-container">
        <h1 className="profile-title">My Profile</h1>

        <div className="profile-grid">
          <div className="profile-card">
            <h3 className="form-heading">Account Details</h3>

            <label className="profile-label">Full Name</label>
            <input className={`profile-input ${errors.name ? "input-error" : ""}`} value={name} onChange={e => setName(e.target.value)} />
            {errors.name && <p className="error-text">{errors.name}</p>}

            <label className="profile-label">Email</label>
            <input className="profile-input" value={email} disabled />

            <label className="profile-label">Role</label>
            <input className="profile-input" value={role} disabled />

            <button className="issues-button" onClick={handleSaveProfile}>Save Changes</button>
            {message && <p className={`profile-message ${message.includes("success") ? "" : "error-text"}`}>{message}</p>}
          </div>

          <div className="profile-card">
            <h3 className="form-heading">Change Password</h3>

            <label className="profile-label">Current Password</label>
            <div className="pw-input-wrapper">
              <input type={showPw.current ? "text" : "password"} className={`profile-input ${pwErrors.currentPassword ? "input-error" : ""}`} value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
              <span className="pw-eye" onClick={() => toggleShow("current")}><EyeIcon open={showPw.current} /></span>
            </div>
            {pwErrors.currentPassword && <p className="error-text">{pwErrors.currentPassword}</p>}

            <label className="profile-label">New Password</label>
            <div className="pw-input-wrapper">
              <input type={showPw.new ? "text" : "password"} className={`profile-input ${pwErrors.newPassword ? "input-error" : ""}`} value={newPassword} onChange={e => setNewPassword(e.target.value)} />
              <span className="pw-eye" onClick={() => toggleShow("new")}><EyeIcon open={showPw.new} /></span>
            </div>
            {pwErrors.newPassword && <p className="error-text">{pwErrors.newPassword}</p>}

            <label className="profile-label">Confirm New Password</label>
            <div className="pw-input-wrapper">
              <input type={showPw.confirm ? "text" : "password"} className={`profile-input ${pwErrors.confirmPassword ? "input-error" : ""}`} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} />
              <span className="pw-eye" onClick={() => toggleShow("confirm")}><EyeIcon open={showPw.confirm} /></span>
            </div>
            {pwErrors.confirmPassword && <p className="error-text">{pwErrors.confirmPassword}</p>}

            <button className="issues-button" onClick={handleChangePassword}>Update Password</button>
            {pwMessage && <p className={`profile-message ${pwMessage.includes("success") ? "" : "error-text"}`}>{pwMessage}</p>}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default MyProfilePage