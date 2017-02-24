import numpy as np
import pickle
import random
from keras.utils import np_utils
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, LSTM, Activation, Masking
from keras.layers.wrappers import TimeDistributed
from keras.optimizers import RMSprop
import pandas as pd
from sklearn import metrics
from run_lstm_util import save_keras_weights_to_disk, load_keras_weights_from_disk

MAX_SEQ_LEN = 10

genpath = "/path_to_feature_files/new_cleaned_features/"
user_list_path = "/path_to_feature_files/course_users/"


def create_model_from_courses(course_list, fold_num, self_paced=False):
    # course = 'RiceX-AdvBIO.5x-2016T1'
    x_arr, y_arr, normalizations = get_arrs_for_course_list(course_list)

    # normalizations needed for testing later
    with open('feature_lstm_data_' + str(fold_num) + '.pickle', 'wb') as f:
        pickle.dump([x_arr, y_arr, normalizations], f)

    # all_users = pd.concat(df_list)
    if self_paced:
        # max_seq_len = 10
        max_input_dim = 78  # 77 event types, plus 1 for 0 screen
    else:
        max_input_dim = 12  # 12 features

    student_number = x_arr.shape[0]
    y = np.reshape(y_arr, (student_number, 1, 1))
    y_repeat = np.broadcast_to(y, (student_number, MAX_SEQ_LEN, 1))

    model = Sequential()
    hidden_size = 100
    # input_dim is the number of categories
    # input_length is the length of each sequence
    model.add(Masking(mask_value=0., input_shape=(MAX_SEQ_LEN, max_input_dim)))
    model.add(LSTM(hidden_size, dropout_W=0.2, return_sequences=True))
    model.add(TimeDistributed(Dense(1)))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
    model.fit(np.array(x_arr), y_repeat, 64, 5)
    # out = model.predict(x_train)
    # with open('test_model_output.pickle', 'wb') as f:
    #     pickle.dump([out, x_train, y_repeat], f)
    return model


def train_cross_validation_models(fold_list_path, self_paced=False):
    fold_df = pd.read_csv(fold_list_path)
    for i in range(0, 5):
        print('fold', i)
        course_list = fold_df['course'][fold_df['exclude_fold'] != i]
        keras_model = create_model_from_courses(course_list, i, self_paced)
        if self_paced:
            model_name = 'self_paced_' + str(i)
        else:
            model_name = 'instructor_paced_' + str(i)
        save_keras_weights_to_disk(keras_model, 'models/feature_lstm_model', model_name)


def get_arrs_for_course_list(course_list):
    df_list = [get_df_for_course(x) for x in course_list]
    all_df = pd.concat(df_list)

    normalizations = {}
    for i in range(1, 12):  # Intentionally skipping 12, which is already normalized
        feature = 'feature' + str(i)
        max_value = all_df[feature].max()
        min_value = all_df[feature].min()
        normalizations[feature] = {'min': min_value, 'max': max_value}
        if max_value == min_value:
            all_df[feature] = 0
        else:
            all_df[feature] = (all_df[feature] - min_value) / (max_value - min_value)
    all_users_list = []
    y_list = []
    for user_id, weeks_df in all_df.groupby('unique_id'):
        sorted_df = weeks_df.sort_values('week')
        user_arr = sorted_df[['feature1', 'feature2', 'feature3', 'feature4',
                              'feature5', 'feature6', 'feature7', 'feature8',
                              'feature9', 'feature10', 'feature11', 'feature12']].values
        all_users_list.append(user_arr)
        y_list.append(sorted_df['stopped'].iloc[0])  # All should be the same for each user
    print('y_list_unique', set(y_list))
    z = list(zip(all_users_list, y_list))
    random.shuffle(z)
    all_users_list[:], y_list[:] = zip(*z)
    x_arr = sequence.pad_sequences(all_users_list, maxlen=MAX_SEQ_LEN, dtype='float64',
                               padding='post', truncating='post')
    y_arr = (np.array(y_list) < 0.5).astype(int).astype(float)  # Switch to y meaning certification
    return x_arr, y_arr, normalizations


def get_df_for_course(course_name):
    return get_df_selected_users(course_name, '_users.pickle')


