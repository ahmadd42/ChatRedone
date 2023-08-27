from typing import Annotated
from fastapi import FastAPI, Body
from pydantic import BaseModel


class NewUser(BaseModel):
    fname: Annotated[str, Body(pattern="^[A-Za-z]*$")]
    lname: Annotated[str, Body(pattern="^[A-Za-z]*$")]
    phone: Annotated[str, Body(min_length=10, max_length=14, pattern="^\+[0-9]*$")]
    id: Annotated[str, Body(max_length=20, pattern="^[A-Za-z0-9_-]*$")]
    pswd: Annotated[str, Body(min_length=8)]

class Credentials(BaseModel):
    uname: str
    pwd: str

app = FastAPI()

#To keep it simple, this nested list is used instead of a database. It simulates a database table having
#the columns "First Name", "Last Name", "Phone No.", "Username" and "Password" in this order

users = [["Ahmad","Rasheed","03336532705","ahmadd42","askari@111"], ["Dawood","Siddiq","03045013064","dawood123",\
        "Daood"], ["Ashar","Rasheed","03019237010","ashar2345","Dogar@123"],["Rifat","Riaz","03336581945",\
        "drrifatriaz","Drrifat"],["Faisal","Ishaq","03346565337","faisal.rana","askari@999"],\
        ["Maryam","Ahmad","03336547896","maryam.ahmad","mano@050719"]]

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
        if users[ind][4] != cr.pwd:
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
    nuser = [nu.fname, nu.lname, nu.phone, nu.id, nu.pswd]
    users.append(nuser)
    return {"msg":"User registered successfully"}