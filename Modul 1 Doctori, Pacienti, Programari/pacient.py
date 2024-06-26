from app_uac import *
from modele import *
from grpc import _channel
import json
#PACIENTI
#In urma unei recomandari, am adaugat cautare partiala dupa nume si pentru pacienti
@app.get("/api/medical_office/patients/")
async def get_patients(response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),page:int=None,items_per_page:int=None,name:str=None,uid:bool=None,email:str=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if uid==True:
            try:
                #if token_response.sub!=str(uid) or token_response.role!="pacient":
                #    grpc_token_request = TokenRequest(token=current_user)
                #    auth_response= auth_service.DestroyToken(grpc_token_request)
                #    raise HTTPException(status_code=403, detail="Doar pacientul in sine se poate cauta dupa uid.")
                patient = Pacient.get(Pacient.id_user == token_response.sub)
                patient_hateoas = PacientHATEOAS(
                        cnp=str(patient.cnp),
                        id_user=patient.id_user,
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        data_nasterii=patient.data_nasterii,
                        is_active=patient.is_active,
                        links=LinkSet({
                        "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                        "parent":{"href":"/api/medical_office/patients/"},
                        "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"},
                        "delete_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"DELETE"},
                        "create_update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PUT"},
                        "update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PATCH"}
                        })
                    )
                return patient_hateoas
            except Pacient.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"}}
        else:
            if token_response.role!="admin" and token_response.role!="doctor":
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul poate vedea lista de pacienti. Doctorul ii vede doar pe cei activi")
            if name is not None:
                print(name)
                if token_response.role=="doctor":
                    patients=Pacient.select().where((Pacient.is_active==True) & (Pacient.nume.startswith(name) | Pacient.prenume.startswith(name)))
                    print(patients)
                elif token_response.role=="admin":
                    patients=Pacient.select().where(Pacient.nume.startswith(name) | Pacient.prenume.startswith(name))
                    print(patients)
            elif page is not None and items_per_page is not None:
                #Protectie DOS afisare paginata
                page = max(1, page)  
                items_per_page = max(1, items_per_page) 
                page=min(100,page)     
                items_per_page=min(100,items_per_page)
                
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                if token_response.role=="doctor":
                    patients=Pacient.select().where(Pacient.is_active==True).offset(start_idx).limit(items_per_page)
                elif token_response.role=="admin":
                    patients=Pacient.select().offset(start_idx).limit(items_per_page)
            elif email is not None and token_response.role=="doctor":
                try:
                    pattern_email = re.compile(r'[,\/]')
                    if pattern_email.search(email):
                        raise HTTPException(status_code=422, detail="Email invalid.")
                    patient=Pacient.get(Pacient.email==email)
                    patient_hateoas = PacientHATEOASDoctor(
                        cnp=str(patient.cnp),
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        links=LinkSet({
                            "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                            "parent":{"href":"/api/medical_office/patients/"},
                            "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"}
                            })
                    )
                    return patient_hateoas
                except Pacient.DoesNotExist:
                    response.status_code=status.HTTP_404_NOT_FOUND
                    return {"parent":{"href":"/api/medical_office/patients/"}}    
            elif token_response.role=="admin":
                print('aa')
                patients=Pacient.select()
            elif token_response.role=="doctor":
                patients=Pacient.select().where(Pacient.is_active==True)
            patient_hateoas_list = []
            for patient in patients:
                if token_response.role=="admin":
                    patient_hateoas = PacientHATEOAS(
                        cnp=str(patient.cnp),
                        id_user=patient.id_user,
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        data_nasterii=patient.data_nasterii,
                        is_active=patient.is_active,
                        links=LinkSet({
                            "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                            "parent":{"href":"/api/medical_office/patients/"},
                            "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"},
                            "delete_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"DELETE"},
                            "create_update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PUT"},
                            "update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PATCH"}
                            })
                    )
                else:
                    patient_hateoas = PacientHATEOASDoctor(
                        cnp=str(patient.cnp),
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        links=LinkSet({
                            "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                            "parent":{"href":"/api/medical_office/patients/"},
                            "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"}
                            })
                    )
                patient_hateoas_list.append(patient_hateoas)
        return patient_hateoas_list
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")

