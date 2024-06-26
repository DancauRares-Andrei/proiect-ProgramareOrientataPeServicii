from app_uac import *
from modele import *
from grpc import _channel
import json
#DOCTORI

@app.get("/api/medical_office/physicians/")
async def get_doctors(response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),specialization:str=None,page:int=None,items_per_page:int=None,name:str=None,email:str=None,uid:bool=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="pacient":
            if specialization is not None:
                doctors=list(Doctor.select().where(Doctor.specializare==specialization))
            elif name is not None:
                doctors=list(Doctor.select().where(Doctor.nume.startswith(name) or Doctor.prenume.startswith(name)))
            elif page is not None and items_per_page is not None:
                page = max(1, page)  
                items_per_page = max(1, items_per_page)  
                page=min(100,page)     
                items_per_page=min(100,items_per_page)
                
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page

                doctors=list(Doctor.select().offset(start_idx).limit(items_per_page))
            elif uid==True:
                try:
                    doctor=Doctor.get(Doctor.id_user==token_response.sub)
                    doctor_hateoas = DoctorHATEOAS(
                    id_doctor=doctor.id_doctor,
                    id_user=doctor.id_user,
                    nume=doctor.nume,
                    prenume=doctor.prenume,
                    email=doctor.email,
                    telefon=doctor.telefon,
                    specializare=doctor.specializare,
                    links=LinkSet({
                        "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                        "parent":{"href":"/api/medical_office/physicians/"},
                        "create_doctor":{"href":"/api/medical_office/physicians/","type":"POST"},
                        "get_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"GET"},
                        "update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PUT"}
                        })
                        )
                    return doctor_hateoas
                except Doctor.DoesNotExist:
                    response.status_code=status.HTTP_404_NOT_FOUND
                    return {"parent":{"href":"/api/medical_office/physicians/"}}        
            else:
                doctors=list(Doctor.select())
        else:
            if email is not None:
                try:
                    pattern_email = re.compile(r'[,\/]')
                    if pattern_email.search(email):
                        raise HTTPException(status_code=422, detail="Adresa doctorului contine caractere invalide.")
                    doctor=Doctor.get(Doctor.email==email)
                    doctor_hateoas_pacient=DoctorHATEOASPacient(
                        id_doctor=doctor.id_doctor,
                        nume=doctor.nume,
                        prenume=doctor.prenume,
                        email=doctor.email,
                        specializare=doctor.specializare,
                        links=LinkSet({
                            "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                            "parent":{"href":"/api/medical_office/physicians/"}
                            })
                    )
                    return doctor_hateoas_pacient
                except Doctor.DoesNotExist:
                    response.status_code=status.HTTP_404_NOT_FOUND
                    return {"parent":{"href":"/api/medical_office/physicians/"}}
            else:
                doctors=list(Doctor.select())
                doctor_hateoas_list = []
                for doctor in doctors:
                    doctor_hateoas_pacient=DoctorHATEOASPacient(
                    id_doctor=doctor.id_doctor,
                    nume=doctor.nume,
                    prenume=doctor.prenume,
                    email=doctor.email,
                    specializare=doctor.specializare,
                    links=LinkSet({
                        "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                        "parent":{"href":"/api/medical_office/physicians/"}
                        })
                )
                    doctor_hateoas_list.append(doctor_hateoas_pacient)
                return doctor_hateoas_list          
        doctor_hateoas_list = []
        for doctor in doctors:
            doctor_hateoas = DoctorHATEOAS(
                id_doctor=doctor.id_doctor,
                id_user=doctor.id_user,
                nume=doctor.nume,
                prenume=doctor.prenume,
                email=doctor.email,
                telefon=doctor.telefon,
                specializare=doctor.specializare,
                links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/physicians/"},
                    "create_doctor":{"href":"/api/medical_office/physicians/","type":"POST"},
                    "get_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"GET"},
                    "update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PUT"}
                    })
            )
            doctor_hateoas_list.append(doctor_hateoas)                
        return doctor_hateoas_list
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")


