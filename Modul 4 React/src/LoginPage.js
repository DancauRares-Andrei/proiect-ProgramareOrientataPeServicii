import React, { useState } from 'react';
import { Link } from 'react-router-dom';
const LoginPage = (props) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorLoginMessage, setErrorLoginMessage] = useState('');
  const handleLogin = async () => {
  if (!username || !password) {
      console.error('Username și parolă sunt obligatorii');
      return;
    }
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch('http://localhost:8002/token', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
      body: formData,
    });
    if(response.status===401){
        const resp=await response.json();
        setErrorLoginMessage(resp.detail);
    }
    else if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    props.setToken(data.access_token);
    props.setUsername(username);
    const response1 = await fetch('http://localhost:8002/api/medical_office_user?username='+username, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${data.access_token}`,
      },
    });
    if (!response1.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data1 = await response1.json();
    props.setRol(data1.role);
    props.setUid(data1.uid);
    setErrorLoginMessage('');
    //Verificare daca pacientul este activ și pentru afișarea operației în HomePage
    if(data1.role === 'pacient'){
        const response2 = await fetch('http://localhost:8000/api/medical_office/patients/?uid=true', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
        });
            if(response.ok){
                const data2 = await response2.json();
                if(data2.is_active===false){
                    window.location.href = '/login';
                    return;
        }
        else{
           props.setCNP(data2.cnp); 
        }
            }
    }
    //Pentru afișarea operației în HomePage
    else if(data1.role === 'doctor'){
        const response2 = await fetch('http://localhost:8000/api/medical_office/physicians/?uid=true', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
        });
            if(response.ok){
                const data2 = await response2.json();
                props.setIdDoctor(data2.id_doctor);
            }
    }
    //window.location.href = '/';
  } catch (err) {
    console.error('Error:', err);
  }
};
  return (//render
  
    <div className="container mt-5">
  <h2>Pagina de autentificare</h2>
  {props.token ? (
    <div>
    <p className="text-success">Autentificare cu succes.</p>
    <Link to="/" className="btn btn-success" >Acasă</Link>
    </div>
  ) : (
    <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} className="mb-3">
      <div className="mb-3">
        <label htmlFor="username" className="form-label">
          Username:
          <input type="text" id="username" className="form-control" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
      </div>
      <div className="mb-3">
        <label htmlFor="password" className="form-label">
          Password:
          <input type="password" id="password" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
      </div>
      <button type="submit" className="btn btn-primary">Login</button>
    </form>
  )}
  {errorLoginMessage && <p className="text-danger">{errorLoginMessage}</p>}
</div>

  );
};
export default LoginPage;