@app.get("/api/medical_office/patients/{cnp}")
async def get_patient(cnp: int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),date:str=None,type:str=None,statusp:str=None,uid:int=None):
    try:
        if date is not None and type is not None:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.role!="admin" and token_response.role!="pacient": 
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul si pacientul in sine pot vedea programarile pacientului.")
            patient = Pacient.get(Pacient.cnp == cnp)
            if token_response.role!="admin" and str(patient.id_user)!=token_response.sub:
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Accesare a unui alt pacient.")
            if type=='month':
                programari = Programare.select().where((Programare.cnp_pacient==cnp) & (Programare.data.month==date))
                programari_hateoas_list=[]
                for programare in programari:
                    programare_hateoas = ProgramareHATEOAS(
                    id_doctor=programare.id_doctor.id_doctor,
                    cnp_pacient=programare.cnp_pacient.cnp,
                    data=programare.data,
                    status=programare.status,
                    links=LinkSet({
                    "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                    "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                    "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                    "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
                    })
                    )
                    programari_hateoas_list.append(programare_hateoas)
                return programari_hateoas_list
            elif type=='day':
                programari = Programare.select().where((Programare.cnp_pacient==cnp) & (Programare.data.day==date) & (Programare.data.month==datetime.now().month))
                programari_hateoas_list=[]
                for programare in programari:
                    programare_hateoas = ProgramareHATEOAS(
                    id_doctor=programare.id_doctor.id_doctor,
                    cnp_pacient=programare.cnp_pacient.cnp,
                    data=programare.data,
                    status=programare.status,
                    links=LinkSet({
                    "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                    "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                    "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                    "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
                    })
                    )
                    programari_hateoas_list.append(programare_hateoas)
                return programari_hateoas_list
            else:
                raise HTTPException(status_code=422, detail="Parametrul type are o valoare incorecta.")
        elif date is not None:
            try:
                grpc_token_request = TokenRequest(token=current_user)
                token_response = auth_service.ValidateToken(grpc_token_request)
                if not token_response.valid:
                    raise HTTPException(status_code=401, detail="Token-ul nu este valid")
                if token_response.role!="admin" and token_response.role!="pacient":
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Doar adminul si pacientul in sine pot vedea programarile pacientului.")
                patient = Pacient.get(Pacient.cnp == cnp)
                if token_response.role!="admin" and str(patient.id_user)!=token_response.sub:
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Accesare a unui alt pacient.")
                programare = Programare.get((Programare.cnp_pacient==cnp) & (Programare.data==date))
                programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
                })
            )
                return programare_hateoas
            except Pacient.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"}}
            except Programare.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"+str(cnp)}}
        elif statusp is not None:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.role!="admin" and token_response.role!="pacient":
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request) 
                raise HTTPException(status_code=403, detail="Doar adminul si pacientul in sine pot vedea informatiile personale.")
            patient = Pacient.get(Pacient.cnp == cnp)
            if token_response.role!="admin" and str(patient.id_user)!=token_response.sub:
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Accesare a unui alt pacient.")
            programari=Programare.select().where((Programare.cnp_pacient==cnp) & (Programare.status==statusp))
            programari_hateoas_list=[]
            for programare in programari:
                programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
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
                if token_response.role!="pacient" or (token_response.role=="pacient" and token_response.sub!=str(uid)):
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request) 
                    raise HTTPException(status_code=403, detail="Doar pacientul in sine poate vedea informatiile personale.")
                patient = Pacient.get((Pacient.cnp == cnp)&(Pacient.id_user == uid))
                patient_hateoas = PacientHATEOAS(
                        cnp=str(patient.cnp),
                        id_user=patient.id_user,
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        data_nasterii=patient.data_nasterii,
                        is_active=patient.is_active,
                        links=LinkSet({
                        "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                        "parent":{"href":"/api/medical_office/patients/"},
                        "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"},
                        "delete_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"DELETE"},
                        "create_update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PUT"},
                        "update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PATCH"}
                        })
                    )

                return patient_hateoas
            except Pacient.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"}}
        else:
            try:
                grpc_token_request = TokenRequest(token=current_user)
                token_response = auth_service.ValidateToken(grpc_token_request)
                if not token_response.valid:
                    raise HTTPException(status_code=401, detail="Token-ul nu este valid")
                if token_response.role!="admin" and token_response.role!="pacient": 
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Doar adminul si pacientul in sine pot vedea informatiile personale.")
                patient = Pacient.get(Pacient.cnp == cnp)
                if token_response.role!="admin" and str(patient.id_user)!=token_response.sub:
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Accesare a unui alt pacient.")
                patient_hateoas = PacientHATEOAS(
                        cnp=str(patient.cnp),
                        id_user=patient.id_user,
                        nume=patient.nume,
                        prenume=patient.prenume,
                        email=patient.email,
                        telefon=patient.telefon,
                        data_nasterii=patient.data_nasterii,
                        is_active=patient.is_active,
                        links=LinkSet({
                        "self":{"href":"/api/medical_office/patients/"+str(patient.cnp)},
                        "parent":{"href":"/api/medical_office/patients/"},
                        "get_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"GET"},
                        "delete_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"DELETE"},
                        "create_update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PUT"},
                        "update_patient":{"href":"/api/medical_office/patients/"+str(patient.cnp),"type":"PATCH"}
                        })
                    )

                return patient_hateoas
            except _channel._InactiveRpcError:
                raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
            except Pacient.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Pacient.DoesNotExist:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office/patients/"}}
    #except Exception as e:
      #  print(e)

