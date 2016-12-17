import pickle
import numpy as np
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Activation, Embedding
from keras.layers import LSTM
from keras.optimizers import RMSprop, Adagrad, Adam
import os
from sklearn import metrics

class MOOC_Keras_Model_binary(object):
    """

    """
    def __init__(self):
        """
        """
        self.keras_model = None
        self.X = None
        self.padded_y_windows = None
        self.y = None
        self.model_params = None
        self.model_histories = []
        self.embedding_vocab_size = None
        self.best_epoch = None
        self.previous_val_loss = []

    def import_data(self, X, y, additional_params = []):
        """
        """

    def set_model_name(self, name):
        if not self.model_params:
            print("WARNING: Create LSTM model before setting model name.")
            return -1
        self.model_name = name + self.model_params_to_string

    @property
    def model_params_to_string(self):
        mp = self.model_params
        return('_' + str(mp['layers']) + '_' + str(mp['lrate']) + '_' + str(mp['hidden_size']) +
            '_' + str(mp['opt']) + '_' + str(mp['e_size']) + '_' + str( mp['output_dim']) + '_' +
            str(mp['input_len']) + '_' + str(mp['embedding_vocab_size']))

    def create_lstm_model(self, layers, lrate, hidden_size, optimizer, input_len, embedding_size):
        """
        Returns a LSTM model
        """
        print('building a functional API model')

        self.model_params = {'layers': layers, 'lrate': lrate, 'hidden_size': hidden_size, 'opt': optimizer, 'embedding_size': embedding_size}
        model = Sequential()
        model.add(Embedding(input_len + 1, embedding_size, mask_zero=True))
        for i in range(1, layers):
            model.add(LSTM(hidden_size, dropout_W=0.2, return_sequences=True))
        model.add(LSTM(hidden_size, dropout_W=0.2))  # from https://github.com/fchollet/keras/blob/master/examples/imdb_lstm.py
        model.add(Dense(1))
        model.add(Activation('sigmoid'))
        opt = optimizer(lr = lrate)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy']) # shuffle = False
        self.keras_model = model
        return model

    def load_keras_weights_from_disk(self, save_models_to_folder, model_name):
        """
        Loads from disk to self.keras_model
        """
        with open(save_models_to_folder + "/" + model_name + ".json", 'r') as json_file:
            self.keras_model = model_from_json(json_file.readline())
        self.keras_model.load_weights(save_models_to_folder + "/" + model_name + "_weights.h5")
        optimizer = self.model_params['opt']
        opt = optimizer(lr = self.model_params['lrate'])
        self.keras_model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])


    def save_keras_weights_to_disk(self, save_models_to_folder, model_name):
        """
        Saves self.keras_model json and weights to disk in save_models_to_folder named with model_name
        """
        model_json = self.keras_model.to_json()
        with open(save_models_to_folder + "/" + model_name + ".json", 'w') as json_file:
            json_file.write(model_json)
        self.keras_model.save_weights(save_models_to_folder + "/" + model_name + "_weights.h5")


    def early_stopping_model_fit(self, train_x, train_y, validation_data, epoch_limit = 200, loss_nonimprove_limit = 3, batch_size = 64, save_models_to_folder = None):
        """
        """
        early_stopping_met = False
        for i in range(epoch_limit):
            print("epoch:", i)
            current_history = self.keras_model.fit(train_x, train_y, batch_size = batch_size, nb_epoch = 1, validation_data = validation_data)
            current_history = current_history.history
            validation_loss = current_history['val_loss'][0]
            model_json = self.keras_model.to_json()
            with open(save_models_to_folder + "/last_model.json", 'w') as json_file:
                json_file.write(model_json)
            self.keras_model.save_weights(save_models_to_folder + "/last_model_weights.h5")
            #self.keras_model.save(save_models_to_folder + "/best_model.h5")
            self.previous_val_loss.append(validation_loss)
            if len(self.previous_val_loss) == 0:
                if save_models_to_folder is not None:
                    self.save_keras_weights_to_disk(save_models_to_folder, "best_model")
            else:
                min_val_loss = min(self.previous_val_loss)
                if validation_loss == min_val_loss:
                    self.best_epoch = i
                    if save_models_to_folder is not None:
                        self.save_keras_weights_to_disk(save_models_to_folder, "best_model")
            if len(self.previous_val_loss) > loss_nonimprove_limit:
                min_val_loss = min(self.previous_val_loss)
                recent_losses = self.previous_val_loss[-loss_nonimprove_limit-1:]
                print(recent_losses)
                if min(recent_losses) > min_val_loss:
                    early_stopping_met = True
            if early_stopping_met:
                print("Early stopping reached.")
                print("Best epoch according to validation loss:", self.best_epoch)
                print("Best epoch's loss:", min_val_loss)
                return min_val_loss
        self.load_keras_weights_from_disk(save_models_to_folder, "best_model")
        return min_val_loss

    def epoch_num_model_fit(self, train_x, train_y, epoch_limit = 5, batch_size = 64, save_models_to_folder = None):
        """
        """
        # early_stopping_met = False
        for i in range(epoch_limit):
            print("epoch:", i)
            current_history = self.keras_model.fit(train_x, train_y, batch_size = batch_size, nb_epoch = 1, validation_data = (train_x, train_y))
            current_history = current_history.history
            validation_loss = current_history['val_loss'][0]
            model_json = self.keras_model.to_json()
            with open(save_models_to_folder + "/last_model.json", 'w') as json_file:
                json_file.write(model_json)
            self.keras_model.save_weights(save_models_to_folder + "/last_model_weights.h5")
            #self.keras_model.save(save_models_to_folder + "/best_model.h5")
            self.previous_val_loss.append(validation_loss)
            if len(self.previous_val_loss) == 0:
                if save_models_to_folder is not None:
                    self.save_keras_weights_to_disk(save_models_to_folder, "best_model")
            else:
                min_val_loss = min(self.previous_val_loss)
                if validation_loss == min_val_loss:
                    self.best_epoch = i
                    if save_models_to_folder is not None:
                        self.save_keras_weights_to_disk(save_models_to_folder, "best_model")
            if len(self.previous_val_loss) > 0:
                min_val_loss = min(self.previous_val_loss)
        # self.load_keras_weights_from_disk(save_models_to_folder, "best_model")
        return min_val_loss


