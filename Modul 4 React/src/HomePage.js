// HomePage.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const HomePage = (props) => {
  const [usernameNew, setUsernameNew] = useState('');
  const [password, setPassword] = useState('');
  const [errorNewUserMessage, setErrorNewUserMessage] = useState('');
  const [errorUpdateUserMessage, setErrorUpdateUserMessage] = useState('');
  const handleCreateUser = async () => {
  if (!usernameNew|| !password) {
      console.error('Username și parolă sunt obligatorii');
      return;
    }
   try {
    const response = await fetch('http://localhost:8002/api/medical_office_user', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body:  JSON.stringify({
        username: usernameNew,
        password: password
      }),
    });
    if (!response.ok) {
        const resp=await response.json();
        setErrorNewUserMessage(resp.detail);
    }
    else if(response.status===201){
        setErrorNewUserMessage('');
        window.location.href = '/login';
    }
   } catch (err) {
    console.error('Error:', err);
  }
  };
  const handleUpdateUser = async () => {
  if (!usernameNew|| !password) {
      console.error('Username și parolă sunt obligatorii');
      return;
    }
   try {
    const response = await fetch('http://localhost:8002/api/medical_office_user/'+props.uid, {
      method: 'PUT',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${props.token}`,
      },
      body:  JSON.stringify({
        username: usernameNew,
        password: password
      }),
    });
    if (!response.ok) {
      const resp=await response.json();
      setErrorUpdateUserMessage(resp.detail);
    }
    else if(response.status===204){
        props.setUsername(usernameNew);
        setErrorUpdateUserMessage('');
    }
   } catch (err) {
    console.error('Error:', err);
  }
  };
  return (//render
   <div className="container mt-5">
    <h2>Acasă</h2>
    {props.token ? (
      <div>
        <p className="lead">Bine ai venit, {props.username}!</p>
        <div className="mb-4">
          <h4>Actualizare credențiale</h4>
          <form onSubmit={(e) => { e.preventDefault(); handleUpdateUser(); }}>
            <div className="mb-3">
              <label htmlFor="usernameNew" className="form-label">
                Username:
                <input type="text" id="usernameNew" className="form-control" value={usernameNew} onChange={(e) => setUsernameNew(e.target.value)} required />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="password" className="form-label">
                Password:
                <input type="password" id="password" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </label>
            </div>
            <button type="submit" className="btn btn-primary">Actualizează</button>
          </form>
        </div>
        {props.rol === 'pacient' ? (
          props.cnp === undefined ? (
            <Link to="/crearepacient" className="btn btn-warning">Completează detaliile pacientului</Link>
          ) : (
            <Link to="/pacient" className="btn btn-success">Vizualizare detalii pacient</Link>
          )
        ) : (
          props.rol === 'doctor' ? (
            <div>
              {props.idDoctor !== undefined ? (
                <Link to="/doctor" className="btn btn-success">Vizualizare detalii doctor</Link>
              ) : (
                <p class="alert alert-danger" role="alert">Adresează-te administratorului pentru a-ți completa datele personale.</p>
              )}
            </div>
          ) : null
        )}
        {errorUpdateUserMessage && <p className="text-danger">{errorUpdateUserMessage}</p>}
      </div>
    ) : (
      <div>
        <p>Te rugăm să te autentifici.</p>
        <Link to="/login" className="btn btn-primary">Login</Link><br /><br />
        <p>Nu ai cont? Creează unul mai jos.</p>
        <form onSubmit={(e) => { e.preventDefault(); handleCreateUser(); }}>
          <div className="mb-3">
            <label htmlFor="usernameNew" className="form-label">
              Username:
              <input type="text" id="usernameNew" className="form-control" value={usernameNew} onChange={(e) => setUsernameNew(e.target.value)} required />
            </label>
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Password:
              <input type="password" id="password" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </label>
          </div>
          <button type="submit" className="btn btn-primary">Creare cont</button>
        </form>
        {errorNewUserMessage && <p className="text-danger">{errorNewUserMessage}</p>}
      </div>
    )}
  </div>
  );
};

export default HomePage;

