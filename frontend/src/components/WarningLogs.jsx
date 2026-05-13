import { useSensor } from "../context/SensorContext";
import { useTheme } from "../context/ThemeContext";

import bahayaImg from "../assets/bahaya.png";
import amanImg from "../assets/aman.png";
import waspadaImg from "../assets/waspada.png";

export default function WarningLogs() {
  const { logs } = useSensor();
  const { darkMode } = useTheme();

  const theme = {
    bg: darkMode ? "#1f1f1f" : "white",
    text: darkMode ? "white" : "black",
    subtext: darkMode ? "#bcbcbc" : "#555",
    border: darkMode ? "#333" : "#ccc",
  };

  const getColor = (status) => {
    if (status === "Bahaya") return "red";
    if (status === "Waspada") return "orange";
    return "green";
  };

  const getImage = (status) => {
    if (status === "Bahaya") return bahayaImg;
    if (status === "Waspada") return waspadaImg;
    return amanImg;
  };

  return (
    <div
      style={{
        background: theme.bg,
        color: theme.text,
        padding: "20px",
        borderRadius: "20px",
        height: "100%",
      }}
    >
      <h3>Log Peringatan Terbaru</h3>

      {logs.map((log, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "15px 0",
            borderBottom: `1px solid ${theme.border}`,
          }}
        >
          {/* Kiri: gambar + status */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <img
              src={getImage(log.status)}
              alt={log.status}
              style={{
                width: "28px",
                height: "28px",
                objectFit: "contain",
              }}
            />

            <div>
              <b style={{ color: getColor(log.status) }}>{log.status}</b>
              <br />
              <span style={{ color: theme.subtext }}>
                Tinggi air mencapai {log.level} cm
              </span>
            </div>
          </div>

          {/* Kanan: waktu */}
          <div style={{ color: theme.subtext }}>
            {log.time}
          </div>
        </div>
      ))}
    </div>
  );
}