from keras.models import load_model
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Load the saved model
model = load_model('brain_tumor_classifier_model.keras')

# Path to the image you want to predict
img_path = 'dataset/yes/Y21.jpg'  # <-- Change path as needed

try:
    # Load and preprocess the image
    img = Image.open(img_path).convert('RGB').resize((128, 128))
    img_array = np.array(img) / 255.0  # Normalize
    img_array = img_array.reshape(1, 128, 128, 3)

    # Show the image
    plt.imshow(img)
    plt.axis('off')
    plt.show()

    # Make prediction
    prediction = model.predict(img_array)
    predicted_class = int(prediction[0][0] > 0.5)  # Thresholding at 0.5

    # Show result
    if predicted_class == 0:
        print("Prediction: Tumor Detected")
    else:
        print("Prediction: No Tumor Detected")

except Exception as e:
    print(f"Error processing image: {e}")
