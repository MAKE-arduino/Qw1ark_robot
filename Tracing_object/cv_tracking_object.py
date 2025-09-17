from ultralytics import YOLO
import cv2
import serial
import time

# Подключение к Arduino
try:
    ser = serial.Serial('COM18', baudrate=9600, timeout=1)
    time.sleep(2)  # Дать Arduino время на перезагрузку
    print("✅ Подключено к Arduino")
except Exception as e:
    print(f"❌ Ошибка подключения к Arduino: {e}")
    exit()

# Загрузка модели YOLOv8
model = YOLO('yolov8s.pt')  # Используем yolo v8 small

# Включение камеры
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ Не удалось открыть камеру")
    exit()

# Словарь классов COCO для YOLOv8
class_names = {
    0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
    5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
    10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
    14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
    20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
    25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
    30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat',
    35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
    39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon',
    45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange',
    50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut',
    55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
    60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse',
    65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
    70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock',
    75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
}

target_class = 'person'  # объект, который мы ищем

target_class_id = None
for key, value in class_names.items():
    if value == target_class:
        target_class_id = key
        break

if target_class_id is None:
    print(f"❌ Класс '{target_class}' не найден в списке")
    exit()

# Переменные для хранения последнего найденного объекта
last_x = None
last_y = None

pre_last_x = None
pre_last_y = None
while True:
    send_x, send_y=None
    ret, frame = cap.read()
    if not ret:
        print("❌ Не удалось получить кадр")
        break

    # Запуск модели
    results = model(frame)
    result = results[0]

    # Получение аннотированного кадра
    annotated_frame = result.plot(
        conf=False,  # не показывать уверенность
        boxes=True,  # показывать bounding boxes
        labels=True,  # показывать метки классов
        probs=False,  # не показывать вероятности классов
    )

    # Обработка каждого объекта
    found_target = False
    last_x = []
    last_y = []
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        class_id = int(box.cls.item())
        confidence = box.conf.item()

        # Получаем название класса
        class_name = class_names.get(class_id, f"class_{class_id}")

        # Проверяем, является ли объект целевым
        if class_name == target_class and confidence > 0.5:  # порог уверенности
            found_target = True
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            last_x.append(x)
            last_y.append(y)
            # Рисуем центр объекта
            cv2.circle(annotated_frame, (int(x), int(y)), 5, (0, 255, 0), -1)

            # Выводим координаты
            print(f"Найден {target_class} в координатах X: {int(x)}")
    if pre_last_x:
        values = []
        mined = 1000
        for x in last_x:
            v = abs(x-pre_last_x)
            if v<mined:
                mined = v
                send_x = x

    else:
        if last_x:
            send_x = last_x[0]
#-----------------------------------
    if pre_last_y:
        values = []
        mined = 1000
        for y in last_y:
            v = abs(y-pre_last_y)
            if v<mined:
                mined = v
                send_x = x

    else:
        if last_y:
            send_y = last_y[0]


    # Отправляем координату в Arduino, если объект найден
    if send_x and send_y:
        try:
            ser.write(f"{int(send_x)}:{int(send_y)}\n".encode('utf-8'))
            print(f"Отправлено: {int(send_x)}")
        except Exception as e:
            print(f"Ошибка отправки данных: {e}")

    # Отображение кадра
    cv2.imshow('YOLOv8 Detection', annotated_frame)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    pre_last_x = send_x
# Очистка
cap.release()
cv2.destroyAllWindows()
ser.close()
print("✅ Программа завершена")
