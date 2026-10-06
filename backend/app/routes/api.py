from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database import get_db
from ..models import Node, Emergency, Shelter, SafeZone
from ..schemas import NodeIn, EmergencyIn, RouteRequest, AdminLogin
from ..services.priority import classify, severity_rank
from ..services.mesh import mesh
from ..services.broadcaster import broadcaster
from ..services.routing import route

router=APIRouter(prefix="/api")

@router.get('/system/status')
def status(db:Session=Depends(get_db)):
    nodes=db.query(Node).all(); active=db.query(Emergency).filter(Emergency.active==True).count()
    return {"internet":"ONLINE","mesh":"ACTIVE" if mesh.gateway_online else "LOCAL_ONLY","nodes":len(nodes),"active_emergencies":active}

@router.post('/nodes')
def upsert_node(data:NodeIn,db:Session=Depends(get_db)):
    n=db.query(Node).filter(Node.node_id==data.node_id).first()
    if not n: n=Node(node_id=data.node_id); db.add(n)
    for k,v in data.model_dump().items(): setattr(n,k,v)
    n.last_seen=datetime.now(timezone.utc); db.commit(); db.refresh(n)
    return n.__dict__

@router.get('/nodes')
def nodes(db:Session=Depends(get_db)):
    return [{"node_id":n.node_id,"latitude":n.latitude,"longitude":n.longitude,"status":n.status,"signal":n.signal,"battery":n.battery,"hops":n.hops,"last_seen":n.last_seen} for n in db.query(Node).order_by(Node.node_id)]

async def persist_emergency(data: EmergencyIn, db: Session):
    # Ignore duplicate messages
    existing = (
        db.query(Emergency)
        .filter(Emergency.message_id == data.message_id)
        .first()
    )

    if existing:
        return existing, False

    # Determine emergency type from sensor values
    hazard, severity = classify(
        data.flame,
        data.smoke,
        data.rain,
        data.sound
    )

    # If frontend explicitly sends a hazard, use it
    if data.hazard and data.hazard not in ("AUTO", "CLEAR"):
        hazard = data.hazard.upper()

    # IMPORTANT:
    # Only ONE emergency can be active at a time.
    # This prevents the previous FIRE alert from appearing
    # when a new FLOOD/SMOKE/HIGH alert is created.
    (
        db.query(Emergency)
        .filter(Emergency.active == True)
        .update(
            {"active": False},
            synchronize_session=False
        )
    )

    # Create the new emergency
    e = Emergency(
        alert_id=uuid4(),
        message_id=data.message_id,
        node_id=data.node_id,
        hazard=hazard,
        severity=severity,
        latitude=data.latitude,
        longitude=data.longitude,
        timestamp=data.timestamp,
        ttl=data.ttl,
        hops=data.hops,
        smoke=data.smoke,
        sound=data.sound,
        rain=data.rain,
        flame=data.flame,
        details=data.details,
        active=True
    )

    db.add(e)
    db.commit()
    db.refresh(e)

    # Broadcast NEW emergency
    await broadcaster.send({
        "type": "emergency",
        "emergency": {
            "alert_id": str(e.alert_id),
            "message_id": e.message_id,
            "node_id": e.node_id,
            "hazard": e.hazard,
            "severity": e.severity,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "timestamp": e.timestamp.isoformat()
                if e.timestamp else None,
            "ttl": e.ttl,
            "hops": e.hops,
            "smoke": e.smoke,
            "sound": e.sound,
            "rain": e.rain,
            "flame": e.flame,
            "details": e.details,
            "active": e.active
        }
    })

    return e, True

@router.post('/emergency')
async def create_emergency(data:EmergencyIn,db:Session=Depends(get_db)):
    e,new=await persist_emergency(data,db)
    if not e: return {"accepted":False,"duplicate":True,"reason":"Duplicate message or TTL exhausted"}
    return {"accepted":True,"duplicate":not new,"alert_id":e.alert_id,"hazard":e.hazard,"severity":e.severity}

@router.post('/mesh/message')
async def mesh_message(data:EmergencyIn,db:Session=Depends(get_db)):
    if data.ttl<=0: return {"accepted":False,"reason":"TTL expired"}
    e,new=await persist_emergency(data.model_copy(update={"ttl":data.ttl-1,"hops":data.hops+1}),db)
    return {"accepted":bool(e),"forwarded":bool(e and new),"ttl_remaining":max(0,data.ttl-1),"hops":data.hops+1}

@router.get('/emergencies')
def emergencies(active:bool|None=None,limit:int=100,db:Session=Depends(get_db)):
    q=db.query(Emergency).order_by(desc(Emergency.timestamp))
    if active is not None: q=q.filter(Emergency.active==active)
    return [e.__dict__ for e in q.limit(limit).all()]

