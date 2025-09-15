
const float DIV_RATIO = 0.5f;




void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(A0);
 

  Serial.print(raw);
  Serial.print("\r\n");

  delay(50);
}

