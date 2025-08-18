template <typename T, uint8_t N>
class AverageWindow {
   public:
    float filter(T val) {
        _sum += val;
        if (++_i >= N) _i = 0;
        _sum -= _buffer[_i];
        _buffer[_i] = val;
        return (float)_sum / N;
    }

   private:
    T _buffer[N] = {};
    T _sum = 0;
    uint8_t _i = 0;
};
AverageWindow<int, 10> aver;

#define ANGLE -600

#include "GyverStepper2.h"

// Пины: EN=-1 (отключён), DIR=2, STEP=4, MS1=3, MS2=5
GStepper2<STEPPER4WIRE> stepper(-1, 2, 4, 3, 5);

String receivedData = "";
int lastPrinted = 0;

// Фильтр: будем фильтровать само значение X (положение)
float filteredX = 0;

void setup() {
  pinMode(13, OUTPUT);
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
        float targetAngle = map(filteredX, 0, 640, -400, 400);
        // Ограничим, чтобы не выходить за пределы
        targetAngle = constrain(targetAngle, -400, 400);

        stepper.setTarget(expRunningAverageAdaptive(aver.filter(targetAngle)));

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

  //delay(1); // небольшая пауза, чтобы не перегружать
}

// === Фильтр: адаптивное экспоненциальное сглаживание ===
float expRunningAverageAdaptive(float newVal) {
  static float filtered = 0;
  float diff = abs(newVal - filtered);
  float k = (diff > 10) ? 0.7 : 0.05;  // резкое изменение — быстрее реагируем
  filtered += (newVal - filtered) * k;
  return filtered;
}