from app.database import init_db, SessionLocal
from app.models import Node, Shelter, SafeZone
init_db(); db=SessionLocal()
for i,(lat,lng) in enumerate([(17.3850,78.4867),(17.3890,78.4860),(17.3950,78.4895),(17.4010,78.4875),(17.4070,78.4910)],1):
    if not db.query(Node).filter_by(node_id=f'NODE-{i:02d}').first(): db.add(Node(node_id=f'NODE-{i:02d}',latitude=lat,longitude=lng,signal=max(60,100-i*7),battery=100-i*3,hops=i-1))
if db.query(Shelter).count()==0: db.add_all([Shelter(name='Central Emergency Shelter',latitude=17.4070,longitude=78.4910,capacity=300),Shelter(name='Safe Assembly Zone',latitude=17.4010,longitude=78.4875,capacity=150)])
if db.query(SafeZone).count()==0: db.add_all([SafeZone(name='Central Safe Zone',latitude=17.4070,longitude=78.4910,radius_m=300),SafeZone(name='Assembly Safe Zone',latitude=17.4010,longitude=78.4875,radius_m=250)])
db.commit(); db.close(); print('Database seeded.')
