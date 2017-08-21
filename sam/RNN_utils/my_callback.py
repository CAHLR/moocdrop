#Callback for attrition model validation
import keras
from sklearn.metrics import roc_auc_score
import numpy as np
from sklearn import metrics

class Histories(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.aucs = []
        self.losses = []
        self.val_acc = []

    def on_train_end(self, logs={}):
        return

    def on_epoch_begin(self, epoch, logs={}):
        return

    def on_epoch_end(self, epoch, logs={}):
        max_seq_len = 7000
        max_input_dim = 88
        end_indx = []
        pred_x = self.model.predict(self.validation_data[0])
        for x in self.validation_data[0]:
            for i in range(max_seq_len):
                if np.sum(x[i]) == 0:
                    end_indx.append(i)
                    break
        reliable_pred_x = []
        ground_truth = []
        for i in range(len(pred_x)):
            temp = pred_x[i][0:end_indx[i]]
            for each_x in temp:
                for number in each_x:
                    new_number = round(number)
                    reliable_pred_x.append(new_number)
        for x in range(len(self.validation_data[1])):
            temp2 = self.validation_data[1][x][0:end_indx[x]]
            for each_x in temp2:
                for number in each_x:
                    new_number = round(number)
                    ground_truth.append(new_number)
        model_accuracy = metrics.accuracy_score(reliable_pred_x, ground_truth)
        self.val_acc.append(model_accuracy)
        self.aucs.append(roc_auc_score(ground_truth, reliable_pred_x))
        return

    def on_batch_begin(self, batch, logs={}):
        return

    def on_batch_end(self, batch, logs={}):
        return