import { useTheme } from "../context/ThemeContext";

export default function RiverPanel(){
  const { darkMode } = useTheme();

  const theme = {
    bg: darkMode ? "#1f1f1f" : "white",
    text: darkMode ? "white" : "black",
    subtext: darkMode ? "#bcbcbc" : "#2b7cff"
  };

  return(
    <div style={{
      background: theme.bg,
      color: theme.text,
      padding:"20px",
      borderRadius:"20px"
    }}>
      <img
        src="https://images.unsplash.com/photo-1506744038136-46273834b3fb"
        style={{
          width:"100%",
          height:"280px",
          objectFit:"cover",
          borderRadius:"20px"
        }}
      />
      <h3 style={{marginBottom:"0"}}>Sungai ciliwung</h3>
      <span style={{color:theme.subtext}}>Kota Ngawi Selatan</span>
    </div>
  )
}