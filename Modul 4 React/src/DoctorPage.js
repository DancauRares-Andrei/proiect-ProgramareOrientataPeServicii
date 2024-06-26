import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
const DoctorPage = (props) => {
const [idDoctor, setIDDoctor] = useState(''); 
const [nume, setNume] = useState('');
const [prenume, setPrenume] = useState('');
const [email, setEmail] = useState('');
const [telefon, setTelefon] = useState('');
const [specializare, setSpecializare] = useState('');
const [patients, setPatients] = useState(null);
const [emailPacient, setEmailPacient] = useState('');
const [emailPacientConsultatie, setEmailPacientConsultatie] = useState('');
const [dataConsultatie, setDataConsultatie] = useState('');
const [programari, setProgramari] = useState(null);
const [consultatie, setConsultatie] = useState(null);
const [consultatii, setConsultatii] = useState(null);
const [diagnosticCreare, setDiagnosticCreare] = useState('');
const [dataCreare, setDataCreare] = useState('');
const [emailPacientCreareConsultatie, setEmailPacientCreareConsultatie] = useState('');
const [investigatiiCreare, setInvestigatiiCreare] = useState([{ denumire: '', durata_de_procesare: 0, rezultat: '' }]);
const [diagnosticUpdate, setDiagnosticUpdate] = useState('');
const [dataUpdate, setDataUpdate] = useState('');
const [emailPacientUpdateConsultatie, setEmailPacientUpdateConsultatie] = useState('');
const [investigatiiUpdate, setInvestigatiiUpdate] = useState([{ denumire: '', durata_de_procesare: 0, rezultat: '' }]);
const [errorVizProg, setErrorVizProgMessage] = useState('');
const [errorVizConsMessage, setErrorVizConsMessage] = useState('');
const [errorCrConsMessage, setErrorCrConsMessage] = useState('');
const [errorUpConsMessage, setErrorUpConsMessage] = useState('');
if(props.token === undefined){
    props.resetProps();
        window.location.href = '/login';
  }
useEffect(() => {//componentDidMount 
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/medical_office/physicians/?uid=true`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });

        if (!response.ok) {
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403 || response.status===422){
            props.resetProps();
            window.location.href = '/login';
          }
          return;
        }

        const doctorData = await response.json();
        setIDDoctor(doctorData.id_doctor);
        setNume(doctorData.nume);
        setPrenume(doctorData.prenume);
        setEmail(doctorData.email);
        setTelefon(doctorData.telefon);
        setSpecializare(doctorData.specializare);
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    const fetchData1 = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/medical_office/patients/`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });

        if (!response.ok) {
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
          return;
        }

        const patientsData = await response.json();
        setPatients(patientsData);
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    const fetchData2 = async () => {
      try {
        if(idDoctor!=""){
        const response = await fetch(`http://localhost:8001/api/medical_office_consultation?id_doctor=`+idDoctor, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });

        if (!response.ok) {
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
          return;
        }

        const consultatiiData = await response.json();
        setConsultatii(consultatiiData);
        }
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    fetchData();
    fetchData1();
    fetchData2();
  }, [props,idDoctor]);
  const handleViewProgramari = async () =>{
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/?email='+emailPacient, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        }
      });
      if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(!response.ok){
        const resp=await response.json();
        setErrorVizProgMessage(resp.detail);
      }
      if (response.status===200) {
        const pacient=await response.json();
        const response1 = await fetch(`http://localhost:8000/api/medical_office/physicians/`+idDoctor+`/patients/`+pacient.cnp, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
      });
      if(response1.status===401 || response1.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(!response1.ok){
        const resp=await response1.json();
        setErrorVizProgMessage(resp.detail);
      }
      else{
      const programariData = await response1.json();
        setProgramari(programariData);
        }
      }
    } catch (error) {
      console.error('Error during create patient:', error);
    }
  };
  const handleViewConsultatie = async () =>{
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/?email='+emailPacientConsultatie, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        }
      });
      if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(response.status!==200){
        const resp=await response.json();
        setErrorVizConsMessage(resp.detail);
      }
      else {
        setErrorVizConsMessage('');
        const pacient=await response.json();
        const response1 = await fetch(`http://localhost:8001/api/medical_office_consultation?cnp=`+pacient.cnp+`&id_doctor=`+idDoctor+`&data=`+dataConsultatie, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
      });
      if(response1.status===401 || response1.status===403){
            props.resetProps();
            window.location.href = '/login';
            return;
          }
      if(response1.status===200){
      setErrorVizConsMessage('');
      const consultatieData = await response1.json();
        setConsultatie(consultatieData);
      }
      else{
        setConsultatie('');
        setErrorVizConsMessage("Nu s-a putut găsi consultație pentru acest pacient la această dată.");
      }
      }
    } catch (error) {
      console.error('Error during create patient:', error);
    }
  };
  const handleAddInvestigatie = () => {
    setInvestigatiiCreare([...investigatiiCreare, { denumire: '', durata_de_procesare: 0, rezultat: '' }]);
  };

  const handleInvestigatieChange = (index, field, value) => {
    const updatedInvestigatii = [...investigatiiCreare];
    updatedInvestigatii[index][field] = value;
    setInvestigatiiCreare(updatedInvestigatii);
  };
  const handleCreateConsultatie = async () =>{
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/?email='+emailPacientCreareConsultatie, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        }
      });
      if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(!response.ok){
        const resp=await response.json();
       setErrorCrConsMessage(resp.detail);
      }
      if (response.status===200) {
        const pacient=await response.json();
        const response1 = await fetch(`http://localhost:8001/api/medical_office_consultation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body:JSON.stringify({
            id_pacient:pacient.cnp,
            id_doctor:idDoctor,
            data:dataCreare,
            diagnostic:diagnosticCreare,
            investigatii:investigatiiCreare
        }),
      });
      if(response1.status===401 || response1.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(!response1.ok){
        const resp=await response1.json();
        setErrorCrConsMessage(resp.detail);
      }
      else{
        setErrorCrConsMessage('');
      }
    }} catch (error) {
      console.error('Error during create patient:', error);
    }
  };
  const handleAddUpdateInvestigatie = () => {
    setInvestigatiiUpdate([...investigatiiUpdate, { denumire: '', durata_de_procesare: 0, rezultat: '' }]);
  };

  const handleInvestigatieUpdateChange = (index, field, value) => {
    const updatedInvestigatii = [...investigatiiUpdate];
    updatedInvestigatii[index][field] = value;
    setInvestigatiiUpdate(updatedInvestigatii);
  };
  const handleUpdateConsultatie = async () =>{
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/?email='+emailPacientUpdateConsultatie, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        }
      });
      if(response.status===401 || response.status===403){
            props.resetProps();
            window.location.href = '/login';
            return;
          }
      else if(!response.ok){
       setErrorUpConsMessage("Nu am găsit pacient cu acest email.");
       return;
      }
      if (response.status===200) {
        const pacient=await response.json();
        const response1 = await fetch(`http://localhost:8001/api/medical_office_consultation?cnp=`+pacient.cnp+`&id_doctor=`+idDoctor+`&data=`+dataUpdate, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
      });
      if(response1.status===401 || response1.status===403){
            props.resetProps();
            window.location.href = '/login';
            return;
          }
      if(!response1.ok){
       setErrorUpConsMessage("Nu am găsit consultație cu aceste date.");
       return;
      }
      else{
      const consultatieData = await response1.json();
        const response2 = await fetch(`http://localhost:8001/api/medical_office_consultation/`+consultatieData.id, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body:JSON.stringify({
            id_pacient:pacient.cnp,
            id_doctor:idDoctor,
            data:dataUpdate,
            diagnostic:diagnosticUpdate,
            investigatii:investigatiiUpdate
        }),
      });
      if(response2.status===401 || response2.status===403){
            props.resetProps();
            window.location.href = '/login';
          }
      else if(!response2.ok){
        const resp=await response2.json();
        setErrorUpConsMessage(resp.detail);
       return;
      }
      else{
        setErrorUpConsMessage('');
      }
      }
    
    }} catch (error) {
      console.error('Error during create patient:', error);
    }
  };