def normalize_sequence(x_full, x_train):
    # Normalize length of x_train to be as long as 99 percentile of x_full length
    # removing longest 1% of students
    length_list = [len(x) for x in x_full]
    length_list.sort()
    maxlen = length_list[int((len(length_list) - 1) * .99)] # 1716 events for first week
    print(len(x_train), 'sequences')
    # print(len(x_dev), 'dev sequences')

    print('Pad sequences (samples x time)')
    x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
    # x_dev = sequence.pad_sequences(x_dev, maxlen=maxlen)
    print('shape:', x_train.shape)
    # print('x_dev shape:', x_dev.shape)
    return(x_train)


MAX_EVENT_INDEX = 51  # Highest number in ce_types (RNN_event_list.csv)


# Does not include test set
cross_sets = [
    {
        'train_course_list': ["../ORDERED_DelftX_AE1110x_1T2014.log", "../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log"],
        'test_course_list': ["../ORDERED_DelftX_EX101x_1T2015.log"]
    },
    {
        'train_course_list': ["../ORDERED_DelftX_EX101x_1T2015.log", "../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log"],
        'test_course_list': ["../ORDERED_DelftX_AE1110x_1T2014.log"],
    },
    {
        'train_course_list': ["../ORDERED_DelftX_EX101x_1T2015.log", "../ORDERED_DelftX_AE1110x_1T2014.log"],
        'test_course_list': ["../ORDERED_BerkeleyX_Stat_2.1x_1T2014-events.log"],
    }
    ]
batch_size = 64
embedding_size_list = [MAX_EVENT_INDEX + 1]
hidden_size_list = [200]
optimizer_list = [RMSprop]
num_layers_list = [1]
lrate_list = [0.001]
results = []

