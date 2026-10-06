// EmergencyMesh — Arduino UNO sensor node
// Existing wiring: Smoke D8, Sound D9, Rain D10, Flame D11, Buzzer D12, Red D7, Blue D6, Green D5
const int SMOKE=8,SOUND=9,RAIN=10,FLAME=11,BUZZER=12,RED=7,BLUE=6,GREEN=5;
void setup(){Serial.begin(115200); pinMode(SMOKE,INPUT);pinMode(SOUND,INPUT);pinMode(RAIN,INPUT);pinMode(FLAME,INPUT);pinMode(BUZZER,OUTPUT);pinMode(RED,OUTPUT);pinMode(BLUE,OUTPUT);pinMode(GREEN,OUTPUT);}
void loop(){
 int smoke=digitalRead(SMOKE),sound=digitalRead(SOUND),rain=digitalRead(RAIN),flame=digitalRead(FLAME);
 const char* severity="NORMAL"; if(flame||smoke) severity="CRITICAL"; else if(rain&&sound) severity="HIGH"; else if(rain||sound) severity="WARNING";
 digitalWrite(RED,strcmp(severity,"CRITICAL")==0); digitalWrite(BLUE,strcmp(severity,"HIGH")==0||strcmp(severity,"WARNING")==0); digitalWrite(GREEN,strcmp(severity,"NORMAL")==0); digitalWrite(BUZZER,strcmp(severity,"CRITICAL")==0);
 Serial.print("SENSOR,"); Serial.print(smoke);Serial.print(',');Serial.print(sound);Serial.print(',');Serial.print(rain);Serial.print(',');Serial.print(flame);Serial.print(',');Serial.println(severity); delay(500);
}