@router.get('/emergencies/nearby')
def nearby(latitude:float,longitude:float,radius_m:float=3000,db:Session=Depends(get_db)):
    # Equirectangular approximation is adequate for the prototype's local radius.
    import math
    out=[]
    for e in db.query(Emergency).filter(Emergency.active==True).all():
        d=math.hypot((e.latitude-latitude)*111000,(e.longitude-longitude)*111000*math.cos(math.radians(latitude)))
        if d<=radius_m: out.append({**e.__dict__,"distance_m":round(d)})
    return sorted(out,key=lambda x:x['distance_m'])

@router.post('/emergencies/clear')
async def clear(db:Session=Depends(get_db)):
    db.query(Emergency).filter(Emergency.active==True).update({"active":False}); db.commit()
    await broadcaster.send({"type":"clear"})
    return {"cleared":True}

@router.get('/evacuation-route')
def evacuation_route(req:RouteRequest,db:Session=Depends(get_db)):
    hazards=[{"hazard":e.hazard,"severity":e.severity,"latitude":e.latitude,"longitude":e.longitude} for e in db.query(Emergency).filter(Emergency.active==True).all()]
    return route((req.latitude,req.longitude),hazards,req.shelter_id)

@router.get('/shelters')
def shelters(db:Session=Depends(get_db)):
    return [s.__dict__ for s in db.query(Shelter).all()]

@router.get('/safe-zones')
def safe_zones(db:Session=Depends(get_db)):
    return [s.__dict__ for s in db.query(SafeZone).all()]

@router.post('/admin/login')
def login(data:AdminLogin):
    if data.username=='admin' and data.password=='emergencymesh': return {"ok":True,"token":"demo-admin-token"}
    raise HTTPException(401,'Invalid admin credentials')

@router.post('/admin/shelters')
def add_shelter(data:dict,db:Session=Depends(get_db)):
    s=Shelter(name=data['name'],latitude=float(data['latitude']),longitude=float(data['longitude']),capacity=int(data.get('capacity',100))); db.add(s); db.commit(); db.refresh(s); return s.__dict__

@router.post('/admin/safe-zones')
def add_safe_zone(data:dict,db:Session=Depends(get_db)):
    s=SafeZone(name=data['name'],latitude=float(data['latitude']),longitude=float(data['longitude']),radius_m=float(data.get('radius_m',250))); db.add(s); db.commit(); db.refresh(s); return s.__dict__
@router.post("/demo/{hazard}")
async def demo_emergency(hazard: str, db: Session = Depends(get_db)):
    demos = {
        "FIRE": {
            "hazard": "FIRE",
            "severity": "CRITICAL",
            "flame": 1,
            "smoke": 0,
            "rain": 0,
            "sound": 0,
            "details": "Demo fire alert"
        },
        "SMOKE": {
            "hazard": "SMOKE",
            "severity": "CRITICAL",
            "flame": 0,
            "smoke": 1,
            "rain": 0,
            "sound": 0,
            "details": "Demo smoke alert"
        },
        "FLOOD": {
            "hazard": "FLOOD_WARNING",
            "severity": "HIGH",
            "flame": 0,
            "smoke": 0,
            "rain": 1,
            "sound": 1,
            "details": "Demo flood warning"
        },
        "HIGH": {
            "hazard": "EMERGENCY_SOUND",
            "severity": "WARNING",
            "flame": 0,
            "smoke": 0,
            "rain": 0,
            "sound": 1,
            "details": "Demo critical alert"
        }
    }

    key = hazard.upper()

    if key not in demos:
        raise HTTPException(status_code=400, detail="Invalid demo hazard")

    # Remove ALL currently active emergencies
    db.query(Emergency).filter(
        Emergency.active == True
    ).update(
        {"active": False},
        synchronize_session=False
    )

    x = demos[key]

    emergency = Emergency(
        alert_id=uuid4(),
        message_id=str(uuid4()),
        node_id="NODE-03",
        hazard=x["hazard"],
        severity=x["severity"],
        latitude=17.395,
        longitude=78.489,
        timestamp=datetime.utcnow(),
        ttl=5,
        hops=0,
        smoke=x["smoke"],
        sound=x["sound"],
        rain=x["rain"],
        flame=x["flame"],
        details=x["details"],
        active=True
    )

    db.add(emergency)
    db.commit()
    db.refresh(emergency)

    await broadcaster.send({
        "type": "emergency",
        "emergency": {
            "message_id": emergency.message_id,
            "node_id": emergency.node_id,
            "hazard": emergency.hazard,
            "severity": emergency.severity,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude,
            "timestamp": emergency.timestamp.isoformat(),
            "ttl": emergency.ttl,
            "hops": emergency.hops,
            "smoke": emergency.smoke,
            "sound": emergency.sound,
            "rain": emergency.rain,
            "flame": emergency.flame,
            "details": emergency.details,
            "active": True
        }
    })

    return {
        "success": True,
        "hazard": emergency.hazard,
        "severity": emergency.severity
    }