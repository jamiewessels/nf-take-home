import numpy as np
import pandas as pd
import scipy.stats as stats


def date_time_cols(df, date_cols):
    """This function takes in a dataframe and an array of column names
        that should be in date format. Function changes columns types to
        datetime format


    Args:
        df (pandas DataFrame)
        date_cols (array): list of column names

    Returns:
        pandas DataFrame
    """
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]) 
        df[col] = pd.DatetimeIndex(df['date']).date
    return df

def remove_dups_within_day(df, groupby_cols, val_col):
    """Removes duplicates by setting value to the mean within each unique 
        patient_id-date combination

    Args:
        df (pandas DataFrame)
        groupby_cols (array): column names that when grouped together are the unique identifier
        val_col (string): column name for value to be aggregated

    Returns:
        pandas DataFrame: duplicates removed 
    """
    return df.groupby(groupby_cols).agg({val_col: 'mean'}).reset_index()

def create_num_visits(df, id_col):
    """Creates additional column that counts the visits for each patient

    Args:
        df (pandas DataFrame)
        id_col (string): column name for patient_id

    Returns:
        pandas DataFrame: column for num_visits added 
    """
    df['num_visit'] = df.groupby('patient_id').cumcount() + 1
    return df

def create_month_year_cols(df, date_col):
    """Creates a month-year column

    Args:
        df (pandas DataFrame)
        date_col (string): column name for date

    Returns:
        pandas DataFrame: column for month-date added 
    """
    df['month'] = pd.DatetimeIndex(df[date_col]).month
    df['year'] = pd.DatetimeIndex(df[date_col]).year
    df['month_year'] = pd.to_datetime(df[date_col]).dt.to_period('M')
    return df

def simulate_age_col(df, id_col):
    """Creates a new column for simulated ages of patients for each unique patient id
        Ages come from a normal distribution centered at 30, sigma of 5

    Args:
        df (pandas DataFrame)
        id_col (string): column name for patient_id

    Returns:
        pandas DataFrame: column for simulated age added
    """
    patients = pd.DataFrame(df[id_col].unique())
    patients.columns = [id_col]
    patients['simulated_age'] = stats.norm(loc = 30, scale = 5).rvs(len(patients)).astype(int)
    df = df.merge(patients)
    return df


def clean_dataframe(df, date_cols, groupby_cols, val_col, id_col, date_col, sim_age = True):
    """This function pulls all the above functions together in series
        and returns a dataframe without duplicates and the necessary columns for analysis.

    Args:
        df (pandas DataFrame)
        date_cols (array): list of column names
        groupby_cols (array): column names that when grouped together are the unique identifier
        val_col (string): column name for value to be aggregated
        id_col (string): column name for patient_id
        date_col (string): column name for date
        sim_age (bool, optional): If True, adds a simulated age column. Defaults to True.

    Returns:
        pandas DataFrame: cleaned, ready for analysis
    """
    df = date_time_cols(df, date_cols)
    df = remove_dups_within_day(df, groupby_cols, val_col)
    df = create_num_visits(df, id_col)
    df = create_month_year_cols(df, date_col) 
    if sim_age:
        df = simulate_age_col(df, id_col)
    return df


def create_pivot(df, index, columns, values):
    """Creates a pivot table with patient_ids as columns and scores as values.

    Args:
        df (pandas DataFrame)
        index (string): column name for num_visit
        columns (string): column name for patient_id
        values (string): column name for score

    Returns:
        pandas DataFrame
    """
    return df.pivot(index = index, columns = columns, values = values)


def get_diffs(df, index, columns, values, drop_null = True):
    """Returns a DataFrame with the score differences between each assessment for each patient.

    Args:
        df (pandas DataFrame)
        index (string): column name for num_visit
        columns (string): column name for patient_id
        values (string): column name for score
        drop_null (bool, optional): If True, dataFrame will not include null values. Defaults to True.

    Returns:
        pandas DataFrame
    """
    diffs_pivot = create_pivot(df=df, index=index, columns=columns, values=values).diff()
    diffs_df = pd.DataFrame(diffs_pivot.unstack()).reset_index()
    #change column name
    diffs_df.columns = np.append(diffs_df.columns[:-1], 'delta_score')
    if drop_null:
        #note, null means they had their last visit already
        diffs_df = diffs_df.dropna().reset_index()
    return diffs_df

def merge_scores_and_diffs(left_df, right_df, left_on, right_on):
    """Returns a DataFrame with both the score differences and the actual scores for each patient.

    Args:
        left_df (pandas DataFrame): DataFrame of the score differences
        right_df (pandas DataFRame): original DataFrame with actual scores
        left_on (array): list of column names from left_df to merge on
        right_on (array): list of column names from right_df to merge on

    Returns:
        pandas DataFrame
    """
    return pd.merge(left_df, right_df, how = 'left', left_on=left_on, right_on=right_on)


def agg_into_series(df, groupby_col, agg_method, col_to_keep):
    """Generates a series using groupby and an aggregation method

    Args:
        df (pandas DataFrame)
        groupby_col (string): column name for groupby 
        agg_method (string): aggregation method ('max', 'mean')
        col_to_keep (string): column name for aggregation

    Returns:
        pandas DataFrame
    """
    return df.groupby(groupby_col).agg({col_to_keep: agg_method})


if __name__ == '__main__':
    date_cols = ['date', 'patient_date_created']
    groupby_cols = ['date', 'patient_id', 'patient_date_created']
    id_col = 'patient_id'
    val_col = 'score'
    date_col = 'date'


    raw = pd.read_csv('../data/phq_all_final.csv')

    # clean dataframe - remove duplicates, data types
    df = clean_dataframe(raw, date_cols, groupby_cols, 
                        val_col, id_col, 
                        date_col)
    # df.to_csv('../data/phq_cleaned.csv')

    #dataframe showing score delta from previous visit
    diffs_df = get_diffs(df, index = 'num_visit', 
                        columns = 'patient_id', values = 'score')
    # diffs_df.to_csv('../data/phq_cleaned_score_diffs.csv')

    merged_df = merge_scores_and_diffs(df, diffs_df, 
                                left_on=['patient_id', 'num_visit'], 
                                right_on=['patient_id', 'num_visit'])
    # merged_df.to_csv('../data/phq_merged.csv')