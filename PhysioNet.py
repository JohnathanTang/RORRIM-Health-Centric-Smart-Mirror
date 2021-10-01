import wfdb
import pandas as pd

for i in range(1,21):
    record, _= wfdb.rdsamp('non_eeg/Subject'+str(i)+'_AccTempEDA')
    # annotation = wfdb.rdann('non_eeg/Subject10_SpO2HR','atr')
    pd.DataFrame(record).to_csv("S"+str(i)+"_ATE.csv")