for i, cross_set in enumerate(cross_sets):
    for week_num in range(1, 6):
        print("starting week:", str(week_num))
        with open('week_' + str(week_num) + '_data_courses.pickle', 'rb') as f:
            week_data = pickle.load(f)
        x_full = np.array([student for course in cross_set["train_course_list"] for student in week_data[course]['x_full']])
        y_full = np.array([student for course in cross_set["train_course_list"] for student in week_data[course]['y_full']])
        username_full = np.array([student + course for course in cross_set["train_course_list"] for student in week_data[course]['username_full']])

        num_passed = len(y_full) - y_full.sum()
        ############
        # Temp: select only twice as many dropouts as passing
        # mask to get even fail and not

        def is_in_username_used(x):
            return(x in username_used)

        # Use existing list of users if it is available
        user_file = "username_used_" + str(i) + ".pickle"
        if os.path.exists(user_file):
            with open(user_file, 'rb') as f:
                username_used = pickle.load(f)
            print("len username_full", len(username_full))
            use_indices = np.vectorize(is_in_username_used)(username_full)
            print(len(use_indices))
            print("sum use_indices", sum(use_indices))
            x_train = x_full[use_indices]
            y_train = y_full[use_indices]
        else:
            # Create list of usernames
            fail_mask = y_full.astype(bool)
            x_pass = x_full[~fail_mask]
            x_fail = x_full[fail_mask]
            y_pass = y_full[~fail_mask]
            y_fail = y_full[fail_mask]
            username_fail = username_full[fail_mask]
            use_indices = np.random.choice(len(username_fail), 2*num_passed)
            username_used = username_fail[use_indices].tolist() + username_full[~fail_mask].tolist()
            print("len use_indices", len(use_indices))
            print("len username_used", len(username_used))
            with open(user_file, 'wb') as f:
                pickle.dump(username_used, f)
            # create list with certification and twice as many dropouts
            x_train = x_pass.tolist() + x_fail[use_indices].tolist()
            y_train = y_pass.tolist() + y_fail[use_indices].tolist()
            #for x in x_full:
            #    x.insert(0, 52)
            x_train = np.array(x_train)
            y_train = np.array(y_train)
        ##############

        # randomize order
        p = np.random.permutation(len(x_train))
        x_train = x_train[p]
        y_train = y_train[p]

        # Get dev set
        # x_dev = np.array([student for course in dev_course_list for student in week_data[course]['x_full']])
        # y_dev = np.array([student for course in dev_course_list for student in week_data[course]['y_full']])

        # Get test set
        x_test = np.array([student for course in cross_set["test_course_list"] for student in week_data[course]['x_full']])
        y_test = np.array([student for course in cross_set["test_course_list"] for student in week_data[course]['y_full']])

        print("In train data,", len(y_train) - y_train.sum(), "passed")
        # print("In dev data,", len(y_dev) - y_dev.sum(), "passed")

        x_train = normalize_sequence(x_full, x_train)
        x_test = normalize_sequence(x_test, x_test)

        # Run code
        for embedding_size in embedding_size_list:
            for hidden_size in hidden_size_list:
                for optimizer in optimizer_list:
                    for num_layers in num_layers_list:
                        for lrate in lrate_list:
                            print('Train...')

                            print('week:', week_num, 'embedding_size:', embedding_size, 'hidden_size:', str(hidden_size),
                                'opt:', str(optimizer), 'num_layers:', str(num_layers),
                                'lrate:', str(lrate), 'fold_index:', str(i))
                            save_directory = "models/week" + str(week_num) + "/sem_final" + str(i)
                            if not os.path.exists(save_directory):
                                os.makedirs(save_directory)
                            binary_model = MOOC_Keras_Model_binary()
                            binary_model.create_lstm_model(num_layers, lrate, hidden_size, optimizer, MAX_EVENT_INDEX, embedding_size)
                            # score = binary_model.early_stopping_model_fit(x_train, y_train, validation_data = (x_dev, y_dev), epoch_limit=100,
                            #     batch_size=batch_size, save_models_to_folder=save_directory)
                            score = binary_model.epoch_num_model_fit(x_train, y_train, epoch_limit=5,
                                batch_size=batch_size, save_models_to_folder=save_directory)
                            best_epoch = binary_model.best_epoch
                            y_pred = binary_model.keras_model.predict(x_test)
                            roc_auc = metrics.roc_auc_score(y_test, y_pred)
                            print('ROC AUC:', roc_auc)
                            # print('Test score:', score)
                            # print('Test accuracy:', acc)
                            # model.save("models/" + str(embedding_size) + "_" + str(hidden_size) + "_" + str(optimizer) +
                            #     "_" + str(num_layers) + "_" + str(lrate) + ".model")
                            results.append({
                                # 'embedding_size': embedding_size,
                                # 'hidden_size': hidden_size,
                                # 'opt': str(optimizer),
                                # 'num_layers': num_layers,
                                # 'lrate': lrate,
                                'score': score,
                                'best_epoch': best_epoch,
                                'week': week_num,
                                'ROC AUC': roc_auc,
                                'fold_index': i})
                            with open('results_sem_final.pickle', 'wb') as f:
                                pickle.dump(results, f)

with open('results_sem_final.pickle', 'wb') as f:
    pickle.dump(results, f)
