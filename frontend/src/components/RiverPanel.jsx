import { useState } from "react";
import { useTheme } from "../context/ThemeContext";
import { useSensor } from "../context/SensorContext"; // 1. Import Context

export default function RiverPanel(){
  const { darkMode } = useTheme();
  
  // 2. Tarik data lokasi aktif dari Context
  const { activeLocation } = useSensor();
  
  const [isLive, setIsLive] = useState(false);

  const theme = {
    bg: darkMode ? "#1f1f1f" : "white",
    text: darkMode ? "white" : "black",
    subtext: darkMode ? "#bcbcbc" : "#2b7cff",
    btnStart: "#28a745", 
    btnStop: "#dc3545"   
  };

  const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  
  // 3. Gunakan URL kamera dinamis berdasarkan lokasi yang dipilih
  const streamUrl = `${API_URL}/camera/stream?camera_source=${activeLocation.cameraUrl}`;
  const staticImage = "https://images.unsplash.com/photo-1506744038136-46273834b3fb";

  const toggleCamera = async () => {
    try {
      if (!isLive) {
        console.log(`Menyalakan Worker untuk ${activeLocation.name}...`);
        await fetch(`${API_URL}/camera/start`, { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                location_id: activeLocation.id, // Gunakan ID dinamis
                location_name: activeLocation.name, // Gunakan nama lokasi dinamis
                camera_source: activeLocation.cameraUrl, // Gunakan URL dinamis
            })
        });
        
        setIsLive(true);
      } else {
        console.log(`Mematikan Worker untuk ${activeLocation.name}...`);
        await fetch(`${API_URL}/camera/stop?location_id=${activeLocation.id}`, { 
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        
        setIsLive(false);
      }
    } catch (error) {
      console.error("Gagal menghubungi API FastAPI:", error);
      alert("Gagal menyalakan/mematikan kamera backend.");
    }
  };

  return(
    <div style={{
      background: theme.bg,
      color: theme.text,
      padding:"20px",
      borderRadius:"20px"
    }}>
      
      <img
        src={isLive ? streamUrl : staticImage} 
        alt={`Pemantauan ${activeLocation.name}`}
        style={{
          width:"100%",
          height:"280px",
          objectFit:"cover",
          borderRadius:"20px",
          backgroundColor: "#000",
          transition: "0.3s"
        }}
        onError={(e) => {
          e.target.onerror = null; 
          e.target.src = staticImage;
        }}
      />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "15px" }}>
        <div>
          {/* 4. Tampilkan Nama Sungai dan Kota secara Dinamis */}
          <h3 style={{margin: "0 0 5px 0"}}>{activeLocation.name}</h3>
          <span style={{color:theme.subtext, fontSize: "0.9em"}}>{activeLocation.city}</span>
        </div>

        <button 
          onClick={toggleCamera}
          style={{
            backgroundColor: isLive ? theme.btnStop : theme.btnStart,
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: "bold",
            transition: "0.2s"
          }}
        >
          {isLive ? "⏹ Matikan Kamera" : "▶ Nyalakan Kamera"}
        </button>
      </div>

    </div>
  )
}