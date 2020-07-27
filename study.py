import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import *
import datetime
from sklearn.model_selection import train_test_split

X = np.load("data/X2000-04-01-2020-04-01.npy")
Y = np.load("data/Y2000-04-01-2020-04-01.npy")
x_train, x_test, y_train, y_test = train_test_split(X, Y, random_state=42, train_size=0.9)


def Layers(data, mode, filters, kernel=None, bn=True, activation="relu", drop=None):
    if mode == "conv":
        x1 = Conv2D(filters, kernel)(data)
    elif mode == "dense":
        x1 = Dense(filters)(data)
    else:
        raise Exception("there is no mode")
    if bn:
        x1 = BatchNormalization()(x1)

    x1 = Activation(activation)(x1)
    if drop:
        x1 = Dropout(drop)(x1)
    return x1


inputs = Input(shape=(16, 10, 20))
x = Layers(inputs, "conv", 256, kernel=(1, 1), drop=0.5)
x = Layers(x, "conv", 256, kernel=(1, 1), drop=0.5)
x = Layers(x, "conv", 256, kernel=(1, 1), drop=0.5)
x = Layers(x, "conv", 512, kernel=(1, 10), drop=0.5)
x = Layers(x, "conv", 512, kernel=(1, 1), drop=0.5)
x = Layers(x, "conv", 1024, kernel=(16, 1), drop=0.5)

x = Flatten()(x)

x = Layers(x, "dense", 512, drop=0.5)
x = Layers(x, "dense", 512, drop=0.5)
x = Layers(x, "dense", 256, drop=0.5)
outputs = Layers(x, "dense", 16, activation="softmax", bn=False)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

model.compile(optimizer=tf.keras.optimizers.Nadam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.summary()

# model.load_weights("data/horse2020-07-26-10-26-21.h5")
history = model.fit(x_train, y_train, batch_size=16, epochs=100, validation_data=(x_test, y_test),
                    callbacks=tf.keras.callbacks.EarlyStopping(monitor="val_accuracy",
                                                               patience=5,
                                                               restore_best_weights=True))

now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
model.save(f"data/horse{now}.h5")
