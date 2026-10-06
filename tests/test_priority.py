from backend.app.services.priority import classify

def test_flame_critical(): assert classify(1,0,0,0)==('FIRE','CRITICAL')
def test_smoke_critical(): assert classify(0,1,0,0)==('SMOKE','CRITICAL')
def test_rain_sound(): assert classify(0,0,1,1)==('FLOOD_SOUND','HIGH')
def test_rain(): assert classify(0,0,1,0)==('FLOOD_WARNING','WARNING')
def test_sound(): assert classify(0,0,0,1)==('EMERGENCY_SOUND','WARNING')
def test_clear(): assert classify(0,0,0,0)==('CLEAR','NORMAL')
