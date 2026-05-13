import { BrowserRouter,Routes,Route } from "react-router-dom";
import Dashboard from "./pages/admin/Dashboard";
import Location from "./pages/admin/Location";
import History from "./pages/admin/History";

export default function App(){
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard/>}/>
        <Route path="/location" element={<Location/>}/>
        <Route path="/history" element={<History/>}/>
      </Routes>
    </BrowserRouter>
  )
}