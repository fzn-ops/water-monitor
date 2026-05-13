import { createContext, useContext, useEffect, useState } from "react";

const SensorContext = createContext();
export const useSensor = ()=>useContext(SensorContext);

export const SensorProvider = ({children})=>{
  const [waterLevel,setWaterLevel] = useState(5);
  const [logs,setLogs] = useState([
    {status:"Bahaya",level:125,time:"20:20:30"},
    {status:"Waspada",level:95,time:"20:10:30"},
    {status:"Aman",level:20,time:"20:00:30"},
  ]);

  const [history,setHistory] = useState([
    {time:"00",level:60},
    {time:"01:00",level:170},
    {time:"02:00",level:130},
    {time:"03:00",level:120},
    {time:"04:00",level:55},
    {time:"05:00",level:15},
    {time:"06:00",level:115},
    {time:"07:00",level:80},
    {time:"08:00",level:110},
    {time:"09:00",level:200},
  ]);

  const getStatus = (level)=>{
    if(level >=100) return "Bahaya";
    if(level >=50) return "Waspada";
    return "Aman";
  }

  useEffect(()=>{
    const interval = setInterval(()=>{
      const level = Math.floor(Math.random()*150)+1;
      const status = getStatus(level);
      const time = new Date().toLocaleTimeString("id-ID");

      setWaterLevel(level);

      setLogs(prev=>[
        {status,level,time},
        ...prev.slice(0,2)
      ]);

      setHistory(prev=>[
        ...prev.slice(1),
        {
          time:new Date().toLocaleTimeString("id-ID",{hour:'2-digit',minute:'2-digit'}),
          level
        }
      ]);
    },3000);

    return ()=>clearInterval(interval);
  },[]);

  return(
    <SensorContext.Provider value={{waterLevel,logs,history,getStatus}}>
      {children}
    </SensorContext.Provider>
  )
}