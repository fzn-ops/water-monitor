import { createContext, useContext, useEffect, useState } from "react";

const SensorContext = createContext();
export const useSensor = () => useContext(SensorContext);

export const SensorProvider = ({ children }) => {
  // Inisialisasi state kosong/default
  const [waterLevel, setWaterLevel] = useState(0);
  const [logs, setLogs] = useState([]);
  const [history, setHistory] = useState([]);

  // --- 1. STATE LOKASI AKTIF ---
  // Default saat web pertama dibuka adalah Sungai Ciliwung
  const [activeLocation, setActiveLocation] = useState({
    id: 1,
    name: "Sungai Ciliwung",
    city: "Kota Ngawi Selatan",
    cameraUrl: "http://192.168.137.18:8080/video" // Sesuaikan IP-nya
  });

  // Ambil alamat API dari file .env (atau gunakan localhost sebagai fallback)
  const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

  const getStatus = (level) => {
    if (level >= 100) return "Bahaya";
    if (level >= 50) return "Waspada";
    return "Aman";
  };

  const fetchSensorData = async () => {
    try {
      // --- 2. UBAH FETCH URL ---
      // Sekarang otomatis menarik data milik lokasi yang sedang aktif saja
      const response = await fetch(`${API_URL}/readings/?location_id=${activeLocation.id}&limit=10`);
      
      if (!response.ok) throw new Error("Gagal mengambil data dari API");
      
      const data = await response.json();

      if (data && data.length > 0) {
        // Update Level Air Saat Ini 
        const currentLevel = data[0].water_level_cm;
        setWaterLevel(currentLevel);

        // Update Logs 
        const newLogs = data.slice(0, 3).map((item) => {
          const dateObj = new Date(item.recorded_at); 
          return {
            status: getStatus(item.water_level_cm),
            level: item.water_level_cm,
            time: dateObj.toLocaleTimeString("id-ID")
          };
        });
        setLogs(newLogs);

        // Update History Chart
        const newHistory = data.map((item) => {
          const dateObj = new Date(item.recorded_at);
          return {
            time: dateObj.toLocaleTimeString("id-ID", { hour: '2-digit', minute: '2-digit' }),
            level: item.water_level_cm
          };
        }).reverse(); 
        
        setHistory(newHistory);
      } else {
        // Jika belum ada data untuk lokasi ini, kosongkan grafik
        setWaterLevel(0);
        setLogs([]);
        setHistory([]);
      }
    } catch (error) {
      console.error("Error menarik data sensor:", error);
    }
  };

  useEffect(() => {
    // Tarik data seketika saat web dimuat ATAU saat lokasi diganti
    fetchSensorData();

    // Polling tiap 5 detik
    const interval = setInterval(() => {
      fetchSensorData();
    }, 5000);

    // Bersihkan interval lama jika lokasi berubah agar tidak bentrok
    return () => clearInterval(interval);
    
  // --- 3. TAMBAHKAN DEPENDENCY ---
  // Efek ini akan di-restart ulang otomatis jika ID lokasi berubah
  }, [activeLocation.id]);

  return (
    // --- 4. EXPORT STATE LOKASI AGAR BISA DIPAKAI KOMPONEN LAIN ---
    <SensorContext.Provider value={{ 
      waterLevel, 
      logs, 
      history, 
      getStatus,
      activeLocation,       // Diekspor agar RiverPanel bisa baca namanya
      setActiveLocation     // Diekspor agar Topbar bisa mengubah lokasinya
    }}>
      {children}
    </SensorContext.Provider>
  );
};