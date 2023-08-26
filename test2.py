from fastapi import FastAPI
from pydantic import BaseModel


class NewUser(BaseModel):
    name: str
    phone: str
    id: str
    pswd: str

class Credentials(BaseModel):
    uname: str
    pwd: str

app = FastAPI()

#To keep it simple, this nested list is used instead of a database. It simulates a database table having
#the columns "Name", "Phone No.", "Username" and "Password" in this order

users = [["Ahmad Rasheed","03336532705","ahmadd42","askari@111"], ["Dawood Siddiq","03045013064","dawood123",\
        "Daood"], ["Ashar Rasheed","03019237010","ashar2345","Dogar@123"],["Rifat Riaz","03336581945",\
        "drrifatriaz","Drrifat"],["Faisal Ishaq","03346565337","faisal.rana","askari@999"],\
        ["Maryam Ahmad","03336547896","maryam.ahmad","mano@050719"]]

LoggedInUsers = []

def searchUser(usname):
    for x in users:
        if usname in x:
            return users.index(x)
    return -1

@app.post("/login/")
async def login(cr: Credentials):
    ind = searchUser(cr.uname) 
    if ind > -1:
        if users[ind][3] != cr.pwd:
            return {"msg":"Incorrect Pasword"}
        elif cr.uname in LoggedInUsers:
            return {"msg":"User already logged in"}
        else:
            LoggedInUsers.append(cr.uname)
            return {"msg":"Logged in successfully"}
    else:
        return {"msg":"Invalid Username"}    
    
@app.post("/signup/")
async def register(nu: NewUser):
    name2 = nu.name.replace(" ","")

    if not name2.isalpha():
        return {"msg":"Invalid value for name"}
    elif not (nu.phone.isdigit() and len(nu.phone) >= 11 and len(nu.phone) <= 14):
        return {"msg":"Phone no should have 11 to 14 digits"}
    elif len(nu.pswd) < 8:
        return {"msg":"Password should have minimum 8 characters"}
    else:
        nuser = [nu.name, nu.phone, nu.id, nu.pswd]
        users.append(nuser)
        return {"msg":"User registered successfully"}