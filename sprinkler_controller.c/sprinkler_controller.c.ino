constexpr auto BAUDE_RATE = 9600;

enum struct Message {
  None,
  Boot,
  Begin,
  End,
  Error,
  Ok,

  Count
};
constexpr char gMessageCodes[static_cast<int>(Message::Count)] = {'N','I','B','E','X','O'};
constexpr bool msg_is_valid(Message m) {
  return static_cast<int>(m) >= 0 && static_cast<int>(m) < static_cast<int>(Message::Count);
}
char msg_to_code(Message m) {
  if (!msg_is_valid(m)) {
    return 'N';
  }
  return gMessageCodes[static_cast<int>(m)];
}
bool code_is_valid(char c) {
  for (auto& mc : gMessageCodes) {
    if (mc == c) {
      return true;
    }
  }
  return false;
}
Message code_to_msg(char c) {
  if (!code_is_valid(c)) {
    return Message::None;
  }
  for (int i = 0; i < static_cast<int>(Message::Count); i++) {
    if (gMessageCodes[i] == c) {
      return static_cast<Message>(i);
    }
  }
  return Message::None;
}

void setup() {
  Serial.begin(BAUDE_RATE);
  send_message(Message::Boot, "Booting...");
}

void loop() {
  while(Serial.available() > 0) {
    Message msg = code_to_msg(Serial.read());
    switch(msg) {
      case Message::Begin:
        auto zone = Serial.read();
        send_message(Message::Ok, "Received begin message");
        break;
      default:
        send_message(Message::Error, "Unknown message received.");
        break;
    }
  }
}
