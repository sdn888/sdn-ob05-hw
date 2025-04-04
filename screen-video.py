import cv2
import numpy as np
import pyautogui

# Получаем размер экрана
screen_size = pyautogui.size()

# Задаем кодек и создаем объект записи видео
fourcc = cv2.VideoWriter_fourcc(*"XVID")  # можно попробовать другие кодеки, например, "MJPG"
out = cv2.VideoWriter("output.avi", fourcc, 20.0, (screen_size.width, screen_size.height))

while True:
    # Захватываем скриншот
    img = pyautogui.screenshot()

    # Преобразуем изображение в формат numpy массива
    frame = np.array(img)

    # Преобразуем цвета из BGR в RGB (или наоборот, в зависимости от кодека)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Записываем кадр в видеофайл
    out.write(frame)

    # Отображаем записываемый кадр (можно убрать, если не нужно окно)
    cv2.imshow("Screen Recorder", frame)

    # Выход из цикла по нажатию клавиши "q"
    if cv2.waitKey(1) == ord("q"):
        break

# Освобождаем ресурсы
out.release()
cv2.destroyAllWindows()
