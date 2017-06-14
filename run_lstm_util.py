import numpy as np
import pickle
from keras.utils import np_utils
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, LSTM, Activation, Masking
from keras.layers.wrappers import TimeDistributed
import pandas as pd
from sklearn import metrics


def create_model_from_courses(course_list, self_paced=False):
    """Fits LSTM model based on the courses in the list course_list"""
    # course = 'RiceX-AdvBIO.5x-2016T1'
    df_local = pd.DataFrame({'A' : []})
    global df_local
    for course in course_list:
        with open('course_users/' + course + '_users.pickle', 'rb') as f:
            df_local = pickle.load(f)
#             df_list.append(df_local)
    all_users = df_local
    try:
        del all_users['status']
        del all_users['is_staff']
        del all_users['seq_len']
    except:
        pass
    
    #only for cs169
    for course in course_list:
        with open('course_attr/' + course + '_full_users.pickle', 'rb') as f:
            df_local = pd.DataFrame(pickle.load(f))
    new_y = df_local.rename(columns={0:'username',1:'rseq'})
    username_list = all_users.username.values #username list passed into x
    y_included = new_y[new_y['username'].isin(username_list)]
    y_excluded = new_y[~new_y['username'].isin(username_list)]
    RESULT = pd.merge(all_users, y_included, right_on='username', left_on='username', how='outer',suffixes=('_orig', '_new'))
    all_users = RESULT
    
    if self_paced:
        max_seq_len = 13100  # Maximum sequence for input users
        max_input_dim = 78  # 77 event types, plus 1 for 0 screen
    else:
        max_seq_len = 7000
        max_input_dim = 88  # 77 event types, plus 10 week endings, plus 1 for 0 screen

    # shuffle before getting values
    all_users.reset_index(drop=True, inplace=True)
    all_users.reindex(np.random.permutation(all_users.index))
    event_list = all_users['seq'].values
    # padded_event_list = sequence.pad_sequences(event_list, maxlen=max_seq_len, dtype='int32',
    #                                            padding='post', truncating='post')
    # weight_array = (padded_event_list != 0).astype(int)  # mask_zero replacement
    event_list_binary = [np_utils.to_categorical(x, max_input_dim) for x in event_list]
    x_train = sequence.pad_sequences(event_list_binary, maxlen=max_seq_len, dtype='int32',
                                     padding='post', truncating='post')                           
    student_number = len(all_users)
#     y = (all_users['status'] == 'downloadable').astype(int).values #11100000
    y = all_users['rseq'].apply(pd.Series).as_matrix()
    reshaped_y = np.reshape(y, (student_number,max_seq_len,1))

    model = Sequential()
    hidden_size = 100
    # input_dim is the number of categories
    # input_length is the length of each sequence
    model.add(Masking(mask_value=0., input_shape=(max_seq_len, max_input_dim)))
    model.add(LSTM(hidden_size, dropout_W=0.2, return_sequences=True))
    model.add(TimeDistributed(Dense(1)))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
    # 64 is batch size, 5 is epoch
    model.fit(np.array(x_train), reshaped_y, 64, 50)
    # out = model.predict(x_train)
    # with open('test_model_output.pickle', 'wb') as f:
    #     pickle.dump([out, x_train, y_repeat], f)
    return model


def save_keras_weights_to_disk(keras_model, save_models_to_folder, model_name):
    """
    Saves self.keras_model json and weights to disk in save_models_to_folder named with model_name
    """
    model_json = keras_model.to_json()
    with open(save_models_to_folder + "/" + model_name + ".json", 'w') as json_file:
        json_file.write(model_json)
    keras_model.save_weights(save_models_to_folder + "/" + model_name + "_weights.h5")


def load_keras_weights_from_disk(save_models_to_folder, model_name):
    """
    Loads model from disk, returns loaded model
    """
    with open(save_models_to_folder + "/" + model_name + ".json", 'r') as json_file:
        keras_model = model_from_json(json_file.readline())
    keras_model.load_weights(save_models_to_folder + "/" + model_name + "_weights.h5")
    keras_model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'])
    return keras_model


def train_cross_validation_models(fold_list_path, self_paced=False):
    """trains 5-folds of cross-validation based on the courses in the csv at fold_list_path"""
    fold_df = pd.read_csv(fold_list_path)
    for i in range(0, 5):
        # Skip courses with fold id
        course_list = fold_df['course'][fold_df['exclude_fold'] != i]
        keras_model = create_model_from_courses(course_list, self_paced)
        if self_paced:
            model_name = 'self_paced_' + str(i)
        else:
            model_name = 'instructor_paced_' + str(i)
        save_keras_weights_to_disk(keras_model, 'models/paper_model', model_name)


def calculate_auc_for_all():
    """Calculates AUC for all courses listed in instructor_paced_fold_list.csv"""
    course_df = pd.read_csv('instructor_paced_fold_list.csv')
    fold_groups = course_df.groupby('exclude_fold')
    result_list = []
    for fold, group in fold_groups:
        print('fold', fold)
        for course_name in group['course']:
            with open('course_users/' + course_name + '_users_full.pickle', 'rb') as f:
                user_df = pickle.load(f)
            keras_model = load_keras_weights_from_disk('models/paper_model', 'instructor_paced_' + str(fold) + '_100')
            max_seq_len = 7000
            max_input_dim = 88  # 77 event types, plus 10 week endings, plus 1 for 0 screen
            event_list_binary = [np_utils.to_categorical(x, max_input_dim) for x in user_df['seq'].tolist()]
            x = sequence.pad_sequences(event_list_binary, maxlen=max_seq_len, dtype='int32',
                                       padding='post', truncating='post')
            y_real = (user_df['status'] == 'downloadable').astype(int)
            out = keras_model.predict(x)
            prediction = out[:, -1, 0]
            user_df['y_pred'] = prediction
            user_df.to_csv('course_users/prediction/' + course_name + '_user_prediction.csv')
            score_per_week = []
            week_list = user_df['week'].unique()
            for i in week_list:
                score_per_week.append(metrics.roc_auc_score(y_real[user_df['week'] == i], prediction[user_df['week'] == i]))
            result_df = pd.DataFrame({'course': course_name, 'week': week_list, 'auc_score': score_per_week})
            result_list.append(result_df)
    return pd.concat(result_list)

# create_model_from_courses(['RiceX-AdvBIO.5x-2016T1', 'HKUSTx-EBA101x-1T2016'])
