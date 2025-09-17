template<typename T, uint8_t N>
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
#define PINserv 3


#include "GyverStepper2.h"
#include "Servo.h"
Servo ser;
// Пины: EN=-1 (отключён), DIR=2, STEP=4, MS1=3, MS2=5
GStepper2<STEPPER4WIRE> stepper(-1, 2, 4, 3, 5);

String receivedDataX, receivedDataY = "";
int lastPrinted = 0;

// Фильтр: будем фильтровать само значение X (положение)
float filteredX, FilteredY = 0;

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);

  Servo.attach(PINserv);

  stepper.setMaxSpeed(500);
  stepper.setAcceleration(100);
  stepper.setTargetDeg(0L);  // начальное положение
}

void loop() {
  stepper.tick();  // ОБЯЗАТЕЛЬНО

  // Чтение данных
  while (Serial.available() > 0) {
    char c = Serial.read();
    String receivedDataX = Serial.readStringUntil(':');
    String receivedDataY = Serial.readStringUntil('\n');
    int rawX = receivedDataX.toInt();
    int rawY = receivedDataY.toInt();
    // === ФИЛЬТРУЕМ САМО ЗНАЧЕНИЕ ===
    filteredX = expRunningAverageAdaptive(rawX);
    FilteredY = expRunningAverageAdaptive(rawX);
    // Устанавливаем ЦЕЛЕВОЕ ПОЛОЖЕНИЕ (можно масштабировать)

    float targetAngleX = map(filteredX, 0, 640, -400, 400);
    float targetAngleY = map(filteredY, 0, 420, 0, 180);
    // Ограничим, чтобы не выходить за пределы
    targetAngleX = constrain(targetAngleX, -400, 400);
    targetAngleY = constrain(targetAngleY, 0, 180);
    stepper.setTarget(expRunningAverageAdaptive(aver.filter(targetAngleX)));
    ser.write(expRunningAverageAdaptive(aver.filter(targetAngleY)));
    // Отправляем ОБРАТНО отфильтрованное значение (или текущее положение)
    // Для отладки: можно отправить filteredX или (int)stepper.getCurrentDeg()
    receivedDataX = "";
    receivedDataY = "";
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
