## Ensemble code
Before running feature creation, write a deadline file with `deadlines.py`.
Feature creation is found in `ensemble_features.py`.
Change the course names at the top of the file to analyze other courses.

Run `clean_ensemble_input.py` to write cleaned csv's from features.
The course name at the top must be changed for each file.

Run `run_ensemble.py`. Set test and train courses with `testdata` and `traindata`.

With results of `run_ensemble.py` in memory, you can combine output results with `combine_results.py`.


## RNN LSTM code
To collect data in the proper format for RNN anaysis, run `collect_data_lstm.py`
and it will write to one file per week of analysis called `week_1_data_courses.pickle`.
Change the filenames at the end to change the courses analyzed.

Run the LSTM with `run_lstm.py`. Change the courses analyzed by changing
`cross_sets` in that file.