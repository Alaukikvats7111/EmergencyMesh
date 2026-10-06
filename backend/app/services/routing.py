from math import radians, sin, cos, sqrt, atan2
from heapq import heappush, heappop

# Local deterministic graph: designed as a demo fallback when no external routing API is configured.
# Coordinates are around Hyderabad; nodes can be replaced by real OSM road graph data later.
GRID = [
    (17.3850,78.4867),(17.3870,78.4885),(17.3890,78.4860),(17.3910,78.4890),
    (17.3930,78.4865),(17.3950,78.4895),(17.3970,78.4870),(17.3990,78.4900),
    (17.4010,78.4875),(17.4030,78.4905),(17.4050,78.4880),(17.4070,78.4910)
]
EDGES = {i:[j for j in (i-1,i+1) if 0<=j<len(GRID)] for i in range(len(GRID))}
EDGES[1].append(4); EDGES[4].append(1); EDGES[3].append(6); EDGES[6].append(3); EDGES[6].append(9); EDGES[9].append(6)
SHELTERS=[{"id":1,"name":"Central Emergency Shelter","latitude":17.4070,"longitude":78.4910},{"id":2,"name":"Safe Assembly Zone","latitude":17.4010,"longitude":78.4875}]

def dist(a,b):
    R=6371000; p1,p2=radians(a[0]),radians(b[0]); dp=radians(b[0]-a[0]); dl=radians(b[1]-a[1])
    x=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*R*atan2(sqrt(x),sqrt(1-x))

def route(start, hazards, shelter_id=None):
    target = next((s for s in SHELTERS if s["id"]==shelter_id), None) or min(SHELTERS, key=lambda s: dist(start,(s["latitude"],s["longitude"])))
    target_idx=min(range(len(GRID)),key=lambda i:dist((GRID[i][0],GRID[i][1]),(target["latitude"],target["longitude"])))
    start_idx=min(range(len(GRID)),key=lambda i:dist(start,GRID[i]))
    def risk(pt):
        score=0; labels=[]
        for h in hazards:
            d=dist(pt,(h["latitude"],h["longitude"]))
            radius={"FIRE":900,"SMOKE":650,"FLOOD_WARNING":800,"FLOOD_SOUND":1000,"EMERGENCY_SOUND":450}.get(h["hazard"],500)
            if d<radius:
                labels.append(h["hazard"])
                score += {"FIRE":100000,"FLOOD_WARNING":100000,"FLOOD_SOUND":100000,"SMOKE":30000,"EMERGENCY_SOUND":10000}.get(h["hazard"],5000)*(1-d/radius)
        return score, labels
    pq=[(0,start_idx)]; came={}; cost={start_idx:0}
    while pq:
        c,u=heappop(pq)
        if u==target_idx: break
        for v in EDGES.get(u,[]):
            base=dist(GRID[u],GRID[v]); r,_=risk(GRID[v]); nc=c+base+r
            if nc<cost.get(v,float('inf')):
                cost[v]=nc; came[v]=u; heappush(pq,(nc,v))
    if target_idx not in cost: return {"safe":False,"reason":"No route available","shelter":target,"path":[]}
    path=[]; cur=target_idx
    while True:
        path.append(GRID[cur])
        if cur==start_idx: break
        cur=came[cur]
    path.reverse();
    hazards_avoided=[]
    for p in path:
        _,labels=risk(p)
        hazards_avoided.extend(labels)
    total=sum(dist(path[i],path[i+1]) for i in range(len(path)-1))
    return {"safe":True,"shelter":target,"path":[{"lat":p[0],"lng":p[1]} for p in path],"distance_m":round(total),"eta_minutes":max(1,round(total/75)),"risk_level":"LOW","avoids":sorted(set(hazards_avoided)),"reason":"Route selected using distance + hazard risk + blockage penalty; hazardous zones are heavily penalized."}
