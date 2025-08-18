# Open_robot
### Этот проект про создание робо собаки ;). 
Я планирую сделать его в концепции что каждый узел (умная голова, манипулятор и т.д) будет отдельным Usb устройством(то бишь ардуино).
# Умная голова v1.0.0
## Схема соиденения компонентов
<img width="1677" height="663" alt="Untitled Sketch_МП" src="https://github.com/user-attachments/assets/a1731e22-c9c2-4350-882c-bae5c23f1c5e" />

## Код и сэмплы
### Код и сэмплы **находяться в папке tracking_object**
Код ардуино в папке **cv_port**
А питон сэмпл в папке **tracking_object**

## Либы
### вот команды для установки всех зависимостей
```bash
pip install opencv-python
pip install ultralytics
pip install numpy
```

## Описание работы
**Перед запуском кода вот тут, вы указываете на какой предмет вы хотите наводиться:**

<img width="317" height="79" alt="Снимок экрана 2025-08-18 112743" src="https://github.com/user-attachments/assets/03334865-8806-47a8-8bdf-0af1b7b39c7a" />

Из списка ↓

<img width="951" height="501" alt="Снимок экрана 2025-08-18 113148" src="https://github.com/user-attachments/assets/268b9e7b-099c-4caf-8cd9-39376d5aec6d" />

### Дальше загружаете прошивку в ардуино!
**Запускайте код на пк указав нужный порт куда подключена ардуино вот тут ↓**

<img width="634" height="37" alt="Снимок экрана 2025-08-18 113712" src="https://github.com/user-attachments/assets/69916867-d5c5-48ae-a89c-dab1b2ae6771" />

Всё, **камера наводиться на выбранный объект по оси X!**
