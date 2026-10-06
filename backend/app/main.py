from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db, SessionLocal
from .models import Node, Shelter, SafeZone
from .routes.api import router
from .services.broadcaster import broadcaster

app=FastAPI(title='EmergencyMesh API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router)

@app.on_event('startup')
def startup():
    init_db(); db=SessionLocal()
    if db.query(Node).count()==0:
        for i,(lat,lng) in enumerate([(17.3850,78.4867),(17.3890,78.4860),(17.3950,78.4895),(17.4010,78.4875),(17.4070,78.4910)],1):
            db.add(Node(node_id=f'NODE-{i:02d}',latitude=lat,longitude=lng,signal=max(60,100-i*7),battery=100-i*3,hops=i-1))
    if db.query(Shelter).count()==0:
        db.add_all([Shelter(name='Central Emergency Shelter',latitude=17.4070,longitude=78.4910,capacity=300),Shelter(name='Safe Assembly Zone',latitude=17.4010,longitude=78.4875,capacity=150)])
    if db.query(SafeZone).count()==0:
        db.add_all([SafeZone(name='Central Safe Zone',latitude=17.4070,longitude=78.4910,radius_m=300),SafeZone(name='Assembly Safe Zone',latitude=17.4010,longitude=78.4875,radius_m=250)])
    db.commit(); db.close()

@app.get('/')
def root(): return {'name':'EmergencyMesh','status':'running','docs':'/docs'}

@app.websocket('/ws')
async def websocket(ws:WebSocket):
    await broadcaster.connect(ws)
    try:
        while True: await ws.receive_text()
    except Exception: broadcaster.disconnect(ws)
