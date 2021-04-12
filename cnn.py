import tensorflow as tf
import PIL
import numpy as np
import csv
from img import convert_to_bw

class CNNModel(tf.keras.Model):
    """
    Class representing a convoluted nerual network model
    """

    def __init__(self):
        super(CNNModel, self).__init__()

        self.conv1 = tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), padding='same', activation='relu')
        self.conv2 = tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu')
        self.norm1 = tf.keras.layers.BatchNormalization()
        self.maxpool1 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))
        self.dropout1 = tf.keras.layers.Dropout(0.3)

        self.conv3 = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), padding='same', activation='relu')
        self.conv4 = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu')
        self.norm2 = tf.keras.layers.BatchNormalization()
        self.maxpool2 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))
        self.dropout2 = tf.keras.layers.Dropout(0.3)

        self.conv5 = tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), padding='same', activation='relu')
        self.conv6 = tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu')
        self.norm3 = tf.keras.layers.BatchNormalization()
        self.maxpool3 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))
        self.dropout3 = tf.keras.layers.Dropout(0.3)

        self.conv7 = tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), activation='relu')
        self.norm4 = tf.keras.layers.BatchNormalization()
        self.maxpool4 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))
        self.flatten = tf.keras.layers.Flatten()
        self.dropout4 = tf.keras.layers.Dropout(0.3)

        self.dense1 = tf.keras.layers.Dense(21, name='char1', activation='softmax')
        self.dense2 = tf.keras.layers.Dense(21, name='char2', activation='softmax')
        self.dense3 = tf.keras.layers.Dense(21, name='char3', activation='softmax')
        self.dense4 = tf.keras.layers.Dense(21, name='char4', activation='softmax')
        self.dense5 = tf.keras.layers.Dense(21, name='char5', activation='softmax')
        self.dense6 = tf.keras.layers.Dense(21, name='char6', activation='softmax')

        
    def call(self, inputs):
        x = self.conv1(inputs)
        x = self.conv2(x)
        x = self.norm1(x)
        x = self.maxpool1(x)
        x = self.dropout1(x)

        x = self.conv3(x)
        x = self.conv4(x)
        x = self.norm2(x)
        x = self.maxpool2(x)
        x = self.dropout2(x)

        x = self.conv5(x)
        x = self.conv6(x) 
        x = self.norm3(x)
        x = self.maxpool3(x)
        x = self.dropout3(x)

        x = self.conv7(x)
        x = self.norm4(x)
        x = self.maxpool4(x)
        x = self.flatten(x)
        x = self.dropout4(x)

        x = [self.dense1(x), self.dense2(x), self.dense3(x), 
             self.dense4(x), self.dense5(x), self.dense6(x)]

        return x

def CompileModel():
    """
    Compile a CNN model, prints its structure to console and returns the model itself.
    """
    model = CNNModel()
    model.build((300, 48, 135, 1))
    model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
    model.summary()

    return model

def LoadData(image_path, label_path, first_img_n, last_img_n):
    """
    Load training and validation data, where images are converted to numpy arrays,
    and labels are converted to one-hot encodings. Prints the shape of data to console,
    and returns the data and the label as a tuple.
    """

    def ToOneHot(string):
        """
        Convert each character of a string to their one-hot encoding,
        return a list of the list of encoding for each character.
        """

        CHARACTERS = "345678bcdefghkmnprwxy"

        result = []
        for char in string:
            OneHot = [0 for _ in range(21)]
            index = CHARACTERS.index(char)
            OneHot[index] = 1
            result.append(OneHot)
        return result

    data = []
    for i in range(first_img_n, last_img_n + 1):
        data.append(convert_to_bw(image_path + str(i) + ".jpg"))
        #with PIL.Image.open(image_path + str(i) + ".jpg") as img:
        #    data.append(np.array(img) / 255.0)
    data = np.stack(data)
    data = data.reshape(last_img_n - first_img_n + 1, 48, 135, 1)

    with open(label_path, "r") as f:
        read_labels = [ToOneHot(row[1]) for row in csv.reader(f)][first_img_n - 1 : last_img_n]
    
    labels = [[] for _ in range(6)]
    for label in read_labels:
        for i in range(6):
            labels[i].append(label[i])
    labels = [array for array in np.asarray(labels)]

    print("Shape of data:", data.shape)

    return (data, labels)


def Callback(model, training_data, training_label, validation_data, validation_label, model_path="./model/bestmodel.h5"):
    checkpoint = tf.keras.callbacks.ModelCheckpoint(model_path, save_weights_only=False, monitor='val_output_6', verbose=1, save_best_only=False, mode='max')
    earlystop = tf.keras.callbacks.EarlyStopping(monitor='val_output_6', patience=5, verbose=1, mode='auto')
    tensorBoard = tf.keras.callbacks.TensorBoard(log_dir = "./logs", histogram_freq = 1)
    callbacks_list = [checkpoint, earlystop, tensorBoard]
    model.fit(training_data, training_label, batch_size=250, epochs=100, verbose=2, validation_data=(validation_data, validation_label), callbacks=callbacks_list)
    model.save()

if __name__ == "__main__":
    model = CompileModel()
    TrainingData, TrainingLabel = LoadData("./captcha/data_labeled/", "./captcha/trained.csv", 1, 250)
    ValidationData, ValidationLabel = LoadData("./captcha/data_labeled/", "./captcha/trained.csv", 251, 300)
    Callback(model, TrainingData, TrainingLabel, ValidationData, ValidationLabel)
