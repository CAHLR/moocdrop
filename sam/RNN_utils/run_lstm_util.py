import numpy as np
import pickle
from keras.utils import np_utils
from keras.preprocessing import sequence
from keras.models import Sequential, model_from_json
from keras.layers import Dense, LSTM, Activation, Masking
from keras.layers.wrappers import TimeDistributed
import pandas as pd
import my_callback
import my_callback_custom_loss
from sklearn import metrics
from sklearn.model_selection import train_test_split


def create_model_from_courses(course_list, self_paced=False):    
    """Fits LSTM model based on the courses in the list course_list
    Trains the model on data prepared by collect_data_lstm
    """
    # course = 'RiceX-AdvBIO.5x-2016T1'
    for course in course_list:
        with open('course_users/' + course + '_users.pickle', 'rb') as f:
            df_local = pickle.load(f)
	#       df_list.append(df_local)
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
    event_list_binary = [np_utils.to_categorical(x, max_input_dim) for x in event_list]
    x_train = sequence.pad_sequences(event_list_binary, maxlen=max_seq_len, dtype='int32',
                                     padding='post', truncating='post')
    student_number = len(all_users)
    y = all_users['rseq'].apply(pd.Series).as_matrix()
    reshaped_y = np.reshape(y, (student_number,max_seq_len,1))
    
    #60:20:20
    train_data_x, test_data_x, train_data_y, test_data_y = train_test_split(x_train, reshaped_y, test_size=0.2, random_state=42)
    x_size = len(train_data_x)
    start_at = int(round(x_size*0.75))
    validation_data_x = train_data_x[start_at:]
    validation_data_y = train_data_y[start_at:]
    train_data_x = train_data_x[:start_at]
    train_data_y = train_data_y[:start_at]
    
    # prepare callback
    histories = my_callback.Histories()
    
    hidden_sizes = [200]
    dropout_Weights = [0.2]
    activation = ['sigmoid']
    epochs = [10]
    results = []
    #grid searched parameters chosen
    for hsize in hidden_sizes:
        for a_weight in dropout_Weights:
            for activation_function in activation:
                for epoch_number in epochs:
                    print ("training")
                    print ("current params: "+str(hsize)+" "+ str(a_weight)+" "+str(activation_function)+" "+str(epoch_number))
                    model = Sequential()
                    model.add(Masking(mask_value=0., input_shape=(max_seq_len, max_input_dim)))
                    model.add(LSTM(hsize, dropout_W=a_weight, return_sequences=True))
                    model.add(TimeDistributed(Dense(1)))
                    model.add(Activation(activation_function))
                    model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
                    big_model = model.fit(train_data_x, train_data_y, batch_size=64, epochs=epoch_number, validation_data=(validation_data_x,validation_data_y), callbacks=[histories])
                    end_indx = []
                    pred_x = model.predict(test_data_x)
                    for x in test_data_x:
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
                    for x in range(len(test_data_y)):
                        temp2 = test_data_y[x][0:end_indx[x]]
                        for each_x in temp2:
                            for number in each_x:
                                new_number = round(number)
                                ground_truth.append(new_number)
                    model_accuracy = metrics.accuracy_score(reliable_pred_x, ground_truth)
                    results.append({'params':{'hidden size':hsize,'dropout weight':a_weight,'activation fn':activation_function,'epoch #':epoch_number},'test_score':model_accuracy,'validation_average':np.mean(histories.val_acc),'roc':np.mean(histories.aucs)})
    with open('models/attr-results_sem_final.pickle', 'wb') as f:
            pickle.dump(results, f)  
    #compare test accuracy for tuning model
	#score = model.evaluate(test_data_x, test_data_y)
	#score = model.evaluate(test_data_x, test_data_y, verbose=0)
    return (model, big_model.history, histories.losses, histories.aucs)
    
