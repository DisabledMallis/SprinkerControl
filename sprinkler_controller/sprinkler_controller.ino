constexpr auto BAUDE_RATE = 9600;

#define MESSAGE_PING 'P'
#define MESSAGE_BOOT 'B'
#define MESSAGE_ZONE 'Z'
#define MESSAGE_END 'E'
#define MESSAGE_OK 'O'
#define MESSAGE_ERROR 'X'

#define ZONE_PIN_BASE 4

void setup() {
  Serial.begin(BAUDE_RATE);
  Serial.print(MESSAGE_BOOT);
  Serial.print("Booting...");
  for (int z = 1; z < 5; z++) {
    pinMode(ZONE_PIN_BASE + z, OUTPUT);
  }
  delay(1000);
  for (int z = 1; z < 5; z++) {
    digitalWrite(ZONE_PIN_BASE + z, HIGH);
    delay(1000);
    digitalWrite(ZONE_PIN_BASE + z, LOW);
    delay(1000);
  }
  Serial.println("BOOT!");
}

struct Zone {
  Zone() = default;
  Zone(int zone) : mZone(zone) {}
  operator int() const {
    return mZone;
  }

  bool valid() const {
    return mZone > 0 && mZone < 5;
  }
  bool begin() const {
    end();
    digitalWrite(ZONE_PIN_BASE + mZone, HIGH);
    return true;
  }
  bool end() const {
    for (int i = 1; i < 5; i++) {
      digitalWrite(ZONE_PIN_BASE + i, LOW);
    }
    return true;
  }
private:
  int mZone = 0;
};

size_t lastPing = 0;
size_t currentTime = 0;
void loop() {
  while(Serial.available() > 0) {
    auto msg = Serial.readStringUntil('\n');
    if (msg.length() <= 0) {
      continue;
    }
    // Check if newline is at the end, and remove if so
    if (msg.endsWith("\n")) {
      msg = msg.substring(0, msg.length() - 1);
    }
    switch(msg[0]) {
      case MESSAGE_ZONE:
        if (msg.length() <= 1) {
          Serial.print(MESSAGE_ERROR);
          Serial.print("No zone to begin");
        } else {
          Zone zone = msg[1] - '0';
          if (zone.valid()) {
            if (zone.begin()) {
              Serial.print(MESSAGE_OK);
              Serial.print("Began zone #");
              Serial.print(zone);
            } else {
              Serial.print(MESSAGE_ERROR);
              Serial.print("Couldn't begin zone #");
              Serial.print(zone);
            }
          } else {
            Serial.print(MESSAGE_ERROR);
            Serial.print("Invalid zone #");
            Serial.print(zone);
          }
        }
        Serial.println();
        break;
      case MESSAGE_END:
        for (int z = 1; z < 5; z++) {
          Zone zone{z};
          zone.end();
        }
        Serial.println(MESSAGE_OK);
        break;
      case MESSAGE_PING:
        lastPing = currentTime;
        Serial.println(MESSAGE_PING);
        break;
      default:
        Serial.print(MESSAGE_ERROR);
        Serial.println("Unknown message received.");
        break;
    }
  }
  currentTime = millis();
  // If we've gone 5 seconds without a ping
  if ((currentTime - lastPing) > 5000) {
    // Assume something's gone wrong and shut down the zones
    for (int z = 1; z < 5; z++) {
      Zone zone{z};
      zone.end();
    }
    
    // Reset this just so we dont spam idk
    lastPing = currentTime;
  }
  delay(1);
}
