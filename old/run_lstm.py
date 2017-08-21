from run_lstm_util import train_cross_validation_models
# from feature_lstm import train_cross_validation_models

# train_cross_validation_models('self_paced_fold_list.csv', self_paced=True)
train_cross_validation_models('instructor_paced_fold_list.csv', self_paced=False)
