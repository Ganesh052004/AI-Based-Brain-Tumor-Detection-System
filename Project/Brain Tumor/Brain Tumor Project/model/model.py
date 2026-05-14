import os
import keras
from keras.models import Sequential
from keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Initialize encoder
encoder = LabelEncoder()

data = []
labels = []

# Load Tumor images (Label 0)
for r, d, f in os.walk('dataset/brain_tumor_dataset/yes'):
    for file in f:
        if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
            try:
                img = Image.open(os.path.join(r, file)).convert('RGB').resize((128, 128))  # ✅ Ensure RGB
                img = np.array(img)
                if img.shape == (128, 128, 3):
                    data.append(img)
                    labels.append(0)
            except:
                print(f"Skipping corrupted image: {file}")

# Load Non-Tumor images (Label 1)
for r, d, f in os.walk('dataset/brain_tumor_dataset/no'):
    for file in f:
        if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
            try:
                img = Image.open(os.path.join(r, file)).convert('RGB').resize((128, 128))  # ✅ Ensure RGB
                img = np.array(img)
                if img.shape == (128, 128, 3):
                    data.append(img)
                    labels.append(1)
            except:
                print(f"Skipping corrupted image: {file}")

print(f"Total images loaded: {len(data)}")
print(f"Total labels loaded: {len(labels)}")

# Preprocessing
data = np.array(data) / 255.0  # Normalize
labels = np.array(labels)

# Train-test split
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, random_state=0)

# Define CNN model
model = Sequential([
    Input(shape=(128, 128, 3)),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.7),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')  # Binary classification
])

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
history = model.fit(x_train, y_train, epochs=20, batch_size=32, validation_data=(x_test, y_test))

# Save model in Keras format
model.save('brain_tumor_classifier_model.keras')

# Evaluation
loss, accuracy = model.evaluate(x_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

train_loss, train_acc = model.evaluate(x_train, y_train, verbose=0)
val_loss, val_acc = model.evaluate(x_test, y_test, verbose=0)

print(f"Training Accuracy: {train_acc * 100:.2f}%")
print(f"Validation Accuracy: {val_acc * 100:.2f}%")
print(f"Training Loss: {train_loss:.4f}")
print(f"Validation Loss: {val_loss:.4f}")

# Load and predict a single image
img_path = 'dataset/brain_tumor_dataset/no/1 no.jpeg'  # Update path as needed
try:
    img = Image.open(img_path).convert('RGB').resize((128, 128))  # ✅ Ensure RGB
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 128, 128, 3)

    # Show image
    plt.imshow(img)
    plt.axis('off')
    plt.show()

    # Predict
    prediction = model.predict(img_array)
    predicted_class = int(prediction[0][0] > 0.5)

    if predicted_class == 0:
        print("Prediction: Tumor Detected")
    else:
        print("Prediction: No Tumor Detected")

except Exception as e:
    print(f"Error loading image: {e}")