@app.post("/api/medical_office/physicians/")
async def create_doctor(doctor: CreateDoctor,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="admin":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar adminul poate adauga noi medici.")
        pattern = re.compile(r'[.,\/]')
        pattern_email = re.compile(r'[,\/]')
        if pattern.search(doctor.nume) or pattern.search(doctor.prenume) or not doctor.telefon.isnumeric() or pattern_email.search(doctor.email) or len(doctor.telefon)!=10:
            raise HTTPException(status_code=422, detail="Datele doctorului sunt gresite.")
        url=f"http://localhost:8002/api/medical_office_user?uid=true"
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            raise HTTPException(status_code=422, detail="Nu exista utilizator cu acest uid.")
        if json.loads(response1.content.decode())['role']!='doctor':
            raise HTTPException(status_code=422, detail="Uid-ul introdus nu corespunde unui doctor.")
        new_doctor = Doctor.create(
            id_user=doctor.id_user,
            nume=doctor.nume,
            prenume=doctor.prenume,
            email=doctor.email,
            telefon=doctor.telefon,
            specializare=doctor.specializare
        )
        doctor_hateoas = DoctorHATEOAS(
                id_doctor=new_doctor.id_doctor,
                id_user=new_doctor.id_user,
                nume=new_doctor.nume,
                prenume=new_doctor.prenume,
                email=new_doctor.email,
                telefon=new_doctor.telefon,
                specializare=new_doctor.specializare,
                links=LinkSet({
                "self":{"href":"/api/medical_office/physicians/"+str(new_doctor.id_doctor)},
                "parent":{"href":"/api/medical_office/physicians/"},
                "create_doctor":{"href":"/api/medical_office/physicians/","type":"POST"},
                "get_doctor":{"href":"/api/medical_office/physicians/"+str(new_doctor.id_doctor),"type":"GET"},
                "update_doctor":{"href":"/api/medical_office/physicians/"+str(new_doctor.id_doctor),"type":"PUT"},
                "partial_update_doctor":{"href":"/api/medical_office/physicians/"+str(new_doctor.id_doctor),"type":"PATCH"}
                })
            )
        response.status_code=status.HTTP_201_CREATED
        return doctor_hateoas
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")    
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu poate fi creat doctorul pentru ca email-ul sau uid-ul este deja folosit.")
    except OperationalError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Nu poate fi creat doctorul pentru ca sunt greseli la una sau mai multe din urmatoarele date: telefon, email, specializare.")
    

@app.get("/api/medical_office/physicians/{id}")
async def get_doctor(id: int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),date:str=None,type:str=None,statusp:str=None,uid:int=None):
    try:
        if date is not None and type is not None:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            doctor = Doctor.get(Doctor.id_doctor == id)
            if token_response.role!="admin" and token_response.role!="doctor": 
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea programarile doctorului.")          
            if token_response.role!="admin" and str(doctor.id_user)!=token_response.sub:
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
            if type=='month':
                programari = Programare.select().where((Programare.id_doctor==id) & (Programare.data.month==date))
                programari_hateoas_list=[]
                for programare in programari:
                    programare_hateoas = ProgramareHATEOAS(
                    id_doctor=programare.id_doctor.id_doctor,
                    cnp_pacient=programare.cnp_pacient.cnp,
                    data=programare.data,
                    status=programare.status,
                    links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                    "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                    "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},
                    
                    "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                    })
                    )
                    programari_hateoas_list.append(programare_hateoas)
                return programari_hateoas_list
            elif type=='day':
                programari = Programare.select().where((Programare.id_doctor==id) & (Programare.data.day==date) & (Programare.data.month==datetime.now().month))
                programari_hateoas_list=[]
                for programare in programari:
                    programare_hateoas = ProgramareHATEOAS(
                    id_doctor=programare.id_doctor.id_doctor,
                    cnp_pacient=programare.cnp_pacient.cnp,
                    data=programare.data,
                    status=programare.status,
                    links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                    "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                    "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},
                    
                    "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                    })
                    )
                    programari_hateoas_list.append(programare_hateoas)
                return programari_hateoas_list
            else:
                raise HTTPException(status_code=422, detail="Parametrul type este gresit.")
        elif date is not None:
            try:
                grpc_token_request = TokenRequest(token=current_user)
                token_response = auth_service.ValidateToken(grpc_token_request)
                if not token_response.valid:
                    raise HTTPException(status_code=401, detail="Token-ul nu este valid")
                doctor = Doctor.get(Doctor.id_doctor == id)
                if token_response.role!="admin" and token_response.role!="doctor":
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request) 
                    raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea programarile doctorului.")          
                if token_response.role!="admin" and str(doctor.id_user)!=token_response.sub:
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
                programare = Programare.get((Programare.id_doctor==id) & (Programare.data==date))
                programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                    "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                    "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},
                    
                    "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                    })
            )
                return programare_hateoas
            except Programare.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/physicians/"+str(id)}}
        elif statusp is not None:
            programari = Programare.select().where((Programare.id_doctor==id) & (Programare.status==statusp))
            programari_hateoas_list=[]
            for programare in programari:
                programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},
                
                "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                })
                )
                programari_hateoas_list.append(programare_hateoas)
            return programari_hateoas_list 
        elif uid is not None:
            try:
                grpc_token_request = TokenRequest(token=current_user)
                token_response = auth_service.ValidateToken(grpc_token_request)
                if not token_response.valid:
                    raise HTTPException(status_code=401, detail="Token-ul nu este valid")
                if token_response.role!="doctor" or (token_response.role=="doctor" and token_response.sub!=str(uid)):
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request) 
                    raise HTTPException(status_code=403, detail="Doar doctorul in sine poate vedea informatiile personale.")              
                doctor = Doctor.get((Doctor.id_doctor == id)&(Doctor.id_user == uid))
                doctor_hateoas = DoctorHATEOAS(
                    id_doctor=doctor.id_doctor,
                    id_user=doctor.id_user,
                    nume=doctor.nume,
                    prenume=doctor.prenume,
                    email=doctor.email,
                    telefon=doctor.telefon,
                    specializare=doctor.specializare,
                    links=LinkSet({#Am eliminat POST pentru ca un doctor nu are dreptul sa faca POST.
                    "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/physicians/"},
                    "get_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"GET"},
                    "update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PUT"},
                    "partial_update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PATCH"}
                    })
                )
                return doctor_hateoas
            except Doctor.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/physicians/"}}
        else:
            doctor = Doctor.get(Doctor.id_doctor == id)
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.role!="admin" and token_response.role!="doctor":
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request) 
                raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea informatiile personale.")
            doctor = Doctor.get(Doctor.id_doctor == id)
            if token_response.role!="admin" and str(doctor.id_user)!=token_response.sub:
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
            doctor_hateoas = DoctorHATEOAS(
                    id_doctor=doctor.id_doctor,
                    id_user=doctor.id_user,
                    nume=doctor.nume,
                    prenume=doctor.prenume,
                    email=doctor.email,
                    telefon=doctor.telefon,
                    specializare=doctor.specializare,
                    links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/physicians/"},
                    "create_doctor":{"href":"/api/medical_office/physicians/","type":"POST"},
                    "get_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"GET"},
                    "update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PUT"},
                    "partial_update_doctor":{"href":"/api/medical_office/physicians/"+str(doctor.id_doctor),"type":"PATCH"}
                    })
                )

            return doctor_hateoas
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Doctor.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"}}
    

