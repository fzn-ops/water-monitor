import { useState, useEffect, useRef } from "react";
import { MdNotificationsNone } from "react-icons/md";
import { useTheme } from "../context/ThemeContext";
import { useSensor } from "../context/SensorContext";

export default function Topbar({ onSelectLocation }) {
  const { darkMode, setDarkMode } = useTheme();
  const { setActiveLocation } = useSensor();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const searchRef = useRef(null);

  // --- STATE BARU UNTUK DATA API ---
  const [allLocations, setAllLocations] = useState([]);
  const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

  // 1. MENGAMBIL DATA LOKASI DARI FASTAPI SAAT WEB DIMUAT
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        // Asumsi endpoint API kamu adalah /locations/
        const response = await fetch(`${API_URL}/locations/`);
        if (!response.ok) throw new Error("Gagal mengambil data");
        
        const data = await response.json();
        setAllLocations(data); // Simpan data dari database ke state
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    };

    fetchLocations();
  }, []); // Array kosong [] artinya fetch hanya berjalan 1 kali saat awal render

  // 2. FILTER DATA API BERDASARKAN KETIKAN USER
// 2. FILTER DATA API BERDASARKAN KETIKAN USER
  useEffect(() => {
    if (query.trim().length > 0) {
      const filtered = allLocations.filter(loc => {
        // Karena datamu pakai "name", kita panggil loc.name
        const locationName = loc.name || ""; 
        
        // Kita hanya mencari berdasarkan nama lokasi saja
        return locationName.toLowerCase().includes(query.toLowerCase());
      });
      setResults(filtered);
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [query, allLocations]);

  // Logika klik di luar kotak pencarian
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) setIsOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

const handleSelect = (location) => {
    const displayName = location.name; 
    
    setQuery(displayName); 
    setIsOpen(false);        
    
    // Simpan lokasi ke dalam SensorContext
    setActiveLocation({
      id: location.id,
      name: location.name,
      city: `Lat: ${location.latitude}, Lon: ${location.longitude}`, 
      
      // Ambil dari database (location.camera_url), JIKA kosong baru pakai fallback IP HP-mu
      cameraUrl: location.camera_url || "http://192.168.137.18:8080/video",
      
      // Ambil gambar dari database juga
      imageUrl: location.image_url 
    });

    if (onSelectLocation) {
      onSelectLocation(location);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "25px" }}>
      
      {/* --- KOTAK PENCARIAN --- */}
      <div ref={searchRef} style={{ width: "55%", position: "relative" }}>
        <input
          placeholder="Cari Lokasi Sungai..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length > 0 && setIsOpen(true)}
          style={{
            width: "100%", padding: "16px", border: "none", borderRadius: "15px",
            background: darkMode ? "#2d2d2d" : "#ddd", color: darkMode ? "white" : "black",
            fontSize: "16px", outline: "none"
          }}
        />

        {/* --- DROPDOWN MELAYANG --- */}
        {isOpen && results.length > 0 && (
          <div style={{
            position: "absolute", top: "60px", left: 0, right: 0,
            background: darkMode ? "#1f1f1f" : "white",
            border: `1px solid ${darkMode ? "#444" : "#ccc"}`,
            borderRadius: "15px", boxShadow: "0px 8px 16px rgba(0,0,0,0.2)",
            zIndex: 999, overflow: "hidden"
          }}>
            {results.map((loc) => (
              <div
                key={loc.id}
                onClick={() => handleSelect(loc)}
                style={{
                  padding: "15px 20px", cursor: "pointer", display: "flex", flexDirection: "column",
                  borderBottom: `1px solid ${darkMode ? "#444" : "#eee"}`, transition: "background 0.2s"
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = darkMode ? "#333" : "#f1f1f1"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
              >
                {/* Nama Sungai */}
                <strong style={{ color: darkMode ? "white" : "black", fontSize: "15px" }}>
                  {loc.name}
                </strong>
                {/* Tampilkan Latitude dan Longitude */}
                <span style={{ fontSize: "13px", color: darkMode ? "#aaa" : "#666", marginTop: "4px" }}>
                  Titik Koordinat: {loc.latitude}, {loc.longitude}
                </span>
              </div>
            ))}
          </div>
        )}

        {isOpen && results.length === 0 && query.length > 0 && (
          <div style={{
            position: "absolute", top: "60px", left: 0, right: 0,
            background: darkMode ? "#1f1f1f" : "white", padding: "15px 20px",
            borderRadius: "15px", border: `1px solid ${darkMode ? "#444" : "#ccc"}`,
            boxShadow: "0px 8px 16px rgba(0,0,0,0.2)", zIndex: 999, color: darkMode ? "#aaa" : "#666"
          }}>
            Lokasi tidak ditemukan.
          </div>
        )}
      </div>

      {/* --- BAGIAN KANAN TOPBAR (TIDAK BERUBAH) --- */}
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        <div style={{ background: darkMode ? "#2d2d2d" : "#ddd", padding: "10px 15px", borderRadius: "20px" }}>
          <button onClick={() => setDarkMode(false)} style={{ border: "none", background: "transparent", cursor: "pointer" }}>☀️</button>
          <button onClick={() => setDarkMode(true)} style={{ border: "none", background: "transparent", cursor: "pointer" }}>🌙</button>
        </div>
        <div style={{ position: "relative", fontSize: "24px", color: darkMode ? "white" : "black" }}>
          <MdNotificationsNone />
          <span style={{ position: "absolute", top: "0", right: "0", width: "8px", height: "8px", background: "red", borderRadius: "50%" }}></span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", color: darkMode ? "white" : "black" }}>
          <img src="https://i.pravatar.cc/40?img=12" alt="Profile" style={{ borderRadius: "50%" }} />
          <b>Leonard</b>
        </div>
      </div>
    </div>
  )
}