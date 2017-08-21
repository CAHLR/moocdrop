import numpy as np
from keras.utils import np_utils
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, LSTM, Activation, Masking
from keras.layers.wrappers import TimeDistributed

def load_keras_weights_from_disk(directory, model_name):
    """
    Loads model from disk, returns loaded model
    """
    with open(directory + "/" + model_name + ".json", 'r') as json_file:
        keras_model = model_from_json(json_file.readline())
    keras_model.load_weights(directory + "/" + model_name + "_weights.h5")
    keras_model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'])
    return keras_model
