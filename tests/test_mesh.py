from backend.app.services.mesh import MeshManager

def test_dedup_and_ttl():
 m=MeshManager(); assert m.should_forward('x',2); assert not m.should_forward('x',2); assert not m.should_forward('y',0)
