import { useState, useEffect, useRef } from "react";
import { useTheme } from "../context/ThemeContext";

export default function SearchBar({ onSelectLocation }) {
  const { darkMode } = useTheme();
  
  // State untuk pencarian
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  
  // Referensi untuk mendeteksi klik di luar kotak pencarian
  const searchRef = useRef(null);

  const theme = {
    bg: darkMode ? "#2d2d2d" : "#f1f3f4",
    text: darkMode ? "white" : "black",
    dropdownBg: darkMode ? "#1f1f1f" : "white",
    hoverBg: darkMode ? "#3d3d3d" : "#f8f9fa",
    border: darkMode ? "#444" : "#e0e0e0"
  };

  // --- DATA DUMMY (Nanti bisa diganti dengan Fetch API dari FastAPI) ---
  const locations = [
    { id: 1, name: "Sungai Ciliwung", city: "Kota Ngawi Selatan" },
    { id: 2, name: "Sungai Cisadane", city: "Kota Tangerang" },
    { id: 3, name: "Sungai Bengawan Solo", city: "Kota Solo" },
  ];

  // Efek untuk menyaring data setiap kali user mengetik
  useEffect(() => {
    if (query.trim().length > 0) {
      const filtered = locations.filter(loc => 
        loc.name.toLowerCase().includes(query.toLowerCase()) ||
        loc.city.toLowerCase().includes(query.toLowerCase())
      );
      setResults(filtered);
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [query]);

  // Efek untuk menutup dropdown jika user klik di luar kotak
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (location) => {
    setQuery(location.name); // Isi input dengan lokasi yang dipilih
    setIsOpen(false);        // Tutup dropdown
    
    // Kirim ID lokasi ke komponen induk (misal: untuk mengubah isi Dashboard)
    if (onSelectLocation) {
      onSelectLocation(location.id);
    }
  };

  return (
    <div ref={searchRef} style={{ position: "relative", width: "400px" }}>
      
      {/* Input Pencarian */}
      <input
        type="text"
        placeholder="Cari Lokasi..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => query.length > 0 && setIsOpen(true)}
        style={{
          width: "100%",
          padding: "10px 15px",
          borderRadius: "20px",
          border: `1px solid ${theme.border}`,
          background: theme.bg,
          color: theme.text,
          outline: "none"
        }}
      />

      {/* Kotak Dropdown Hasil Pencarian */}
      {isOpen && results.length > 0 && (
        <div style={{
          position: "absolute",
          top: "45px", // Jarak dari input box
          left: 0,
          right: 0,
          background: theme.dropdownBg,
          border: `1px solid ${theme.border}`,
          borderRadius: "10px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          zIndex: 50, // PENTING: Agar melayang di atas card lain
          overflow: "hidden"
        }}>
          {results.map((loc) => (
            <div
              key={loc.id}
              onClick={() => handleSelect(loc)}
              style={{
                padding: "12px 15px",
                cursor: "pointer",
                borderBottom: `1px solid ${theme.border}`,
                display: "flex",
                flexDirection: "column"
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = theme.hoverBg}
              onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            >
              <strong style={{ color: theme.text }}>{loc.name}</strong>
              <span style={{ fontSize: "0.8em", color: "#888" }}>{loc.city}</span>
            </div>
          ))}
        </div>
      )}
      
      {/* Pesan jika tidak ditemukan */}
      {isOpen && results.length === 0 && query.length > 0 && (
        <div style={{
          position: "absolute", top: "45px", left: 0, right: 0,
          background: theme.dropdownBg, padding: "12px 15px",
          borderRadius: "10px", border: `1px solid ${theme.border}`,
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)", zIndex: 50, color: "#888"
        }}>
          Lokasi tidak ditemukan
        </div>
      )}

    </div>
  );
}