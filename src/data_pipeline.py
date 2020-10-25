import numpy as np
import pandas as pd
import scipy.stats as stats


def date_time_cols(df, date_cols):
    for col in date_cols:
        df[col] = pd.to_datetime(df[col]) 
        df[col] = pd.DatetimeIndex(df['date']).date
    return df

def remove_dups_within_day(df, groupby_cols, time_col, val_col):
    return df.groupby(groupby_cols).agg({val_col: 'mean'}).reset_index()

def create_num_visits(df, id_col):
    df['num_visit'] = df.groupby('patient_id').cumcount() + 1
    return df

def create_month_year_cols(df, date_col):
    df['month'] = pd.DatetimeIndex(df[date_col]).month
    df['year'] = pd.DatetimeIndex(df[date_col]).year
    df['month_year'] = pd.to_datetime(df[date_col]).dt.to_period('M')
    return df

def simulate_age_col(df, id_col):
    patients = pd.DataFrame(df[id_col].unique())
    patients.columns = [id_col]
    patients['simulated_age'] = stats.norm(loc = 30, scale = 5).rvs(len(patients)).astype(int)
    df = df.merge(patients)
    return df


def clean_dataframe(df, date_cols, groupby_cols, time_col, val_col, id_col, date_col, sim_age = True):
    df = date_time_cols(df, date_cols)
    df = remove_dups_within_day(df, groupby_cols, time_col, val_col)
    df = create_num_visits(df, id_col)
    df = create_month_year_cols(df, date_col) 
    if sim_age:
        df = simulate_age_col(df, id_col)
    return df


def create_pivot(df, index, columns, values):
    return df.pivot(index = index, columns = columns, values = values)


def get_diffs(df, index, columns, values, drop_null = True):
    diffs_pivot = create_pivot(df=df, index=index, columns=columns, values=values).diff()
    diffs_df = pd.DataFrame(diffs_pivot.unstack()).reset_index()
    #change column name
    diffs_df.columns = np.append(diffs_df.columns[:-1], 'delta_score')
    if drop_null:
        #note, null means they had their last visit already
        diffs_df = diffs_df.dropna().reset_index()
    return diffs_df

def merge_scores_and_diffs(left_df, right_df, left_on, right_on):
    return pd.merge(left_df, right_df, how = 'left', left_on=left_on, right_on=right_on)


def agg_into_series(df, groupby_col, agg_method, col_to_keep):
    return df.groupby(groupby_col).agg({col_to_keep: agg_method})


if __name__ == '__main__':
    date_cols = ['date', 'patient_date_created']
    groupby_cols = ['date', 'patient_id', 'patient_date_created']
    time_col = 'time'
    id_col = 'patient_id'
    val_col = 'score'
    date_col = 'date'


    raw = pd.read_csv('../data/phq_all_final.csv')

    # clean dataframe - remove duplicates, data types
    df = clean_dataframe(raw, date_cols, groupby_cols, 
                        time_col, val_col, id_col, 
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