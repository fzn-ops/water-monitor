import { createContext, useContext, useState } from "react";

const ThemeContext = createContext();

export const useTheme = ()=> useContext(ThemeContext);

export const ThemeProvider = ({children})=>{
  const [darkMode,setDarkMode] = useState(false);

  return(
    <ThemeContext.Provider value={{darkMode,setDarkMode}}>
      {children}
    </ThemeContext.Provider>
  )
}