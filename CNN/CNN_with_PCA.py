import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers.legacy import Adam
from keras.utils import to_categorical
from keras.layers import Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import cv2
from sklearn.model_selection import train_test_split
import pickle
import os
import pandas as pd
import random
from keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
import h5py
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

path = "FaceShape_Dataset"
labelFile = 'FaceLabels.csv'
batch_size_val = 50
steps_per_epoch_val = 1000
epochs_val =25
imageDimesions = (32, 32, 3)
testRatio = 0.2
validationRatio = 0.2

count = 0
images = []
classNo = []
myList = os.listdir(path)
print("Total Classes Detected:", len(myList))
noOfClasses = len(myList)
print("Importing Classes.....")
for x in range(0, len(myList)):
    myPicList = os.listdir(path + "/" + str(count))
    for y in myPicList:
        try:
            curImg = cv2.imread(path + "/" + str(count) + "/" + y)

            dim = (32, 32)

            resized = cv2.resize(curImg, dim, interpolation=cv2.INTER_AREA)

            images.append(resized)
            classNo.append(count)

        except Exception as e:
            print(str(e))
    print(count, end=" ")
    count += 1
print(" ")
images = np.array(images)
classNo = np.array(classNo)

X_train, X_test, y_train, y_test = train_test_split(images, classNo, test_size=testRatio)
X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=validationRatio)


print("Data Shapes")
print("Train", end="")
print(X_train.shape, y_train.shape)
print("Validation", end="")
print(X_validation.shape, y_validation.shape)
print("Test", end="")
print(X_test.shape, y_test.shape)

data = pd.read_csv(labelFile)
print("data shape ", data.shape, type(data))

num_of_samples = []
cols = 5
num_classes = noOfClasses
fig, axs = plt.subplots(nrows=num_classes, ncols=cols, figsize=(5, 300))
fig.tight_layout()
for i in range(cols):
    for j, row in data.iterrows():
        x_selected = X_train[y_train == j]
        axs[j][i].imshow(x_selected[random.randint(0, len(x_selected) - 1), :, :], cmap=plt.get_cmap("gray"))
        axs[j][i].axis("off")
        if i == 2:
            axs[j][i].set_title(str(j) + "-" + row["Name"])
            num_of_samples.append(len(x_selected))

print(num_of_samples)
plt.figure(figsize=(12, 4))
plt.bar(range(0, num_classes), num_of_samples)
plt.title("Distribution of the training dataset")
plt.xlabel("Class number")
plt.ylabel("Number of images")
plt.show()



import logging

# Set up the logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def grayscale(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

def equalize(img):
    img = cv2.equalizeHist(img)
    return img

def preprocessing(img):
    img = grayscale(img)
    img = equalize(img)
    img = img / 255
    return img

# Preprocess the images and log the progress
def preprocess_images(images, set_name):
    preprocessed_images = []
    for i, img in enumerate(images):
        logger.info(f"Preprocessing {set_name} image {i + 1}/{len(images)}")
        preprocessed_img = preprocessing(img)
        preprocessed_images.append(preprocessed_img)
    return np.array(preprocessed_images)

print("Preprocessing started for X_TRAIN")
X_train = preprocess_images(X_train, "training")
print("Preprocessing ended for X_TRAIN")

print("Preprocessing started for X_VALIDATION")
X_validation = preprocess_images(X_validation, "validation")
print("Preprocessing ended for X_VALIDATION")

print("Preprocessing started for X_TEST")
X_test = preprocess_images(X_test, "test")
print("Preprocessing ended for X_TEST")

print("Preprocessing Done")


# cv2.imshow("GrayScale Images",
#            X_train[random.randint(0, len(X_train) - 1)])
# cv2.waitKey(0)  # Wait indefinitely until a key is pressed
# cv2.destroyAllWindows()  # Close all OpenCV windows
# ----
# X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
# X_validation = X_validation.reshape(X_validation.shape[0], X_validation.shape[1], X_validation.shape[2], 1)
# X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)

# print("Reshape Done")

# dataGen = ImageDataGenerator(width_shift_range=0.1,
#                              # 0.1 = 10%     IF MORE THAN 1 E.G 10 THEN IT REFFERS TO NO. OF  PIXELS EG 10 PIXELS
#                              height_shift_range=0.1,
#                              zoom_range=0.2,  # 0.2 MEANS CAN GO FROM 0.8 TO 1.2
#                              shear_range=0.1,  # MAGNITUDE OF SHEAR ANGLE
#                              rotation_range=10)  # DEGREES

# dataGen.fit(X_train)

# batches = dataGen.flow(X_train, y_train,
#                        batch_size=20)
# X_batch, y_batch = next(batches)

# fig, axs = plt.subplots(1, 15, figsize=(20, 5))
# fig.tight_layout()

# for i in range(15):
#     axs[i].imshow(X_batch[i].reshape(imageDimesions[0], imageDimesions[1]))
#     axs[i].axis('off')
# plt.show()

y_train = to_categorical(y_train, noOfClasses)
y_validation = to_categorical(y_validation, noOfClasses)
y_test = to_categorical(y_test, noOfClasses)
# ----

# Reshape the images for PCA
X_train_flat = X_train.reshape(X_train.shape[0], -1)
X_validation_flat = X_validation.reshape(X_validation.shape[0], -1)
X_test_flat = X_test.reshape(X_test.shape[0], -1)

# Standardize the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_flat)
X_validation_scaled = scaler.transform(X_validation_flat)
X_test_scaled = scaler.transform(X_test_flat)

# Apply PCA
n_components = 100  # You can adjust this based on your dataset and computational resources
pca = PCA(n_components=n_components)
X_train_pca = pca.fit_transform(X_train_scaled)
X_validation_pca = pca.transform(X_validation_scaled)
X_test_pca = pca.transform(X_test_scaled)
# Modify your model to accept the reduced-dimensional data
def myModelPCA():
    no_Of_Nodes = 500
    model = Sequential()
    model.add(Dense(no_Of_Nodes, input_dim=n_components, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(noOfClasses, activation='softmax'))
    model.compile(Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model_pca = myModelPCA()

# Train the model with the reduced-dimensional data
history_pca = model_pca.fit(X_train_pca, y_train, epochs=epochs_val,
                             steps_per_epoch=len(X_train_pca) // batch_size_val,
                             batch_size=batch_size_val,
                             validation_data=(X_validation_pca, y_validation),
                             shuffle=1)

# Evaluate the model with PCA on the test set
score_pca = model_pca.evaluate(X_test_pca, y_test, verbose=0)
print('Test Score (with PCA):', score_pca[0])
print('Test Accuracy (with PCA):', score_pca[1])

# history = model.fit(X_train, y_train, epochs=epochs_val, steps_per_epoch=len(X_train)//batch_size_val, batch_size=batch_size_val,
#                     validation_data=(X_validation, y_validation), shuffle=1)

# STORE THE MODEL AS A PICKLE OBJECT
model_pca.save('faceshape_model_pca.h5')

print(model_pca.summary())

plt.figure(1)
plt.plot(history_pca.history['loss'])
plt.plot(history_pca.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('loss')
plt.xlabel('epoch')
plt.figure(2)
plt.plot(history_pca.history['accuracy'])
plt.plot(history_pca.history['val_accuracy'])
plt.legend(['training', 'validation'])
plt.title('Acurracy')
plt.xlabel('epoch')
plt.show()
score = model_pca.evaluate(X_test, y_test, verbose=0)
print('Test Score:', score[0])
print('Test Accuracy:', score[1])



cv2.waitKey(0)