@app.delete("/api/medical_office/patients/{cnp}")
async def delete_patient(cnp: int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid.")
        patient = Pacient.get(Pacient.cnp == cnp)
        if token_response.role!="pacient" and (token_response.role!="pacient" and token_response.sub!=patient.id_user): 
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar pacientul in sine isi poate dezactiva contul.")
        if patient.is_active==False:
            raise HTTPException(status_code=404, detail="Acest pacient a fost sters deja.")
        patient.is_active=False
        patient.save()
        response.status_code=status.HTTP_204_NO_CONTENT
    except Pacient.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")


@app.put("/api/medical_office/patients/{cnp}")
async def create_update_patient(cnp: int, patient: CreatePacient,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:        
        existing_patient = Pacient.get(Pacient.cnp == cnp)
        #Protectie impotriva atacurilor la calea de acces
        pattern = re.compile(r'[.,\/]')
        pattern_email = re.compile(r'[,\/]')
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="pacient" or (token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user)):
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Doar pacientul in sine isi poate modifica informatiile.")
        if pattern.search(patient.nume) or pattern.search(patient.prenume) or not patient.telefon.isnumeric() or pattern_email.search(patient.email) or len(patient.telefon)!=10:
                raise HTTPException(status_code=422, detail="Datele pacientului sunt gresite.")
        if existing_patient.is_active==False:
            raise HTTPException(status_code=409, detail="Nu se pot modifica datele unui pacient inactiv.")#Explicatie la PUT pe programari
        #existing_patient.id_user=patient.id_user
        existing_patient.nume = patient.nume
        existing_patient.prenume = patient.prenume
        existing_patient.email = patient.email
        existing_patient.telefon = patient.telefon
        existing_patient.data_nasterii = patient.data_nasterii
        existing_patient.is_active=True
        existing_patient.save()
        
        response.status_code=status.HTTP_204_NO_CONTENT
    except IntegrityError as e:
            print(e)
            raise HTTPException(status_code=409, detail="Nu poate fi actualizat pacientul pentru ca email-ul este deja in uz.")
    except OperationalError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Nu poate fi actualizat pacientul pentru ca una din urmatoarele date e gresita: cnp, telefon, email, data de nastere mai mica de 18 ani.")
    except _channel._InactiveRpcError:
            raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Pacient.DoesNotExist:
        try:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.role!="pacient": 
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar pacientul in sine isi poate completa informatiile personale.")
            #Protectie impotriva atacurilor la calea de acces
            pattern = re.compile(r'[.,\/]')
            pattern_email = re.compile(r'[,\/]')
            if pattern.search(patient.nume) or pattern.search(patient.prenume) or not patient.telefon.isnumeric() or pattern_email.search(patient.email) or len(str(cnp))!=13 or len(patient.telefon)!=10:
                raise HTTPException(status_code=422, detail="Datele pacientului sunt gresite.")
            new_patient = Pacient.create(
                cnp=cnp,
                id_user=int(token_response.sub),
                nume=patient.nume,
                prenume=patient.prenume,
                email=patient.email,
                telefon=patient.telefon,
                data_nasterii=patient.data_nasterii,
                is_active=True
            )
            patient_hateoas = PacientHATEOAS(
                cnp=str(cnp),
                id_user=int(token_response.sub),
                nume=patient.nume,
                prenume=patient.prenume,
                email=patient.email,
                telefon=patient.telefon,
                data_nasterii=patient.data_nasterii,
                is_active=True,
                links=LinkSet({
                "self":{"href":"/api/medical_office/patients/"+str(cnp)},
                "parent":{"href":"/api/medical_office/patients/"},
                "get_patient":{"href":"/api/medical_office/patients/"+str(cnp),"type":"GET"},
                "delete_patient":{"href":"/api/medical_office/patients/"+str(cnp),"type":"DELETE"},
                "create_update_patient":{"href":"/api/medical_office/patients/"+str(cnp),"type":"PUT"},
                    "update_patient":{"href":"/api/medical_office/patients/"+str(cnp),"type":"PATCH"}
                })
            )
            response.status_code=status.HTTP_201_CREATED
            return patient_hateoas
        except IntegrityError as e:
            print(e)
            raise HTTPException(status_code=409, detail="Nu poate fi creat pacientul pentru ca email-ul este refolosit sau uid-ul este refolosit.")
        except OperationalError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Nu poate fi creat pacientul pentru ca una din urmatoarele date e gresita: cnp, telefon, email, data de nastere mai mica de 18 ani. ")
        except _channel._InactiveRpcError:
            raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
            
@app.patch("/api/medical_office/patients/{cnp}")
async def update_patient(cnp: int,response:Response, pacient:PatchPacient,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_patient = Pacient.get(Pacient.cnp == cnp)
        if token_response.role!="pacient" and (token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user)):
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar pacientul in sine poate modifica informatiile personale.")
        pattern = re.compile(r'[.,\/]')
        pattern_email = re.compile(r'[,\/]')
        if existing_patient.is_active==False:
            raise HTTPException(status_code=409, detail="Nu se pot modifica datele unui pacient inactiv.")#Explicatii la PUT programari.
        if pacient.nume is not None:
            if pattern.search(pacient.nume):
                raise HTTPException(status_code=422, detail="Numele pacientului contine caractere invalide.")
            existing_patient.nume = pacient.nume
        if pacient.prenume is not None:
            if pattern.search(pacient.prenume):
                raise HTTPException(status_code=422, detail="Numele pacientului contine caractere invalide.")
            existing_patient.prenume = pacient.prenume
        if pacient.email is not None:
            if pattern_email.search(pacient.email):
                raise HTTPException(status_code=422, detail="Email-ul pacientului contine caractere invalide.")
            existing_patient.email = pacient.email
        if pacient.telefon is not None:
           if len(pacient.telefon)!=10 or not pacient.telefon.isnumeric():
              raise HTTPException(status_code=422, detail="Telefonul pacientului nu respecta formatul.")
           existing_patient.telefon = pacient.telefon
        if pacient.data_nasterii is not None:
            existing_patient.data_nasterii = pacient.data_nasterii
        
        existing_patient.save()
        response.status_code=status.HTTP_204_NO_CONTENT
    except Pacient.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"}}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu poate fi creat pacientul pentru ca email-ul este refolosit.")
    except OperationalError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Nu poate fi creat pacientul pentru ca una din urmatoarele date e gresita: cnp, telefon, email, data de nastere mai mica de 18 ani. ")
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
        
        
        