#In contextul problemei, nu are sens sa am delete la medici.

@app.put("/api/medical_office/physicians/{id}")
async def update_doctor(id: int, doctor: UpdateDoctor,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_doctor = Doctor.get(Doctor.id_doctor == id)
        if token_response.role!="doctor" or (token_response.role=="doctor" and token_response.sub!=str(existing_doctor.id_user)):
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar doctorul in sine isi poate modifica informatiile.")
        pattern = re.compile(r'[.,\/]')
        pattern_email = re.compile(r'[,\/]')
        if pattern.search(doctor.nume) or pattern.search(doctor.prenume) or not doctor.telefon.isnumeric() or pattern_email.search(doctor.email) or len(doctor.telefon)!=10:
            raise HTTPException(status_code=422, detail="Datele doctorului sunt gresite.")
        
        
        existing_doctor.nume = doctor.nume
        existing_doctor.prenume = doctor.prenume
        existing_doctor.email = doctor.email
        existing_doctor.telefon = doctor.telefon
        existing_doctor.specializare = doctor.specializare
        existing_doctor.save()
        
        response.status_code=status.HTTP_204_NO_CONTENT
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")    
    except Doctor.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"}}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu poate fi actualizat doctorul pentru ca email-ul este deja in uz de catre altcineva.")
    except OperationalError:
        raise HTTPException(status_code=422, detail="Nu poate fi actualizat doctorul pentru ca sunt greseli la una sau mai multe din urmatoarele date: telefon, email, specializare.")
    
          
