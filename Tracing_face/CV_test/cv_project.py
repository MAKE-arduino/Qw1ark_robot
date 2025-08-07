import cv2
import serial
import time

ser = serial.Serial('COM12', baudrate=9600, timeout=1)
time.sleep(2)  # Дать Arduino перезагрузиться

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Для ограничения частоты отправки и изменения значений
last_send_time = 0
last_sent_x = None  # Сохраняем последнее отправленное значение X
SEND_INTERVAL = 0.1  # 100 мс (ограничение частоты)
THRESHOLD = 10      # Минимальное изменение для отправки

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    current_time = time.time()

    if len(faces) > 0:
        x, y, w, h = faces[0]  # Только первое лицо
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Проверяем, нужно ли отправлять
        send = False
        if last_sent_x is None:
            # Первое обнаружение — отправляем сразу
            send = True
        else:
            # Проверяем, изменилось ли значение более чем на THRESHOLD
            if abs(x - last_sent_x) >= THRESHOLD:
                send = True

        # Если нужно отправить и прошло достаточно времени
        if send and (current_time - last_send_time >= SEND_INTERVAL):
            ser.write(f"{x}\n".encode('utf-8'))
            last_sent_x = x  # Обновляем последнее отправленное значение
            last_send_time = current_time

            # Читаем ответ, если есть
            while ser.in_waiting > 0:
                try:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        print(f"Arduino: {response}")
                except Exception as e:
                    print(f"Ошибка чтения: {e}")

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()