#PROGRAMARI PACIENTI
@app.get("/api/medical_office/patients/{cnp}/physicians")
async def get_programari_pacient(cnp:int,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),page:int=None,items_per_page:int=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_patient = Pacient.get(Pacient.cnp == cnp)
        if token_response.role!="admin" and (token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user)):
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul sau pacientul in sine pot vedea programarile unui pacient existent.")
        if page is not None and items_per_page is not None:
            page = max(1, page)  
            page=min(100,page)
            items_per_page = max(1, items_per_page)  
            items_per_page=min(100,items_per_page)
            
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page

            
            programari=Programare.select().where(Programare.cnp_pacient==cnp).offset(start_idx).limit(items_per_page)
        else:
            programari=Programare.select().where(Programare.cnp_pacient==cnp)
        programari_hateoas_list = []
        for programare in programari:
            programare_hateoas = ProgramareHATEOAS(
                id_doctor=programare.id_doctor.id_doctor,
                cnp_pacient=programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                    "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                    "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                    "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                    "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                    "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
                    })
            )
            programari_hateoas_list.append(programare_hateoas)
        return programari_hateoas_list
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Pacient.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"}}
 
@app.get("/api/medical_office/patients/{cnp}/physicians/{id}")
async def get_programare_pacient(cnp:int,id:int,response:Response,data:date,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_patient = Pacient.get(Pacient.cnp == cnp)
        if token_response.role!="admin" and (token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user)):
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul sau pacientul in sine pot vedea programarea unui pacient existent.")
        programare = Programare.get((Programare.id_doctor == id) & (Programare.cnp_pacient==cnp) & (Programare.data==data))
        programare_hateoas = ProgramareHATEOAS(
            id_doctor=programare.id_doctor.id_doctor,
            cnp_pacient=programare.cnp_pacient.cnp,
            data=programare.data,
            status=programare.status,
            links=LinkSet({
                "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor)},
                "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"GET"},
                "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"DELETE"},
                "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(programare.id_doctor.id_doctor),"type":"PUT"}
                })
        )
        url=f"http://localhost:8001/api/medical_office_consultation?id_doctor={programare.id_doctor.id_doctor}&cnp={cnp}&data={programare.data}"
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code == 200:
            consultatie=json.loads(response1.content.decode())
            print(consultatie)
            programare_hateoas.links["get_consultatie"]={"href":f"http://localhost:8001/api/medical_office_consultation/{consultatie['id']}","type":"GET"}
        return programare_hateoas
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
    except Pacient.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"}}
    except Programare.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"}}
           