@app.patch("/api/medical_office/physicians/{id}")
async def partial_update_doctor(id: int,response:Response, doctor: PatchDoctor,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_doctor = Doctor.get(Doctor.id_doctor == id)
        if token_response.role!="doctor" or (token_response.role=="doctor" and token_response.sub!=str(existing_doctor.id_user)):
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar doctorul in sine isi poate modifica informatiile.")
        pattern = re.compile(r'[.,\/]')
        pattern_email = re.compile(r'[,\/]')
        
        if doctor.nume is not None:
            if pattern.search(doctor.nume):
                raise HTTPException(status_code=422, detail="Numele doctorului contine caractere invalide.")
            existing_doctor.nume = doctor.nume
        if doctor.prenume is not None:
            if pattern.search(doctor.prenume):
                raise HTTPException(status_code=422, detail="Prenumele doctorului contine caractere invalide.")
            existing_doctor.prenume = doctor.prenume
        if doctor.email is not None:
            if pattern_email.search(doctor.email):
                raise HTTPException(status_code=422, detail="Email-ul doctorului contine caractere invalide.")
            existing_doctor.email = doctor.email
        if doctor.telefon is not None:
            if not doctor.telefon.isnumeric() or len(doctor.telefon)!=10:
                raise HTTPException(status_code=422, detail="Telefonul doctorului nu respecta formatul.")
            existing_doctor.telefon = doctor.telefon
        if doctor.specializare is not None:
            existing_doctor.specializare = doctor.specializare
        existing_doctor.save()
        response.status_code=status.HTTP_204_NO_CONTENT
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Doctor.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"}}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu poate fi actualizat doctorul pentru ca email-ul este deja folosit de altcineva.")
    except OperationalError:
        raise HTTPException(status_code=422, detail="Nu poate fi actualizat doctorul pentru ca sunt greseli la una sau mai multe din urmatoarele date: telefon, email, specializare.")
        
        
#PROGRAMARI DOCTORI 

@app.get("/api/medical_office/physicians/{id}/patients")
async def get_programari_doctor(id:int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),page:int=None,items_per_page:int=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        doctor = Doctor.get(Doctor.id_doctor == id)
        if token_response.role!="admin" and token_response.role!="doctor": 
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea programarile doctorului.")          
        if token_response.role!="admin" and str(doctor.id_user)!=token_response.sub:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
        if page is not None and items_per_page is not None:
            page = max(1, page) 
            items_per_page = max(1, items_per_page)  
            page=min(100,page)      
            items_per_page=min(100,items_per_page)

            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page


            programari=Programare.select().where(Programare.id_doctor==id).offset(start_idx).limit(items_per_page)
        else:
            programari=Programare.select().where(Programare.id_doctor==id)
        programari_hateoas_list = []
        for programare in programari:
            programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                    "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                    "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},                    
                    "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                    })
            )
            programari_hateoas_list.append(programare_hateoas)
        return programari_hateoas_list
    except Doctor.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
 
