// App.js
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from './LoginPage';
import LayoutPage from './LayoutPage';
import HomePage from './HomePage';
import LogoutPage from './LogoutPage';
import CreatePacientPage from './CreatePacientPage';
import PacientPage from './PacientPage';
import DoctorPage from './DoctorPage';
const App = () => {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState('');
  const [rol, setRol] = useState('');
  const [uid, setUid] = useState('');//Doar pentru modificarea informatiilor din HomePage.
  const [cnp, setCNP] = useState('');
  const [idDoctor, setIdDoctor] = useState('');
  const resetProps=()=>{
    setToken('');
    setUsername('');
    setRol('');
    setUid('');
    setCNP('');
    setIdDoctor('');
  };
  return (//render
    <BrowserRouter>
    <Routes>
        <Route path="/" element={<LayoutPage />}>
        <Route index element={<HomePage token={token} cnp={cnp} rol={rol} username={username} uid={uid} setUsername={setUsername} idDoctor={idDoctor} resetProps={resetProps}/>} />
        <Route path="login" element={<LoginPage setToken={setToken} token={token} username={username} setUsername={setUsername} setUid={setUid} rol={rol} setRol={setRol} setCNP={setCNP} setIdDoctor={setIdDoctor} resetProps={resetProps}/>} />
        <Route path="logout" element={<LogoutPage token={token} resetProps={resetProps}/>} />
        <Route path="crearepacient" element={<CreatePacientPage cnp={cnp} idDoctor={idDoctor} setCNP={setCNP} token={token} resetProps={resetProps}/>} />
        <Route path="pacient" element={<PacientPage token={token} resetProps={resetProps}/>} />
        <Route path="doctor" element={<DoctorPage token={token} resetProps={resetProps}/>} />
        <Route path="*" element={<LoginPage setToken={setToken} token={token} username={username} setUsername={setUsername} setUid={setUid} rol={rol} setRol={setRol} setCNP={setCNP} setIdDoctor={setIdDoctor} resetProps={resetProps}/>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

