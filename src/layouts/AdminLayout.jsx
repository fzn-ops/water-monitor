import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { useTheme } from "../context/ThemeContext";

export default function AdminLayout({children}){
  const {darkMode} = useTheme();

  return(
    <div style={{
      display:"flex",
      background:darkMode?"#121212":"#efefef",
      color:darkMode?"white":"black"
    }}>
      <Sidebar/>
      <div style={{flex:1,padding:"20px"}}>
        <Topbar/>
        {children}
      </div>
    </div>
  )
}