import { MdDashboard, MdHistory, MdLocationOn } from "react-icons/md";
import { Link, useLocation } from "react-router-dom";
import logoutIcon from "../assets/Vector.png";
import { useTheme } from "../context/ThemeContext";

export default function Sidebar() {
  const location = useLocation();
  const { darkMode } = useTheme();

  const menus = [
    {
      name: "Dashboard",
      path: "/",
      icon: <MdDashboard size={24} />,
    },
    {
      name: "Location",
      path: "/location",
      icon: <MdLocationOn size={24} />,
    },
    {
      name: "History",
      path: "/history",
      icon: <MdHistory size={24} />,
    },
  ];

  return (
    <div
      style={{
        width: "220px",
        background: darkMode ? "#1f1f1f" : "#f5f5f5",
        color: darkMode ? "white" : "black",
        minHeight: "100vh",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      {/* Profile + Menu */}
      <div>
        <div style={{ textAlign: "center" }}>
          <img
            src="https://i.pravatar.cc/80?img=12"
            alt="Admin"
            style={{ borderRadius: "50%" }}
          />
          <h2>Admin</h2>
          <p style={{ color: "gray" }}>Prime Leonard</p>
        </div>

        <div style={{ marginTop: "40px" }}>
          {menus.map((m) => (
            <Link
              key={m.path}
              to={m.path}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "15px",
                marginBottom: "10px",
                borderRadius: "10px",
                color: darkMode ? "white" : "#333",
                textDecoration: "none",
                background:
                  location.pathname === m.path
                    ? darkMode
                      ? "#333"
                      : "#e8ecef"
                    : "transparent",
              }}
            >
              {m.icon}
              {m.name}
            </Link>
          ))}
        </div>
      </div>

      {/* Logout */}
      <div
        style={{
          marginTop: "40px",
          marginBottom: "30px",
          color: "red",
          display: "flex",
          gap: "10px",
          alignItems: "center",
          cursor: "pointer",
        }}
      >
        <img
          src={logoutIcon}
          alt="Logout"
          style={{
            width: "22px",
            height: "22px",
            objectFit: "contain",
          }}
        />
        <span>LOGOUT</span>
      </div>
    </div>
  );
}