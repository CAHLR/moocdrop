from run_lstm_util import train_models_cert_comp
from run_lstm_util import train_cross_validation_models

train_cross_validation_models('abridged_list.csv', self_paced=False)
train_models_cert_comp(['BerkeleyX-CS169.2x-1T2016'], "comp")
train_models_cert_comp(['BerkeleyX-CS169.2x-1T2016'], "cert")

#If running from a csv with lost of courses, can execute as follows:

# from feature_lstm import train_cross_validation_models
# train_models_attr('self_paced_fold_list.csv', self_paced=True)