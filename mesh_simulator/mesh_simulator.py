#!/usr/bin/env python3
"""Five-node EmergencyMesh simulator: A -> B -> C -> D -> Gateway.
Posts the same JSON message through /api/mesh/message at each hop, demonstrating TTL and deduplication.
"""
import argparse, json, time, uuid
import requests

NODES=['NODE-A','NODE-B','NODE-C','NODE-D','GATEWAY']

def main():
    p=argparse.ArgumentParser(); p.add_argument('--url',default='http://localhost:8000'); p.add_argument('--hazard',default='FIRE'); a=p.parse_args()
    base={'message_id':str(uuid.uuid4()),'node_id':'NODE-A','hazard':a.hazard,'severity':'CRITICAL' if a.hazard in ('FIRE','SMOKE') else 'HIGH','latitude':17.395,'longitude':78.4895,'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ'),'ttl':5,'hops':0,'flame':1 if a.hazard=='FIRE' else 0,'smoke':1 if a.hazard=='SMOKE' else 0,'rain':1 if a.hazard=='FLOOD' else 0,'sound':1 if a.hazard=='FLOOD' else 0}
    print('Mesh path:', ' -> '.join(NODES))
    for i,node in enumerate(NODES[:-1]):
        msg={**base,'node_id':node,'ttl':5-i,'hops':i}
        r=requests.post(base_url(a.url)+'/api/mesh/message',json=msg,timeout=3); print(node,'=>',r.json())
    print('Testing duplicate:'); print(requests.post(a.url+'/api/mesh/message',json={**base,'node_id':'NODE-B','ttl':4,'hops':1},timeout=3).json())

def base_url(x): return x.rstrip('/')
if __name__=='__main__': main()
