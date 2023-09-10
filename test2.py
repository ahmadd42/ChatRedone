from typing import Annotated
from fastapi import FastAPI, Body, Form, Request, WebSocket, Response, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import random


class NewUser(BaseModel):
    fname: Annotated[str, Body(pattern="^[A-Za-z]+$")]
    lname: Annotated[str, Body(pattern="^[A-Za-z]+$")]
    phone: Annotated[str, Body(min_length=10, max_length=14, pattern="^\+\d+$")]
    id: Annotated[str, Body(min_length=5, max_length=20, pattern="^[A-Za-z0-9_-]+$")]
    pswd: Annotated[str, Body(min_length=8)]

class Credentials(BaseModel):
    uname: str = Body()
    psw: str = Body()

class Sess(BaseModel):
    sessid: str = Body()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

app = FastAPI()

manager = ConnectionManager()

templates = Jinja2Templates(directory='templates')
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "sample/static"),
    name="static",
)

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

def searchSession(sessid):
    for x in LoggedInUsers:
        if x[1] == sessid:
            return LoggedInUsers.index(x)
    return -1

def alreadyLoggedIn(uname):
    for x in LoggedInUsers:
            if x[0] == uname:
                return LoggedInUsers.index(x)
    return -1

@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    sessid = str(request.cookies.get('mysession'))
    if len(sessid) > 5 and searchSession(sessid) > -1:
        return templates.TemplateResponse('dashboard.html', {'request': request})
    else:
        return templates.TemplateResponse('index.html', {'request': request})

    #return templates.TemplateResponse('index.html', {'request': request})

@app.get('/chatmain/', response_class=HTMLResponse)
def chatroomMain(request: Request):
    sessid = str(request.cookies.get('mysession'))
    if len(sessid) > 5 and searchSession(sessid) > -1:
        return templates.TemplateResponse('ChatRoom.html', {'request': request})
    else:
        return templates.TemplateResponse('index.html', {'request': request})

@app.get('/dashboard/', response_class=HTMLResponse)
def getDashboard(request: Request):
    sessid = str(request.cookies.get('mysession'))
    if len(sessid) > 5 and searchSession(sessid) > -1:
        return templates.TemplateResponse('dashboard.html', {'request': request})
    else:
        return templates.TemplateResponse('index.html', {'request': request})

@app.post("/login/")
async def login(cr: Credentials, response: Response):
    ind = searchUser(cr.uname)
    ind2 = alreadyLoggedIn(cr.uname)

    if ind > -1:
        if users[ind][4] != cr.psw:
            return {"msg":"Incorrect Pasword"}
        else:
            if ind2 > -1:
                LoggedInUsers.remove(ind2)
        ########  Generate Login token
            sess = cr.uname[0:3] + str(random.randint(1001,999999))
        ###############################
            LoggedInUsers.append([cr.uname, sess])
        ########  For convenience, session handling is done through cookies which are local to browser, i.e.,
        ######## IE has its own cookies and Chrome has its own. Therefore, session is local to browser. 
        ######## A more proper way would be to write session values in a file on client machine. This method
        ####### is used by google.
        
            response.set_cookie(key="myusername", value=cr.uname, expires=2592000)
            response.set_cookie(key="mysession", value=sess, expires=2592000)
            return {"msg":"Logged in successfully"}
    else:
        return {"msg":"Invalid Username"}    
    
@app.post("/logout/")
async def logout(sid: Sess, response: Response):
    if len(sid.sessid) > 0 and searchSession(sid.sessid) > -1:
        for x in LoggedInUsers:
            if x[1] == sid.sessid:
                LoggedInUsers.remove(x)
                response.delete_cookie("myusername")
                response.delete_cookie("mysession")
    return {"msg":"User logged out successfully"}
    
@app.post("/signup/")
async def register(nu: NewUser):
    nuser = [nu.fname, nu.lname, nu.phone, nu.id, nu.pswd]
    users.append(nuser)
    return {"msg":"User registered successfully"}

@app.post("/test/")
async def testFunc():
    roomusers = ["ahmadd42","ashar2345","drrifat","faisal.rana"]
    return roomusers

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    await manager.broadcast(user_id + " has joined the room")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.broadcast(user_id + " has left the room")