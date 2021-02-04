import pandas as pd
import ast 
from sklearn.preprocessing import MinMaxScaler

from config import config

def convert_string_to_list(df,column):
    '''Converts a string representation of a list to a python list'''
    df = df.copy()
    df[column] = df[column].apply(ast.literal_eval)
    return df

def scale_columns(df, columns_to_scale):
    """Scales the given list of columns to a 0-1 scale"""
    df = df.copy()
    scaler = MinMaxScaler()
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale].values)
    return df

def ohe(df,columns_to_encode):
    '''Performs one hot encoding on the given list of categorical columns'''
    for column in columns_to_encode:
        df = df.join(pd.get_dummies(df[column], prefix=column)).drop(column, axis=1)
    return df

def drop_columns(df,columns_to_drop):
    '''Drops the given list of columns from a dataframe'''
    df = df.copy()
    df = df.drop(columns_to_drop, axis=1)
    return df

if __name__=='__main__':
    # Data import
    features = pd.read_csv(config.DATASET_DIR / config.DATASET_RAW)
    # Convert the artists column from string to list
    features = convert_string_to_list(features, config.STRING_COLUMN_TO_LIST)
    # Scale numerical columns
    features = scale_columns(features, config.COLUMNS_TO_SCALE)
    # Drop irrelevant columns
    features = drop_columns(features, config.COLUMNS_TO_DROP)
    # Save the preprocessed data
    features.to_csv(config.DATASET_DIR / config.DATASET_PREPROCESSED_NAME, index=False)