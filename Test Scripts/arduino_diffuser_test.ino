const int mosfetPin = 9; // Connect MOSFET gate to digital pin 9

void setup() {
  pinMode(mosfetPin, OUTPUT);
  digitalWrite(mosfetPin, LOW); // Ensure MOSFET is off at startup
}

void loop() {
  // Turn the ultrasonic disk ON
  digitalWrite(mosfetPin, HIGH);
  delay(2000); // Keep it on for 1 second

  // Turn the ultrasonic disk OFF
  digitalWrite(mosfetPin, LOW);
  delay(3000); // Keep it off for 1 second
}
