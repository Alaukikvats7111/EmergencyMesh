from backend.app.services.routing import route

def test_route_returns_path():
 r=route((17.392,78.487),[{"hazard":"FIRE","latitude":17.395,"longitude":78.4895}]); assert r['safe']; assert len(r['path'])>1
