import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import *
import datetime

X = np.load("data/X.npy")
Y = np.load("data/Y.npy")
x_train, x_test = X[:int(len(X)*0.8)], X[int(len(X)*0.8):]
y_train, y_test = Y[:int(len(Y)*0.8)], Y[int(len(Y)*0.8):]

model = tf.keras.models.Sequential()

model.add(Flatten())

model.add(Dense(1024))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.8))


model.add(Dense(256))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.8))

model.add(Dense(64))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5))

model.add(Dense(16, activation="softmax"))

model.compile(optimizer=tf.keras.optimizers.Nadam(learning_rate=0.0001),
              loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=16,
          epochs=500,
          validation_data=(x_test, y_test))

now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
model.save(f"data/horse{now}.h5")