#Metoda reintrodusa de delete din partea pacientului
@app.delete("/api/medical_office/patients/{cnp}/physicians/{id}")  
async def delete_programare_pacient(cnp:int,id:int,data:date,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        programare = Programare.get((Programare.id_doctor == id) & (Programare.cnp_pacient==cnp) & (Programare.data==data))
        data_curenta=datetime.now().date()
        if programare.data<=data_curenta:
            raise HTTPException(status_code=409, detail="O programare nu poate fi setata ca anulata dupa ce a inceput.")
        if programare.status=="anulata":
            raise HTTPException(status_code=404, detail="Programarea a fost deja stearsa.")
        programare.status="anulata"
        programare.save()
       # programare.delete_instance()
        response.status_code=status.HTTP_204_NO_CONTENT
    except Programare.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/physicians/"+str(id)+"/patients/"}}
    except Pacient.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office/patients/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.") 

#Pacientul doar poate crea, nu si modifica programarea    
@app.put("/api/medical_office/patients/{cnp}/physicians/{id}")
async def create_programare_pacient(cnp:int,id:int,programare:CreateProgramare,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
   try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        existing_patient = Pacient.get(Pacient.cnp == cnp)
        if token_response.role!="pacient" or (token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user)):
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar adminul sau pacientul in sine pot modifica programarile unui pacient existent.")
        ex_programare = Programare.get((Programare.id_doctor == id) & (Programare.cnp_pacient==cnp) & (Programare.data==programare.data))
        raise HTTPException(status_code=403, detail="Pacientul nu are voie sa modifice informatiile unei programari existente.")
   except Programare.DoesNotExist:
        try:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            existing_patient = Pacient.get(Pacient.cnp == cnp)
            if token_response.role=="pacient" and token_response.sub!=str(existing_patient.id_user):
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request)
                    raise HTTPException(status_code=403, detail="Doar pacientul in sine poate crea o noua programare pentru un pacient existent.")
            if existing_patient.is_active==False:
                raise HTTPException(status_code=409, detail="Nu se poate crea o programare pentru un pacient inactiv.")#When a PUT representation is inconsistent with the target resource[...]. The 409 (Conflict) or 415 (Unsupported Media Type) status codes are suggested-RFC 7231 dar se mentine si in RFC 9110
            data_curenta=datetime.now().date()
            if programare.data<data_curenta:
                raise HTTPException(status_code=422, detail="O programare nu poate fi creata la o data anterioara zilei de azi.")
            new_programare=Programare.create(
            cnp_pacient = cnp,
            id_doctor = id,
            data = programare.data,
            status = programare.status
        )
            programare_hateoas = ProgramareHATEOAS(
                id_doctor=new_programare.id_doctor.id_doctor,
                cnp_pacient=new_programare.cnp_pacient.cnp,
                data=programare.data,
                status=programare.status,
                links=LinkSet({
                "self":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(new_programare.id_doctor.id_doctor)},
                "parent":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians"},
                "get_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(new_programare.id_doctor.id_doctor),"type":"GET"},
                "delete_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(new_programare.id_doctor.id_doctor),"type":"DELETE"},
                "create_programare_pacient":{"href":"/api/medical_office/patients/"+str(cnp)+"/physicians/"+str(new_programare.id_doctor.id_doctor),"type":"PUT"}
                })
            )
            response.status_code=status.HTTP_201_CREATED
            return programare_hateoas
        except IntegrityError:
                raise HTTPException(status_code=409, detail="Nu poate fi creata programarea pentru ca pacientul sau doctorul nu exista.")#La fel ca cea de mai sus.
        except OperationalError:
                raise HTTPException(status_code=422, detail="Nu poate fi creata programarea pentru ca statusul nu este corect.")
        except _channel._InactiveRpcError:
            raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
            
