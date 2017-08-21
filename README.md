# MOOC Dropout
This repo holds code analyzing MOOC dropout data from EdX
using both RNN LSTM and an ensemble of other machine learning models.

## Ensemble code
Before running feature creation, write a deadline file with `deadlines.py`.
Feature creation is found in `ensemble_features.py`.
Change the course names at the top of the file to analyze other courses.

Run `clean_ensemble_input.py` to write cleaned csv's from features.
The course name at the top must be changed for each file.

Run `run_ensemble.py`. Set test and train courses with `testdata` and `traindata`.

With results of `run_ensemble.py` in memory, you can combine output results with `combine_results.py`.


## RNN LSTM code
collect_data_lstm.py contains code for extraction of events from log to training and testing data
run_lstm_util contains helper functions that train the model and store weights.

To collect data in the proper format for RNN anaysis, import `collect_data_lstm.py`
and it will write users for training to `'course_users/' + course_name + '_users.pickle'`
and users for testing to `'course_users/' + course_name + '_users_full.pickle'`.
and run `'get_events_from_folder_name_generic'` for each course
and run `'get_event_streams_train'` to generate train data for certification model
and run `'get_event_streams_test'` to generate test data for certification model
and run `'attritionLabels'` to generate all data for attrition model

Tune the LSTM through `run_lstm_util.py`.
Run the LSTM through `run_lstm.py`.