def get_df_selected_users(course_name, user_extension='_users.pickle'):
    feature_df = pd.read_csv(genpath + 'FEATURES_' + course_name + '.csv')
    feature_df['week'] = (feature_df['feature12'] / feature_df['feature12'].min()).round().astype(int)
    feature_df['username'] = 'username_' + feature_df['user_id'].astype(str)
    # merge with user.pickle to get correct users to train on
    with open(user_list_path + course_name + user_extension, 'rb') as f:
        user_df = pickle.load(f)
    user_list = set(user_df['username'])

    @np.vectorize
    def selected(x):
        return x in user_list
    feature_df = feature_df[selected(feature_df['username'])]
    feature_df['unique_id'] = course_name + feature_df['username'].astype(str)
    return feature_df


def calculate_auc_for_all():
    course_df = pd.read_csv('instructor_paced_fold_list.csv')
    fold_groups = course_df.groupby('exclude_fold')

    result_list = []
    for fold, group in fold_groups:
        print('fold', fold)
        with open('feature_lstm_data_' + str(fold) + '.pickle', 'rb') as f:
            [x_arr, y_arr, normalizations] = pickle.load(f)
        keras_model = load_keras_weights_from_disk('models/feature_lstm_model', 'instructor_paced_' + str(fold))
        for course_name in group['course']:
            feature_df = get_df_selected_users(course_name, '_users_full.pickle')

            for i in range(1, 12):  # Intentionally skipping 12, which is already normalized
                feature = 'feature' + str(i)
                max_value = normalizations[feature]['min']
                min_value = normalizations[feature]['max']
                if max_value == min_value:
                    feature_df[feature] = 0
                else:
                    feature_df[feature] = (feature_df[feature] - min_value) / (max_value - min_value)
            all_users_list = []
            y_list = []
            usernames = []
            for user_id, weeks_df in feature_df.groupby('unique_id'):
                sorted_df = weeks_df.sort_values('week')
                user_arr = sorted_df[['feature1', 'feature2', 'feature3', 'feature4',
                                      'feature5', 'feature6', 'feature7', 'feature8',
                                      'feature9', 'feature10', 'feature11', 'feature12']].values
                all_users_list.append(user_arr)
                y_list.append(sorted_df['stopped'].iloc[0])  # All should be the same for each user
                usernames.append(user_id)
            print('y_list_unique', set(y_list))
            x_arr = sequence.pad_sequences(all_users_list, maxlen=MAX_SEQ_LEN, dtype='float64',
                                           padding='post', truncating='post')

            out = keras_model.predict(x_arr)
            prediction_df = pd.DataFrame({'unique_id': np.repeat(usernames, out.shape[1]),
                                          'week': np.tile(range(1, 11), out.shape[0]),
                                          'prediction': out.flatten()})
            test_df = feature_df.merge(prediction_df, on=['unique_id', 'week'])
            test_df['certified'] = (test_df['stopped'] < 0.5).astype(int)
            test_df.to_csv('course_users/prediction/' + course_name + '_user_prediction_instructor_paced_feature_lstm.csv')
            score_per_week = []
            week_list = test_df['week'].unique()
            for i in week_list:
                score_per_week.append(metrics.roc_auc_score(test_df['stopped'][test_df['week'] == i], test_df['prediction'][test_df['week'] == i]))
            result_df = pd.DataFrame({'course': course_name, 'week': week_list, 'auc_score': score_per_week})
            result_list.append(result_df)
    return pd.concat(result_list)


# max_seq_len = 10
# max_input_dim = 12
# model = Sequential()
# hidden_size = 100
# # input_dim is the number of categories
# # input_length is the length of each sequence
# model.add(Masking(mask_value=0., input_shape=(max_seq_len, max_input_dim)))
# model.add(LSTM(hidden_size, dropout_W=0.2, return_sequences=True))
# model.add(TimeDistributed(Dense(1)))
# model.add(Activation('sigmoid'))
# model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
# model.fit(np.array(x_train), y_repeat, 64, 5)
# # out = model.predict(x_train)
# # with open('test_model_output.pickle', 'wb') as f:
# #     pickle.dump([out, x_train, y_repeat], f)
# #return model