@app.get("/api/medical_office/physicians/{id}/patients/{cnp}")
async def get_programare_doctor(id:int,cnp:int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),data:date=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        doctor = Doctor.get(Doctor.id_doctor == id)
        if token_response.role!="admin" and token_response.role!="doctor": 
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea programarile doctorului.")          
        if token_response.role!="admin" and str(doctor.id_user)!=token_response.sub:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
        if data is not None:
            programare = Programare.get((Programare.id_doctor == id) & (Programare.cnp_pacient==cnp) & (Programare.data==data))
            programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                    "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(cnp)},
                    "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                    "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(cnp),"type":"GET"},
                    "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(cnp),"type":"PUT"}
                    })
            )
            url=f"http://localhost:8001/api/medical_office_consultation?id_doctor={programare.id_doctor.id_doctor}&cnp={cnp}&data={programare.data}"
            print(url)
            response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
            if response1.status_code == 200:
                consultatie=json.loads(response1.content.decode())
                programare_hateoas.links["get_consultatie"]={"href":f"http://localhost:8001/api/medical_office_consultation/{consultatie['id']}","type":"GET"}
                programare_hateoas.links["update_consultatie"]={"href":f"http://localhost:8001/api/medical_office_consultation/{consultatie['id']}","type":"PUT"}                            
            else:
                programare_hateoas.links["create_consultatie"]={"href":f"http://localhost:8001/api/medical_office_consultation","type":"POST"}
            return programare_hateoas
        else:
            programari=Programare.select().where((Programare.id_doctor == id) & (Programare.cnp_pacient==cnp))
            programari_hateoas_list = []
            for programare in programari:
                programare_hateoas = ProgramareHATEOAS(
                    id_doctor=programare.id_doctor.id_doctor,
                    cnp_pacient=programare.cnp_pacient.cnp,
                    data=programare.data,
                    status=programare.status,
                    links=LinkSet({
                        "self":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp)},
                        "parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients"},
                        "get_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"GET"},                        
                        "update_programare_doctor":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"+str(programare.cnp_pacient.cnp),"type":"PUT"}
                        })
                )
                programari_hateoas_list.append(programare_hateoas)
            return programari_hateoas_list  
    except Doctor.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"}}
    except Programare.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    
#Nu am delete la programari din partea doctorului
    
#Readaugarea metodei de actualizare pentru status
@app.put("/api/medical_office/physicians/{id}/patients/{cnp}")
async def update_programare_doctor(id:int,cnp:int,programare:CreateProgramare,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
   try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        doctor = Doctor.get(Doctor.id_doctor == id)
        if token_response.role!="doctor": 
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar adminul si doctorul in sine pot vedea programarile doctorului.")          
        if str(doctor.id_user)!=token_response.sub:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Accesare a unui alt doctor.")
        ex_programare = Programare.get((Programare.cnp_pacient==cnp) & (Programare.id_doctor == id) & (Programare.data==programare.data))
        ex_programare.data=programare.data #Data e folosita in identificare, deci nu va fi schimbată.
        ex_programare.status=programare.status
        ex_programare.save()
        response.status_code=status.HTTP_204_NO_CONTENT
   except OperationalError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Nu poate fi creata programarea pentru ca statusul nu este corect.")
   except Doctor.DoesNotExist:
        raise HTTPException(status_code=409, detail="Nu poate fi creata programarea pentru ca doctorul nu exista.")#RFC 7231 PUT cand nu corespunde reprezentarea
   except Programare.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"+str(id)}}
