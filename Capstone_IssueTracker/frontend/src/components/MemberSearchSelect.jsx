import { useState, useRef, useEffect } from "react"
import "./MemberSearchSelect.css"

function MemberSearchSelect({ options, onSelect, placeholder = "Search member..." }) {
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)
  const wrapperRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const filtered = options.filter(o =>
    o.name.toLowerCase().includes(query.toLowerCase()) ||
    o.email?.toLowerCase().includes(query.toLowerCase())
  )

  function handlePick(option) {
    onSelect(option)
    setQuery("")
    setOpen(false)
  }

  return (
    <div className="member-search-wrapper" ref={wrapperRef}>
      <input
        className="projects-input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
        onFocus={() => setOpen(true)}
      />
      {open && filtered.length > 0 && (
        <div className="member-search-dropdown">
          {filtered.map(o => (
            <div key={o.id} className="member-search-option" onClick={() => handlePick(o)}>
              {o.name} <span className="member-search-role">({o.role})</span>
            </div>
          ))}
        </div>
      )}
      {open && query && filtered.length === 0 && (
        <div className="member-search-dropdown">
          <div className="member-search-empty">No matching users</div>
        </div>
      )}
    </div>
  )
}

export default MemberSearchSelect