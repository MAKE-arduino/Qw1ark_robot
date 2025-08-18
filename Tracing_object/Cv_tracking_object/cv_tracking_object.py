from ultralytics import YOLO
import cv2
import serial
import time

ser = serial.Serial('COM11', baudrate=9600, timeout=1)
time.sleep(2)  # Дать Arduino перезагрузиться

# Загружаем модель YOLOv5
model = YOLO('yolov5s.pt')  # или другая модель

cap = cv2.VideoCapture(0)

# Словарь классов COCO (для YOLOv5)
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
target_class = 'person' # индекс объекта обнаружения из списка выше


while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    result = results[0]

    annotated_frame = result.plot(
    conf=False,      # показывать уверенность
    boxes=True,     # показывать bounding boxes
    labels=True,    # показывать метки классов
    probs=True,      # показывать вероятности классов
)
    # Обрабатываем каждый объект
    for i, box in enumerate(result.boxes):
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        class_id = int(box.cls.item())
        confidence = box.conf.item()

        # Получаем название класса
        class_name = class_names.get(class_id, f"class_{class_id}")

    if class_name == target_class:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        print(x // 1)
    cv2.imshow('YOLO Detection', annotated_frame)
    ser.write(f"{x // 1}\n".encode('utf-8'))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
