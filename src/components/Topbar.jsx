import { MdNotificationsNone } from "react-icons/md";
import { useTheme } from "../context/ThemeContext";

export default function Topbar(){
  const {darkMode,setDarkMode} = useTheme();

  return(
    <div style={{
      display:"flex",
      justifyContent:"space-between",
      alignItems:"center",
      marginBottom:"25px"
    }}>
      <input
        placeholder="Cari Lokasi"
        style={{
          width:"55%",
          padding:"16px",
          border:"none",
          borderRadius:"15px",
          background: darkMode ? "#2d2d2d" : "#ddd",
          color: darkMode ? "white" : "black",
          fontSize:"16px"
        }}
      />

      <div style={{display:"flex",alignItems:"center",gap:"20px"}}>
        <div style={{
          background: darkMode ? "#2d2d2d" : "#ddd",
          padding:"10px 15px",
          borderRadius:"20px"
        }}>
          <button onClick={()=>setDarkMode(false)} style={{border:"none",background:"transparent",cursor:"pointer"}}>☀️</button>
          <button onClick={()=>setDarkMode(true)} style={{border:"none",background:"transparent",cursor:"pointer"}}>🌙</button>
        </div>

        <div style={{position:"relative",fontSize:"24px",color:darkMode?"white":"black"}}>
          <MdNotificationsNone />
          <span style={{
            position:"absolute",
            top:"0",
            right:"0",
            width:"8px",
            height:"8px",
            background:"red",
            borderRadius:"50%"
          }}></span>
        </div>

        <div style={{display:"flex",alignItems:"center",gap:"10px",color:darkMode?"white":"black"}}>
          <img src="https://i.pravatar.cc/40?img=12" style={{borderRadius:"50%"}} />
          <b>Leonard</b>
        </div>
      </div>
    </div>
  )
}