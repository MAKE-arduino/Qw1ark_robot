#define ANGLE -420 // макс колличество шагов (обязательно с минусом в начале)

#include "GyverStepper2.h"
// Пины: EN=-1 (отключён), DIR=2, STEP=4, MS1=3, MS2=5
GStepper2<STEPPER4WIRE> stepper(-1, 2, 4, 3, 5);

String receivedData = "";
int lastPrinted = 0;

// Фильтр: будем фильтровать само значение X (положение)
float filteredX = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  stepper.setMaxSpeed(500);
  stepper.setAcceleration(100);
  stepper.setTargetDeg(0L); // начальное положение
}

void loop() {
  stepper.tick(); // ОБЯЗАТЕЛЬНО

  // Чтение данных
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (receivedData.length() > 0) {
        int rawX = receivedData.toInt();

        // === ФИЛЬТРУЕМ САМО ЗНАЧЕНИЕ X ===
        filteredX = expRunningAverageAdaptive(rawX);

        // Устанавливаем ЦЕЛЕВОЕ ПОЛОЖЕНИЕ (можно масштабировать)
        // Например: 640 пикселей → 180 градусов
        float targetAngle = map(filteredX, 0, 640, ANGLE, abs(ANGLE));
        // Ограничим, чтобы не выходить за пределы
        targetAngle = constrain(targetAngle, ANGLE, abs(ANGLE));

        stepper.setTarget(expRunningAverageAdaptive(targetAngle));

        // Отправляем ОБРАТНО отфильтрованное значение (или текущее положение)
        // Для отладки: можно отправить filteredX или (int)stepper.getCurrentDeg()
        int currentSent = (int)targetAngle;
        if (abs(currentSent - lastPrinted) > 5) { // только если изменилось существенно
          Serial.println(currentSent);
          lastPrinted = currentSent;
        }
        receivedData = "";
      }
    } else {
      receivedData += c;
    }
  }
}

// === Фильтр: адаптивное экспоненциальное сглаживание ===
float expRunningAverageAdaptive(float newVal) {
  static float filtered = 0;
  float diff = abs(newVal - filtered);
  float k = (diff > 10) ? 0.7 : 0.05;  // резкое изменение — быстрее реагируем
  filtered += (newVal - filtered) * k;
  return filtered;
}
