// CreatePacientPage.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
const CreatePacientPage = (props) => {
  const [cnp, setCnp] = useState('');
  const [nume, setNume] = useState('');
  const [prenume, setPrenume] = useState('');
  const [email, setEmail] = useState('');
  const [telefon, setTelefon] = useState('');
  const [dataNasterii, setDataNasterii] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  if(props.cnp !== undefined || props.token === undefined || props.idDoctor !== ''){
        props.resetProps();
        window.location.href = '/';
  }
  const handleCreatePacient = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/' + cnp, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body: JSON.stringify({
          nume: nume,
          prenume: prenume,
          email: email,
          data_nasterii: dataNasterii,
          telefon:telefon,
          is_active:true
        }),
      });

      if (response.status===201) {
        setSuccessMessage('Pacientul a fost creat cu succes!');
        props.setCNP(cnp);
        setErrorMessage('');
      } else if (response.status!==403){
        const data = await response.json();
        setErrorMessage(`Eroare: ${data.detail}`);
        setSuccessMessage('');
      }
      else{
        props.resetProps();
        window.location.href = '/';
      }
    } catch (error) {
      console.error('Error during create patient:', error);
      setErrorMessage('A apărut o eroare.');
      setSuccessMessage('');
    }
  };

  return (//render
    <div className="container mt-5">
  <h2>Create Pacient Page</h2>
  <form onSubmit={(e) => { e.preventDefault(); handleCreatePacient(); }} className="mb-3">
    <div className="mb-3">
      <label htmlFor="cnp" className="form-label">
        CNP:
        <input type="number" id="cnp" className="form-control" value={cnp} onChange={(e) => setCnp(e.target.value)} required />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="nume" className="form-label">
        Nume:
        <input type="text" id="nume" className="form-control" value={nume} onChange={(e) => setNume(e.target.value)} required />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="prenume" className="form-label">
        Prenume:
        <input type="text" id="prenume" className="form-control" value={prenume} onChange={(e) => setPrenume(e.target.value)} required />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="telefon" className="form-label">
        Telefon:
        <input type="tel" id="telefon" className="form-control" value={telefon} onChange={(e) => setTelefon(e.target.value)} required />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="email" className="form-label">
        Email:
        <input type="email" id="email" className="form-control" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="dataNasterii" className="form-label">
        Data Nasterii:
        <input type="date" id="dataNasterii" className="form-control" value={dataNasterii} onChange={(e) => setDataNasterii(e.target.value)} required />
      </label>
    </div>
    <button type="submit" className="btn btn-primary">Create Pacient</button>
  </form>
  {errorMessage && <p className="text-danger">{errorMessage}</p>}
  {successMessage && (
    <>
      <p>{successMessage}</p>
      <Link to="/pacient" className="btn btn-success">Vizualizare detalii pacient</Link>
    </>
  )}
</div>
  );
};

export default CreatePacientPage;

