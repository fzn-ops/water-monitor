import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { SensorProvider } from "./context/SensorContext";
import { ThemeProvider } from "./context/ThemeContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider>
      <SensorProvider>
        <App />
      </SensorProvider>
    </ThemeProvider>
  </React.StrictMode>
);