return (
    <div className="container mt-5">
      <h2>Pagina doctorului</h2>
      {idDoctor ? (
        <div>
          <div className="mb-3">
            <p>Id: {idDoctor}</p>
            <p>Nume: {nume}</p>
            <p>Prenume: {prenume}</p>
            <p>Email: {email}</p>
            <p>Telefon: {telefon}</p>
            <p>Specializare: {specializare}</p>
          </div>

          <div className="mb-4">
            <h4>Lista Pacienților activi</h4>
            {patients ? (
              <ul>
                {patients.map((patient) => (
                  <li key={patient.email}>
                    <p>Nume: {patient.nume}</p>
                    <p>Prenume: {patient.prenume}</p>
                    <p>Email: {patient.email}</p>
                    <p>Telefon: {patient.telefon}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Se încarcă...</p>
            )}
          </div>
          <div className="mb-4">
            <h4>Lista Consultațiilor mele</h4>
            {consultatii ? (
              <ul>
                {consultatii.map((consultatie) => (
                  <li key={consultatie.id}>
                    <p>Id: {consultatie.id}</p>
                <p>Diagnostic: {consultatie.diagnostic}</p>
                <p>Investigații:</p>
                <ul>
                  {consultatie.investigatii.map((investigatie) => (
                    <li key={investigatie.id}>
                      <p>Denumire: {investigatie.denumire}</p>
                      <p>Durată de procesare: {investigatie.durata_de_procesare}</p>
                      <p>Rezultat: {investigatie.rezultat}</p>
                    </li>
                  ))}
                </ul>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Se încarcă...</p>
            )}
          </div>
          <div className="mb-4">
            <h4>Vizualizare programări pentru un pacient</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleViewProgramari(); }}>
              <div className="mb-3">
                <label htmlFor="emailPacient" className="form-label">
                  Email pacient:
                  <input type="email" id="emailPacient" className="form-control" value={emailPacient} onChange={(e) => setEmailPacient(e.target.value)} />
                </label>
              </div>
              <button type="submit" className="btn btn-primary">Vizualizare Programări</button>
            </form>
            {programari ? (
              <ul>
                {programari.map((programare) => (
                  <li key={`${programare.cnp} ${programare.data} ${programare.id_doctor}`}>
                    <p>Data: {programare.data}</p>
                    <p>Status: {programare.status}</p>
                  </li>
                ))}
              </ul>
            ) : null}
            {errorVizProg && <p className="text-danger">{errorVizProg}</p>}
          </div>

          <div className="mb-4">
            <h4>Vizualizare consultație pentru o programare</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleViewConsultatie(); }}>
              <div className="mb-3">
                <label htmlFor="emailPacientConsultatie" className="form-label">
                  Email pacient:
                  <input type="email" id="emailPacientConsultatie" className="form-control" value={emailPacientConsultatie} onChange={(e) => setEmailPacientConsultatie(e.target.value)} />
                </label>
              </div>
              <div className="mb-3">
                <label htmlFor="dataConsultatie" className="form-label">
                  Data programării:
                  <input type="date" id="dataConsultatie" className="form-control" value={dataConsultatie} onChange={(e) => setDataConsultatie(e.target.value)} />
                </label>
              </div>
              <button type="submit" className="btn btn-primary">Vizualizare Consultatie</button>
            </form>
            {consultatie ? (
              <div>
                <p>Id: {consultatie.id}</p>
                <p>Diagnostic: {consultatie.diagnostic}</p>
                <p>Investigații:</p>
                <ul>
                  {consultatie.investigatii.map((investigatie) => (
                    <li key={investigatie.id}>
                      <p>Denumire: {investigatie.denumire}</p>
                      <p>Durată de procesare: {investigatie.durata_de_procesare}</p>
                      <p>Rezultat: {investigatie.rezultat}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          {errorVizConsMessage && <p className="text-danger">{errorVizConsMessage}</p>}
          </div>

          <div className="mb-4">
  <h4>Creare consultație pentru o programare</h4>
  <form onSubmit={(e) => { e.preventDefault(); handleCreateConsultatie(); }}>
    <div className="mb-3">
      <label htmlFor="emailPacientCreareConsultatie" className="form-label">
        Email pacient:
        <input type="email" id="emailPacientCreareConsultatie" className="form-control" value={emailPacientCreareConsultatie} onChange={(e) => setEmailPacientCreareConsultatie(e.target.value)} />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="dataCreare" className="form-label">
        Data programării:
        <input type="date" id="dataCreare" className="form-control" value={dataCreare} onChange={(e) => setDataCreare(e.target.value)} />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="diagnosticCreare" className="form-label">
        Diagnostic:
        <input type="text" id="diagnosticCreare" className="form-control" value={diagnosticCreare} onChange={(e) => setDiagnosticCreare(e.target.value)} />
      </label>
    </div>
    {investigatiiCreare.map((investigatie, index) => (
      <div key={index} className="mb-3">
        <label>
          Nume investigație:
          <input
            type="text"
            className="form-control"
            value={investigatie.denumire}
            onChange={(e) => handleInvestigatieChange(index, 'denumire', e.target.value)}
          />
        </label>
        <label>
          Durată de procesare:
          <input
            type="number"
            className="form-control"
            value={investigatie.durata}
            onChange={(e) => handleInvestigatieChange(index, 'durata_de_procesare', e.target.value)}
          />
        </label>
        <label>
          Rezultat investigație:
          <input
            type="text"
            className="form-control"
            value={investigatie.rezultat}
            onChange={(e) => handleInvestigatieChange(index, 'rezultat', e.target.value)}
          />
        </label>
      </div>
    ))}
    <button type="button" className="btn btn-secondary" onClick={handleAddInvestigatie}>Adaugă investigație</button>
    <br />
    <br />
    <button type="submit" className="btn btn-primary">Creare Consultație</button>
  </form>
  {errorCrConsMessage && <p className="text-danger">{errorCrConsMessage}</p>}
</div>
          <div className="mb-4">
  <h4>Actualizare consultație pentru o programare</h4>
  <form onSubmit={(e) => { e.preventDefault(); handleUpdateConsultatie(); }}>
    <div className="mb-3">
      <label htmlFor="emailPacientUpdateConsultatie" className="form-label">
        Email pacient:
        <input type="email" id="emailPacientUpdateConsultatie" className="form-control" value={emailPacientUpdateConsultatie} onChange={(e) => setEmailPacientUpdateConsultatie(e.target.value)} />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="dataUpdate" className="form-label">
        Data programării:
        <input type="date" id="dataUpdate" className="form-control" value={dataUpdate} onChange={(e) => setDataUpdate(e.target.value)} />
      </label>
    </div>
    <div className="mb-3">
      <label htmlFor="diagnosticUpdate" className="form-label">
        Diagnostic:
        <input type="text" id="diagnosticUpdate" className="form-control" value={diagnosticUpdate} onChange={(e) => setDiagnosticUpdate(e.target.value)} />
      </label>
    </div>
    {investigatiiUpdate.map((investigatie, index) => (
      <div key={index} className="mb-3">
        <label>
          Nume investigație:
          <input
            type="text"
            className="form-control"
            value={investigatie.denumire}
            onChange={(e) => handleInvestigatieUpdateChange(index, 'denumire', e.target.value)}
          />
        </label>
        <label>
          Durată de procesare:
          <input
            type="number"
            className="form-control"
            value={investigatie.durata}
            onChange={(e) => handleInvestigatieUpdateChange(index, 'durata_de_procesare', e.target.value)}
          />
        </label>
        <label>
          Rezultat investigație:
          <input
            type="text"
            className="form-control"
            value={investigatie.rezultat}
            onChange={(e) => handleInvestigatieUpdateChange(index, 'rezultat', e.target.value)}
          />
        </label>
      </div>
    ))}
    <button type="button" className="btn btn-secondary" onClick={handleAddUpdateInvestigatie}>Adaugă investigație</button>
    <br />
    <br />
    <button type="submit" className="btn btn-primary">Actualizare Consultatie</button>
  </form>
  {errorUpConsMessage && <p className="text-danger">{errorUpConsMessage}</p>}
</div>
          <div>
            <h2>Deconectare</h2>
            <Link to="/logout" className="btn btn-danger">Deconectare</Link>
          </div>
        </div>
      ) : (
        <p>Se încarcă...</p>
      )}
      <br />
      <br />
    </div>
        );
};
export default DoctorPage;
