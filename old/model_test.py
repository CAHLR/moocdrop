# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:52:54 2017

@author: smeyer

Example code for testing the model
"""
import numpy as np
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Activation, Embedding, Lambda, Masking
from keras.layers import LSTM
from keras.layers.wrappers import TimeDistributed
from keras.utils import np_utils
from keras.optimizers import RMSprop
from keras import backend as K

event_list = [
    [3,5,6,7, 8],
    [4,5,8,1],
    [2,3,7],
    [4],
    [1,4,6,7],
    [5,6,7,2],
    [1],
    [2],
    [3],
    [4]
]
# y = [0,1,0,1,0,1,0,1,0,1]
y = np.array([[[0], [0], [0]], [[1], [1], [1]]])
y = np.repeat(y, 5, axis=0)
print(y)

padded_event_list = sequence.pad_sequences(event_list, maxlen=3, dtype='int32',
    padding='post', truncating='post')
weight_array = padded_event_list != 0
event_list_binary = [np_utils.to_categorical(x, 9) for x in event_list]
print(event_list_binary)

x_train = sequence.pad_sequences(event_list_binary, maxlen=3, dtype='int32',
    padding='post', truncating='post')

#print(np_utils.to_categorical(x_train, 9))

print(x_train)

model = Sequential()
hidden_size = 100
# input_dim is the number of categories
# input_length is the length of each sequence
model.add(Masking(mask_value=0., input_shape=(3, 9)))
model.add(LSTM(hidden_size, dropout_W=0.2, return_sequences=True))  # , input_dim=9, input_length=3
model.add(TimeDistributed(Dense(1)))
# https://github.com/fchollet/keras/issues/2271
# time_distributed_merge_layer = Lambda(function=lambda x: K.mean(x, axis=1),
#                                       output_shape=lambda shape: (shape[0],) + shape[2:])
# model.add(time_distributed_merge_layer)
# model.add(Activation('sigmoid'))
# model.add(Dense(1))
model.add(Activation('sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
model.fit(x_train, np.array(y), 2, 10)