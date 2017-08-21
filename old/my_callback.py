import keras
from sklearn.metrics import roc_auc_score

class Histories(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.aucs = []
        self.losses = []

    def on_train_end(self, logs={}):
        return

    def on_epoch_begin(self, epoch, logs={}):
        return

    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        y_pred = self.model.predict(self.validation_data[0])
        flat_list_true = []
        for sublist in self.validation_data[1]:
            for item in sublist:
                flat_list_true.append(item)
        flat_list_pred = []
        for sublist in y_pred:
            for item in sublist:
                flat_list_pred.append(item)
        self.aucs.append(roc_auc_score(flat_list_true, flat_list_pred))
        return

    def on_batch_begin(self, batch, logs={}):
        return

    def on_batch_end(self, batch, logs={}):
        return