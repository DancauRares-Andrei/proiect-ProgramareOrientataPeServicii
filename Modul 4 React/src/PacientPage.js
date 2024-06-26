import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
const PacientPage = (props) => {
  const [cnp, setCNP] = useState(''); 
  const [consultations, setConsultations] = useState(null);
  const [programari, setProgramari] = useState(null);
  const [doctors, setDoctors] = useState(null);
  const [nume, setNume] = useState('');
  const [prenume, setPrenume] = useState('');
  const [email, setEmail] = useState('');
  const [telefon, setTelefon] = useState('');
  const [dataNasterii, setDataNasterii] = useState('');
  const [isActive, setActive] = useState('');
  const [numeUpdate, setNumeUpdate] = useState('');
  const [prenumeUpdate, setPrenumeUpdate] = useState('');
  const [emailUpdate, setEmailUpdate] = useState('');
  const [telefonUpdate, setTelefonUpdate] = useState('');
  const [dataNasteriiUpdate, setDataNasteriiUpdate] = useState('');
  const [numePUpdate, setNumePUpdate] = useState('');
  const [prenumePUpdate, setPrenumePUpdate] = useState('');
  const [emailPUpdate, setEmailPUpdate] = useState('');
  const [telefonPUpdate, setTelefonPUpdate] = useState('');
  const [dataNasteriiPUpdate, setDataNasteriiPUpdate] = useState('');
  const [errorPUpdateMessage, setErrorPUpdateMessage] = useState('');
  const [errorUpdateMessage, setErrorUpdateMessage] = useState('');
  const [errorDeleteMessage, setErrorDeleteMessage] = useState('');
  const [errorAddPMessage, setErrorAddPMessage] = useState('');
  const [emailAddP, setEmailAddP] = useState('');
  const [dataPr, setDataPr] = useState('');
  const [statusP, setStatusP] = useState('');
  if(props.token === undefined){
    props.resetProps();
        window.location.href = '/login';
  }
  useEffect(() => {//componentDidMount 
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/medical_office/patients/?uid=true`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });
        if (!response.ok) {
          // Tratează cazul în care cererea nu este reușită
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403 || response.status===422){
            props.resetProps();window.location.href = '/login';
          }
          return;
        }
        const patientData = await response.json();
        if(patientData.is_active===false){
            props.resetProps();window.location.href = '/login';
            return;
        }
        setCNP(patientData.cnp);
        setNume(patientData.nume);
        setPrenume(patientData.prenume);
        setEmail(patientData.email);
        setTelefon(patientData.telefon);
        setDataNasterii(patientData.data_nasterii);
        setActive(patientData.is_active);
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    const fetchData1 = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/medical_office/physicians/`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });

        if (!response.ok) {
          // Tratează cazul în care cererea nu este reușită
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
          return;
        }

        const doctorsData = await response.json();
        setDoctors(doctorsData);
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    const fetchData2 = async () => {
      try {
        const response = await fetch(`http://localhost:8001/api/medical_office_consultation`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });

        if (!response.ok) {
          // Tratează cazul în care cererea nu este reușită
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
          return;
        }

        const consultationData = await response.json();
        setConsultations(consultationData);
      } catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    const fetchData3 = async () => {
      try {
      if(cnp){
        const response = await fetch(`http://localhost:8000/api/medical_office/patients/`+cnp+`/physicians`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${props.token}`,
          },
        });
        if (!response.ok) {
          console.error('Cererea nu a reușit:', response.statusText);
          if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
          return;
        }

        const programariData = await response.json();
        setProgramari(programariData);
      }} catch (error) {
        console.error('Eroare în timpul cererii:', error);
      }
    };
    fetchData();
    fetchData1();
    fetchData2();
    fetchData3();
  },[props,cnp]);
  const handleDeletePacient = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/medical_office/patients/' + cnp, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${props.token}`,
            }
          });
          if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
          if (response.ok) {
            setErrorDeleteMessage('');
            props.resetProps();window.location.href = '/login';
          } 
        } catch (error) {
          console.error('Error during create patient:', error);
          setErrorDeleteMessage('A apărut o eroare.');
        }
      };
  const handleUpdatePacient = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/patients/' + cnp, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body: JSON.stringify({
          nume: numeUpdate,
          prenume: prenumeUpdate,
          email: emailUpdate,
          data_nasterii: dataNasteriiUpdate,
          telefon:telefonUpdate,
          is_active:true
        }),
      });
       if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
       if(response.status===422){
           const resp=await response.json();
          setErrorUpdateMessage(resp.detail);
       }
      if (response.status===204) {
        setErrorUpdateMessage('');
        setNume(numeUpdate);
        setPrenume(prenumeUpdate);
        setEmail(emailUpdate);
        setTelefon(telefonUpdate);
        setDataNasterii(dataNasteriiUpdate);
      } 
    } catch (error) {
      console.error('Error during create patient:', error);
      setErrorUpdateMessage('A apărut o eroare.');
    }
  };
  const handlePUpdatePacient = async () => {
    try {
      const bodyData = {
      nume: numePUpdate,
      prenume: prenumePUpdate,
      email: emailPUpdate,
      data_nasterii: dataNasteriiPUpdate,
      telefon: telefonPUpdate
      };
      const filteredBodyData = Object.fromEntries(
      Object.entries(bodyData).filter(([key, value]) => value !== null && value !== undefined && value !== "")
      );
    const requestBody = JSON.stringify(filteredBodyData); 
      const response = await fetch('http://localhost:8000/api/medical_office/patients/' + cnp, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body: requestBody,
      });
       if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
      if (response.status===204) {
        setErrorPUpdateMessage('');
        setNume(numePUpdate!==''?numePUpdate:nume);
        setPrenume(prenumePUpdate!==''?prenumePUpdate:prenume);
        setEmail(emailPUpdate!==''?emailPUpdate:email);
        setTelefon(telefonPUpdate!==''?telefonPUpdate:telefon);
        setDataNasterii(dataNasteriiPUpdate!==''?dataNasteriiPUpdate:dataNasterii);
      }
      if(response.status===422){
           const resp=await response.json();
          setErrorPUpdateMessage(resp.detail);
       } 
    } catch (error) {
      console.error('Error during create patient:', error);
      setErrorPUpdateMessage('A apărut o eroare.');
    }
  };
  const handleAddProgramare = async () =>{
    try {
      const response = await fetch('http://localhost:8000/api/medical_office/physicians/?email='+emailAddP, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        }
      });
       if(response.status===401 || response.status===403){
            props.resetProps();window.location.href = '/login';
          }
      if (response.status===200) {
        const doctor=await response.json();
        const response1 = await fetch(`http://localhost:8000/api/medical_office/patients/`+cnp+`/physicians/`+doctor.id_doctor, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${props.token}`,
        },
        body: JSON.stringify({
          data:dataPr,
          status:statusP
        }),
      });
      if(response1.status===401 || response1.status===403){
            props.resetProps();window.location.href = '/login';
          }
      if(response1.status===422){
           const resp=await response1.json();
          setErrorAddPMessage(resp.detail);
       } 
      else if(response.status===201){
      var programariNoi = [...programari];
      programariNoi.push({'cnp_pacient':cnp,'id_doctor':doctor.id_doctor,'data':dataPr,'status':statusP});
      setProgramari(programariNoi);
      setErrorAddPMessage('');
      }
      }
      else if(response.status===404){
        setErrorAddPMessage('Nu am găsit doctor cu această adresă de email.');
      }
      else{
        setErrorAddPMessage('A aparut o eroare cu statusul:'+response.status);
      }
    } catch (error) {
      console.error('Error during create patient:', error);
    }
  };
  return (//render
    <div className="container mt-5">
    <h2>Pagina pacientului</h2>
    {cnp ? (
      <div>
        <div className="mb-4">
          <h4>Informații personale</h4>
          <p>CNP: {cnp}</p>
          <p>Nume: {nume}</p>
          <p>Prenume: {prenume}</p>
          <p>Email: {email}</p>
          <p>Telefon: {telefon}</p>
          <p>Data nașterii: {dataNasterii}</p>
          <p>Activat: {isActive.toString()}</p>
        </div>

        <div className="mb-4">
          <h4>Listă doctori</h4>
          {doctors ? (
            <ul>
              {doctors.map((doctor) => (
                <li key={doctor.email}>
                  <p>Nume: {doctor.nume}</p>
                  <p>Prenume: {doctor.prenume}</p>
                  <p>Email: {doctor.email}</p>
                  <p>Specializare: {doctor.specializare}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>Se încarcă...</p>
          )}
        </div>

        <div className="mb-4">
          <h4>Vizualizare istoric medical</h4>
          {consultations ? (
            <ul>
              {consultations.map((consultation) => (
                <li key={consultation.id}>
                  <p>ID: {consultation.id}</p>
                  <p>Data: {consultation.data}</p>
                  <p>Diagnostic: {consultation.diagnostic}</p>
                  <p>Investigații:</p>
                  <ul>
                    {consultation.investigatii.map((investigatie) => (
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
          <h4>Vizualizare listă programări</h4>
          {programari ? (
            <ul>
              {programari.map((programare) => (
                <li key={programare.cnp + " " + programare.data + " " + programare.id_doctor}>
                  <p>Data: {programare.data}</p>
                  <p>Status: {programare.status}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>Se încarcă...</p>
          )}
        </div>

        <div className="mb-4">
          <h4>Actualizare Pacient</h4>
          <form onSubmit={(e) => { e.preventDefault(); handleUpdatePacient(); }}>
            <div className="mb-3">
              <label htmlFor="numeUpdate" className="form-label">
                Nume:
                <input type="text" id="numeUpdate" className="form-control" value={numeUpdate} onChange={(e) => setNumeUpdate(e.target.value)} required />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="prenumeUpdate" className="form-label">
                Prenume:
                <input type="text" id="prenumeUpdate" className="form-control" value={prenumeUpdate} onChange={(e) => setPrenumeUpdate(e.target.value)} required />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="telefonUpdate" className="form-label">
                Telefon:
                <input type="tel" id="telefonUpdate" className="form-control" value={telefonUpdate} onChange={(e) => setTelefonUpdate(e.target.value)} required />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="emailUpdate" className="form-label">
                Email:
                <input type="email" id="emailUpdate" className="form-control" value={emailUpdate} onChange={(e) => setEmailUpdate(e.target.value)} required />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="dataNasteriiUpdate" className="form-label">
                Data nașterii:
                <input type="date" id="dataNasteriiUpdate" className="form-control" value={dataNasteriiUpdate} onChange={(e) => setDataNasteriiUpdate(e.target.value)} required />
              </label>
            </div>
            <button type="submit" className="btn btn-primary">Actualizare Pacient</button>
          </form>
          {errorUpdateMessage && <p className="text-danger">{errorUpdateMessage}</p>}
        </div>

        <div className="mb-4">
          <h4>Actualizare parțială pacient</h4>
          <form onSubmit={(e) => { e.preventDefault(); handlePUpdatePacient(); }}>
            <div className="mb-3">
              <label htmlFor="numePUpdate" className="form-label">
                Nume:
                <input type="text" id="numePUpdate" className="form-control" value={numePUpdate} onChange={(e) => setNumePUpdate(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="prenumePUpdate" className="form-label">
                Prenume:
                <input type="text" id="prenumePUpdate" className="form-control" value={prenumePUpdate} onChange={(e) => setPrenumePUpdate(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="telefonPUpdate" className="form-label">
                Telefon:
                <input type="tel" id="telefonPUpdate" className="form-control" value={telefonPUpdate} onChange={(e) => setTelefonPUpdate(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="emailPUpdate" className="form-label">
                Email:
                <input type="email" id="emailPUpdate" className="form-control" value={emailPUpdate} onChange={(e) => setEmailPUpdate(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="dataNasteriiPUpdate" className="form-label">
                Data nașterii:
                <input type="date" id="dataNasteriiPUpdate" className="form-control" value={dataNasteriiPUpdate} onChange={(e) => setDataNasteriiPUpdate(e.target.value)} />
              </label>
            </div>
            <button type="submit" className="btn btn-primary">Actualizare Pacient</button>
          </form>
          {errorPUpdateMessage && <p className="text-danger">{errorPUpdateMessage}</p>}
        </div>

        <div className="mb-4">
          <h4>Efectuare programare</h4>
          <form onSubmit={(e) => { e.preventDefault(); handleAddProgramare(); }}>
            <div className="mb-3">
              <label htmlFor="emailAddP" className="form-label">
                Email doctor:
                <input type="email" id="emailAddP" className="form-control" value={emailAddP} onChange={(e) => setEmailAddP(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="statusP" className="form-label">
                Status:
                <input type="text" id="statusP" className="form-control" value={statusP} onChange={(e) => setStatusP(e.target.value)} />
              </label>
            </div>
            <div className="mb-3">
              <label htmlFor="dataPr" className="form-label">
                Data programării:
                <input type="date" id="dataPr" className="form-control" value={dataPr} onChange={(e) => setDataPr(e.target.value)} />
              </label>
            </div>
            <button type="submit" className="btn btn-primary">Adăugare Programare</button>
          </form>
          {errorAddPMessage && <p className="text-danger">{errorAddPMessage}</p>}
        </div>

        <div className="mb-4">
          <h4>Dezactivare cont</h4>
          <form onSubmit={(e) => { e.preventDefault(); handleDeletePacient(); }}>
            <button type="submit" className="btn btn-danger">Dezactivare cont</button>
          </form>
          {errorDeleteMessage && <p className="text-danger">{errorDeleteMessage}</p>}
        </div>
      </div>
    ) : (
      <p>Se încarcă...</p>
    )}

    <div>
      <h4>Deconectare</h4>
      <Link to="/logout" className="btn btn-secondary">Deconectare</Link>
      <br />
      <br />
    </div>
    <div>
      <h4>Navigare Acasă</h4>
      <Link to="/" className="btn btn-secondary">Acasă</Link>
      <br />
      <br />
    </div>
  </div>
  );
};

export default PacientPage;