# creates model for completion and certification
def create_model_from_courses_cert_completion(course_list, cert_or_comp, self_paced=False):    
    """Fits LSTM model based on the courses in the list course_list"""
    # course = 'RiceX-AdvBIO.5x-2016T1'
    df_list = []
    for course in course_list:
        with open('course_users/' + course + '_users.pickle', 'rb') as f:
            df_local = pickle.load(f)
    all_users = df_local
    if self_paced:
        max_seq_len = 13100  # Maximum sequence for input users
        max_input_dim = 78  # 77 event types, plus 1 for 0 screen
    else:
        max_seq_len = 7000
        max_input_dim = 88  # 77 event types, plus 10 week endings, plus 1 for 0 screen
    
    #if comp, add comp column to the dataset
    if cert_or_comp == "comp":
        f = pd.read_csv('completion_labels_BerkeleyX-CS169.2x-1T2016.csv')
        usernames = f.user_id.tolist()
        new_usernames = []
        for name in usernames:
            try:
                new_number = round(name)
            except:
                new_number=''
            new_name = 'username_'+str(new_number)
            new_usernames.append(new_name)
        values = f.completed.tolist()
        new_df = pd.DataFrame({'username':new_usernames,'completion':values})
        username_list = all_users.username.values
        y_included = new_df[new_df['username'].isin(username_list)]
        y_excluded = new_df[~new_df['username'].isin(username_list)]
        RESULT = pd.merge(all_users, y_included, right_on='username', left_on='username', how='outer',suffixes=('_orig', '_new'))
        all_users = RESULT
    
    # shuffle before getting values
    all_users.reset_index(drop=True, inplace=True)
    all_users = all_users.reindex(np.random.permutation(all_users.index))
    event_list = all_users['seq'].values
    event_list_binary = [np_utils.to_categorical(x, max_input_dim) for x in event_list]
    x_train = sequence.pad_sequences(event_list_binary, maxlen=max_seq_len, dtype='int32',
                                     padding='post', truncating='post')
    if cert_or_comp == "cert":
        student_number = len(all_users)
        y = (all_users['status'] == 'downloadable').astype(int).values
        y = np.reshape(y, (student_number, 1, 1))
        reshaped_y = np.broadcast_to(y, (student_number, max_seq_len, 1))
    else:
        student_number = len(all_users)
        y = (all_users['completion']).values
        y = np.reshape(y, (student_number, 1, 1))
        reshaped_y = np.broadcast_to(y, (student_number, max_seq_len, 1))
    
    #60:20:20
    train_data_x, test_data_x, train_data_y, test_data_y = train_test_split(x_train, reshaped_y, test_size=0.2, random_state=42)
    x_size = len(train_data_x)
    start_at = int(round(x_size*0.75))
    validation_data_x = train_data_x[start_at:]
    validation_data_y = train_data_y[start_at:]
    train_data_x = train_data_x[:start_at]
    train_data_y = train_data_y[:start_at]
    
    # prepare callback
    histories = my_callback_custom_loss.Histories()
    #comp model = {'dropout weight': 0.1, 'activation fn': 'sigmoid', 'epoch #': 10, 'hidden size': 200}
    #cert model = {'dropout weight': 0.2, 'activation fn': 'sigmoid', 'epoch #': 10, 'hidden size': 100}
    hidden_sizes = [200]
    dropout_Weights = [0.2]
    activation = ['sigmoid']
    epochs = [10]
    results = []
    #grid searched parameters chosen
    for hsize in hidden_sizes:
        for a_weight in dropout_Weights:
            for activation_function in activation:
                for epoch_number in epochs:
                    print ("training")
                    print ("current params: "+str(hsize)+" "+ str(a_weight)+" "+str(activation_function)+" "+str(epoch_number))
                    model = Sequential()
                    model.add(Masking(mask_value=0., input_shape=(max_seq_len, max_input_dim)))
                    model.add(LSTM(hsize, dropout_W=a_weight, return_sequences=True))
                    model.add(TimeDistributed(Dense(1)))
                    model.add(Activation(activation_function))
                    model.compile(loss='binary_crossentropy', optimizer='RMSprop', metrics=['accuracy'], sample_weight_mode='temporal')
                    big_model = model.fit(train_data_x, train_data_y, batch_size=64, epochs=epoch_number, validation_data=(validation_data_x,validation_data_y), callbacks=[histories])
                    end_indx = []
                    pred_x = model.predict(test_data_x)
                    for x in test_data_x:
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
                    for x in range(len(test_data_y)):
                        temp2 = test_data_y[x][0:end_indx[x]]
                        for each_x in temp2:
                            for number in each_x:
                                new_number = round(number)
                                ground_truth.append(new_number)
                    model_accuracy = metrics.accuracy_score(reliable_pred_x, ground_truth)
                    print (model_accuracy)
                    results.append({'params':{'hidden size':hsize,'dropout weight':a_weight,'activation fn':activation_function,'epoch #':epoch_number},'test_score':model_accuracy,'validation_average':np.mean(histories.val_acc)})
    with open('models/'+cert_or_comp+'-results_sem_final3.pickle', 'wb') as f:
            pickle.dump(results, f)  
    #compare test accuracy for tuning model
	#score = model.evaluate(test_data_x, test_data_y)
	#score = model.evaluate(test_data_x, test_data_y, verbose=0)
    print('model_accuracy ====', model_accuracy)
    return (model, big_model.history, model_accuracy)


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
    """trains models and stores aucs, history and model weights"""
    fold_df = pd.read_csv(fold_list_path)
    course_list = fold_df['course']
    keras_model, historyObject, losses, aucs= create_model_from_courses(course_list, self_paced)
    if self_paced:
        model_name = 'self_paced_'
    else:
        model_name = 'instructor_paced_attr'
    with open('models/results-aucs','w') as f:
        for item in aucs:
            f.write(str(aucs))
    with open('models/results-history','w') as f:
        for item in historyObject:
            f.write(str(item))
    print ("Saving weights to disk")
    save_keras_weights_to_disk(keras_model, 'models/paper_model', model_name)

def train_models_cert_comp(courses, cert_or_comp, self_paced=False):
    """trains models and stores score, history and model weights"""
    keras_model, historyObject, score = create_model_from_courses_cert_completion(courses,cert_or_comp, self_paced)
    if cert_or_comp == "cert" or cert_or_comp == "comp":
        if self_paced:
            model_name = 'self_paced_'
        else:
            model_name = 'instructor_paced_'+cert_or_comp
        with open('models/'+ cert_or_comp+'-results-score','w') as f:
            score_statement = "score = "+str(score)
            f.write(score_statement)
        with open('models/'+ cert_or_comp+'-results-history','w') as f:
            for item in historyObject:
                f.write(str(item))
        print ("Saving weights to disk")
        save_keras_weights_to_disk(keras_model, 'models/'+ cert_or_comp+'-paper_model', model_name)