// Equal-resistor divider => Arduino sees half of sensor voltage
const float DIV_RATIO = 0.5f;

// ADC characteristics (Uno/Nano classic: 10-bit, 0–5 V)


void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(A0);
 

  Serial.print(raw);
  Serial.print("\r\n");

  delay(50);
}
