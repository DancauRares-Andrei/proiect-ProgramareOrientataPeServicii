from app_uac import *
db=MySQLDatabase(database='medical_office',user='rares',password='rares',host='localhost',port=3306)
db_user=MySQLDatabase(database='medical_office',user='user',password='pass',host='localhost',port=3306)
data_limita = (datetime.now().date() - timedelta(days=365*18)).isoformat()
class Pacient(Model):
    cnp = CharField(primary_key=True, max_length=13)
    nume = CharField(max_length=50)
    prenume = CharField(max_length=50)
    email = CharField(unique=True, max_length=50,constraints=[Check("email LIKE '%%@%%.%%'")])
    telefon = CharField(max_length=10,constraints=[Check("LENGTH(telefon) = 10 AND telefon LIKE '0%%' AND telefon REGEXP '^[0-9]+$'")])
    id_user = IntegerField(unique=True)
    data_nasterii = DateField(constraints=[Check(f"data_nasterii <= '{data_limita}'")])
    is_active = BooleanField()
    
    class Meta:
        database = db_user

class Doctor(Model):
    id_doctor = AutoField(primary_key=True)
    nume = CharField(max_length=50)
    prenume = CharField(max_length=50)
    email = CharField(unique=True, max_length=50,constraints=[Check("email LIKE '%%@%%.%%'")])
    telefon = CharField(max_length=10,constraints=[Check("LENGTH(telefon) = 10 AND telefon LIKE '0%%' AND telefon REGEXP '^[0-9]+$'")])
    id_user = IntegerField(unique=True)
    specializare = CharField(max_length=10, constraints=[Check('specializare in ("dentist", "chirurg", "veterinar")')])
    
    class Meta:
        database = db_user

class Programare(Model):
    cnp_pacient = ForeignKeyField(Pacient, backref='programari_pacient')
    id_doctor = ForeignKeyField(Doctor, backref='programari_doctor')
    data = DateField()
    status = CharField(max_length=12, constraints=[Check('status in ("onorata", "neprezentat", "anulata")')])
    
    class Meta:
        database = db_user
        primary_key=CompositeKey('cnp_pacient','id_doctor','data')
    
class PacientHATEOAS(HyperModel):
    cnp: str
    id_user: int
    nume: str
    prenume: str
    email: str
    telefon: str
    data_nasterii: date
    is_active: bool
    links: dict
class PacientHATEOASDoctor(HyperModel):
    cnp: str
    nume: str
    prenume: str
    email: str
    telefon: str
    links: dict
class DoctorHATEOAS(HyperModel):
    id_doctor:int
    id_user:int
    nume: str
    prenume: str
    email:str
    telefon:str
    specializare:str
    links:dict
class DoctorHATEOASPacient(HyperModel):
    id_doctor:int
    nume: str
    prenume: str
    email:str
    specializare:str
    links:dict
class ProgramareHATEOAS(HyperModel):
    cnp_pacient:str
    id_doctor:int
    data:date
    status:str  
    links: dict
class CreatePacient(BaseModel):
    #id_user: int
    nume: str
    prenume: str
    email: str="string@test.com"
    telefon: str="0111111111"
    data_nasterii: date = "2001-10-30"
class CreateDoctor(BaseModel):
    id_user: int
    nume: str
    prenume: str
    email: str="string@test.com"
    telefon: str="0111111111"
    specializare: str
class UpdateDoctor(BaseModel):
    nume: str
    prenume: str
    email: str="string@test.com"
    telefon: str="0111111111"
    specializare: str
class PatchPacient(BaseModel):
    #id_user: int | None = None
    nume: str | None = None
    prenume: str | None = None 
    email: str | None = None
    telefon: str | None = None
    data_nasterii: date | None = None
class PatchDoctor(BaseModel):
   # id_user: int | None = None
    nume: str | None = None
    prenume: str | None = None
    email: str | None = None
    telefon: str | None = None
    specializare: str | None = None
class CreateProgramare(BaseModel):
    data:date = datetime.now().date()
    status:str    
    
    
db.connect()

if not Pacient.table_exists():
    Pacient._meta.database = db
    Doctor._meta.database = db
    Programare._meta.database = db
    db.create_tables([Pacient,Doctor,Programare])
    Pacient._meta.database = db_user
    Doctor._meta.database = db_user
    Programare._meta.database = db_user
