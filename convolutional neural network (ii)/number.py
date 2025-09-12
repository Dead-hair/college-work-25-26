# Импорт модулей
import tensorflow as tf  # pip install tensorflow
import numpy as np  # pip install numpy
from PIL import Image  # pip install pillow
import os

# Параметры
img_height = 28
img_width = 28

# Функция для загрузки и предобработки изображений
def load_images_from_folder(folder):
    images = []
    labels = []
    for label in range(10):
        path = os.path.join(folder, str(label))
        for filename in os.listdir(path):
            img_path = os.path.join(path, filename)
            img = Image.open(img_path).convert('L')
            img = img.resize((img_width, img_height))
            img = np.asarray(img)
            img = img / 255.0
            images.append(img)
            labels.append(label)
    return np.array(images), np.array(labels)

# Загрузка и предобработка данных
x_train, y_train = load_images_from_folder('train')
x_test, y_test = load_images_from_folder('test')

# Убедимся, что данные имеют правильные формы перед reshape
print(f'Количество train-изобр.: {x_train.shape[0]}, высота/ширина: {x_train.shape[1]}x{x_train.shape[2]}px')
print(f'Количество test-изобр.: {x_test.shape[0]}, высота/ширина: {x_test.shape[1]}x{x_test.shape[2]}px')

x_train = x_train.reshape(-1, img_height, img_width, 1)
x_test = x_test.reshape(-1, img_height, img_width, 1)

# Создание модели нейросети с использованием Input
model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(img_height, img_width, 1)),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Компиляция и обучение модели
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)

# Оценка модели
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f'Точность на тестовом наборе данных: {test_acc}')

# Сохранение модели в новом формате Keras
model.save('my_model.keras')
print(f'Модель создана!')