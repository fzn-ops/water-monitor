import { useSensor } from "../context/SensorContext";
import { useTheme } from "../context/ThemeContext";

// Gambar berada di folder src/assets
import waterIcon from "../assets/air.png";
import safeIcon from "../assets/aman.png";
import dangerIcon from "../assets/bahaya.png";
import lastupdateIcon from "../assets/clock.png";
import warningIcon from "../assets/waspada.png";

export default function StatusCards() {
  const { waterLevel, currentStatus, dangerThreshold } = useSensor();
  const { darkMode } = useTheme();
  const status = currentStatus;

  // Tentukan ikon berdasarkan status
  let statusIcon = safeIcon;

  if (status === "Bahaya") {
    statusIcon = dangerIcon;
  } else if (status === "Waspada" || status === "Siaga") {
    statusIcon = warningIcon;
  }

  const card = {
    background: darkMode ? "#1f1f1f" : "white",
    padding: "30px",
    borderRadius: "20px",
    color: darkMode ? "white" : "black",
    boxShadow: darkMode
      ? "none"
      : "0 4px 20px rgba(0,0,0,0.05)",
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "20px",
      }}
    >
<div
  style={{
    ...card,
    minHeight: "180px",
  }}
>
  {/* Judul */}
  <p
    style={{
      margin: 0,
      marginTop: "5px", // Naikkan tulisan ke atas
      fontSize: "18px",
    }}
  >
    Status Saat Ini
  </p>

  {/* Icon + Status */}
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "20px",
      marginTop: "35px",
    }}
  >
    {/* Gambar */}
    <img
      src={statusIcon}
      alt={status}
      style={{
        width: "90px",
        height: "90px",
        objectFit: "contain",
        flexShrink: 0,
      }}
    />

    {/* Status */}
    <h1
      style={{
        margin: 0,
        fontSize: "60px",
        fontWeight: "700",
      }}
    >
      {status}
    </h1>
  </div>
</div>

      {/* TINGGI AIR SAAT INI */}
      <div
        style={{
          ...card,
          minHeight: "180px",
        }}
      >
        {/* Judul */}
        <p
          style={{
            margin: 0,
            fontSize: "18px",
          }}
        >
          Tinggi Air Saat Ini
        </p>

        {/* Icon + Nilai */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
            marginTop: "20px",
          }}
        >
          {/* Gambar */}
          <img
            src={waterIcon}
            alt="Tinggi Air"
            style={{
              width: "90px",
              height: "90px",
              objectFit: "contain",
              flexShrink: 0,
            }}
          />

          {/* Nilai air */}
          <h1
            style={{
              margin: 0,
              fontSize: "48px",
              fontWeight: "700",
            }}
          >
            {waterLevel} cm
          </h1>
        </div>

        {/* Keterangan ambang bahaya */}
        <p
          style={{
            marginTop: "12px",
            marginBottom: 0,
            fontSize: "16px",
            color: darkMode ? "#ddd" : "#444",
          }}
        >
          <span style={{ color: "#ff6b6b" }}>
            ({Math.max(0, dangerThreshold - waterLevel).toFixed(2)}cm)
          </span>{" "}
          lagi dari ambang bahaya
        </p>
      </div>

      {/* PERUBAHAN TERAKHIR */}
      <div
        style={{
          ...card,
          minHeight: "180px",
        }}
      >
        {/* Judul */}
        <p
          style={{
            margin: 0,
            fontSize: "18px",
          }}
        >
          Waktu Saat Ini
        </p>
          
        {/* Icon + Waktu */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
            marginTop: "20px",
          }}
        >
          {/* Gambar Jam */}
          <img
            src={lastupdateIcon}
            alt="Last Update"
            style={{
              width: "90px",
              height: "90px",
              objectFit: "contain",
              flexShrink: 0,
            }}
          />

          {/* Waktu */}
          <h1
            style={{
              margin: 0,
              fontSize: "40px",
              fontWeight: "700",
            }}
          >
            {new Date().toLocaleTimeString("id-ID")}
          </h1>
        </div>

        {/* Tanggal */}
        <p
          style={{
            marginTop: "12px",
            marginBottom: 0,
            fontSize: "16px",
            color: darkMode ? "#ddd" : "#666",
          }}
        >
          {new Date().toLocaleDateString("id-ID", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
        </p>
      </div>
    </div>
  );
}