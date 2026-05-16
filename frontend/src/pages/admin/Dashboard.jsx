import AdminLayout from "../../layouts/AdminLayout";
import StatusCards from "../../components/StatusCards";
import RiverPanel from "../../components/RiverPanel";
import WarningLogs from "../../components/WarningLogs";
import WaterChart from "../../components/WaterChart";

export default function Dashboard(){
  return(
    <AdminLayout>
      <StatusCards/>

      <div style={{display:"grid",gridTemplateColumns:"2fr 1.4fr",gap:"20px",marginTop:"20px"}}>
        <RiverPanel/>
        <WarningLogs/>
      </div>

      <WaterChart/>
    </AdminLayout>
  )
}