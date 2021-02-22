import pandas as pd
import ast 
from sklearn.preprocessing import MinMaxScaler

from app.config import DATASET_DIR,DATASET_RAW_NAME,DATASET_PREPROCESSED_NAME

# Since we use cosine similarity to recommend tracks all the features should have the same scale (0-1)
# List of numerical columns to scale using MinMaxscaler from sklearn
COLUMNS_TO_SCALE = [
    'acousticness', 
    'danceability', 
    'duration_ms', 
    'energy',
    'instrumentalness', 
    'key', 
    'liveness', 
    'loudness',
    'popularity', 
    'speechiness', 
    'tempo',
    'valence', 
    'year'
]

# List of columns that are irrelevant and need to be dropped
COLUMNS_TO_DROP = [
    'release_date'
]

# Column that needs to be converted from a string to a list
STRING_COLUMN_TO_LIST = 'artists'

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
    features = pd.read_csv(DATASET_DIR / DATASET_RAW_NAME)
    # Convert the artists column from string to list
    features = convert_string_to_list(features, STRING_COLUMN_TO_LIST)
    # Scale numerical columns
    features = scale_columns(features, COLUMNS_TO_SCALE)
    # Drop irrelevant columns
    features = drop_columns(features, COLUMNS_TO_DROP)
    # Save the preprocessed data
    features.to_csv(DATASET_DIR / DATASET_PREPROCESSED_NAME, index=False)