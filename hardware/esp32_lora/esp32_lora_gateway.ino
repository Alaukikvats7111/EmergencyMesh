// EmergencyMesh — ESP32 LoRa bridge. Adapt LoRa pins to your module/board.
// Expected Arduino serial: SENSOR,smoke,sound,rain,flame,severity
#include <ArduinoJson.h>
#include <SPI.h>
#include <LoRa.h>
const char* NODE_ID="NODE-01";
unsigned long lastId=0;
void setup(){Serial.begin(115200); Serial2.begin(115200); LoRa.setPins(18,14,26); if(!LoRa.begin(915E6)) while(true);}
void loop(){
 if(Serial2.available()){
   String line=Serial2.readStringUntil('\n'); line.trim();
   if(line.startsWith("SENSOR,")){int v[4];String sev;int idx=0,last=7;for(int i=0;i<4;i++){int p=line.indexOf(',',last);v[i]=line.substring(last,p<0?line.length():p).toInt();last=p+1;}sev=line.substring(last);
    StaticJsonDocument<384> d; d["message_id"]=String(NODE_ID)+"-"+String(millis());d["node_id"]=NODE_ID;d["hazard"]=sev=="CRITICAL"?(v[3]?"FIRE":"SMOKE"):(v[2]?"FLOOD_WARNING":"EMERGENCY_SOUND");d["severity"]=sev;d["smoke"]=v[0];d["sound"]=v[1];d["rain"]=v[2];d["flame"]=v[3];d["ttl"]=5;d["hops"]=0;d["latitude"]=17.3850;d["longitude"]=78.4867;String out;serializeJson(d,out);LoRa.beginPacket();LoRa.print(out);LoRa.endPacket(); Serial.println(out);
   }
 }
 int packet=LoRa.parsePacket(); if(packet){String msg;while(LoRa.available())msg+=(char)LoRa.read();LoRa.beginPacket();LoRa.print(msg);LoRa.endPacket();}
}
