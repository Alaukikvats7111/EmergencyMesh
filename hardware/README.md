# Hardware integration

## Arduino UNO
Wire sensors exactly as the supplied project specification: Smoke D8, Sound D9, Rain D10, Flame D11, Buzzer D12, Red D7, Blue D6, Green D5. The sketch emits `SENSOR,smoke,sound,rain,flame,severity` over Serial.

## ESP32 + LoRa
Connect the UNO Serial output to an appropriate 3.3V-safe ESP32 serial interface (use level shifting where required). Connect the LoRa module according to its board-specific pinout; the example uses SPI and `LoRa.setPins(18,14,26)`, which must be changed for your ESP32/LoRa board. Do not connect 5V UART directly to ESP32 GPIO.

The ESP32 converts the sensor event into JSON with node ID, hazard, severity, sensor values, TTL and hop count. A gateway service can POST the JSON to `/api/mesh/message`.
