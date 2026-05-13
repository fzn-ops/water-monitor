import { useSensor } from "../context/SensorContext";
import { useTheme } from "../context/ThemeContext";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function WaterChart() {
  const { history } = useSensor();
  const { darkMode } = useTheme();

  const theme = {
    bg: darkMode ? "#1f1f1f" : "white",
    text: darkMode ? "white" : "black",
    axis: darkMode ? "#bcbcbc" : "#666",
    tooltipBg: darkMode ? "#333" : "#fff",
    border: "#2b7cff",
  };

  return (
    <div
      style={{
        background: theme.bg,
        color: theme.text,
        padding: "30px",
        borderRadius: "28px",
        marginTop: "20px",
        boxShadow: darkMode
          ? "none"
          : "0 4px 20px rgba(0,0,0,0.05)",
      }}
    >
      {/* Judul */}
      <div
        style={{
          marginBottom: "20px",
          display: "flex",
          alignItems: "baseline",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: "22px",
            fontWeight: "700",
          }}
        >
          Grafik Ketinggian Air
        </h2>

        <span
          style={{
            fontSize: "14px",
            color: darkMode ? "#ccc" : "#555",
          }}
        >
          (24 jam terakhir dalam cm)
        </span>
      </div>

      {/* Area Grafik + Keterangan */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          alignItems: "flex-start",
        }}
      >
        {/* Grafik */}
        <div
          style={{
            flex: 1,
            border: `3px solid ${theme.border}`,
            borderRadius: "4px",
            padding: "10px",
          }}
        >
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={history}>
              <CartesianGrid vertical={false} stroke="transparent" />

              <XAxis
                dataKey="time"
                stroke={theme.axis}
                tick={{ fill: theme.axis, fontSize: 12 }}
              />

              <YAxis
                stroke={theme.axis}
                tick={{ fill: theme.axis, fontSize: 12 }}
              />

              <Tooltip
                contentStyle={{
                  background: theme.tooltipBg,
                  border: "none",
                  color: theme.text,
                  borderRadius: "8px",
                }}
              />

              <Line
                type="monotone"
                dataKey="level"
                stroke="#2b7cff"
                strokeWidth={2}
                dot={{
                  r: 4,
                  fill: "#ffffff",
                  stroke: "#666",
                  strokeWidth: 1.5,
                }}
                activeDot={{
                  r: 6,
                  fill: "#2b7cff",
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Legend kanan */}
        <div
          style={{
            minWidth: "90px",
            fontSize: "14px",
            lineHeight: 1.8,
            marginTop: "4px",
          }}
        >
          <div style={{ marginBottom: "20px" }}>
            <div style={{ color: "#ff4d4f", fontWeight: "600" }}>Bahaya</div>
            <div style={{ color: theme.text }}>&gt;100 cm</div>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <div style={{ color: "#f59e0b", fontWeight: "600" }}>Waspada</div>
            <div style={{ color: theme.text }}>50 - 100 cm</div>
          </div>

          <div>
            <div style={{ color: "#22c55e", fontWeight: "600" }}>Aman</div>
            <div style={{ color: theme.text }}>&lt;50 cm</div>
          </div>
        </div>
      </div>
    </div>
  );
}