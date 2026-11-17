import pandas as pd
from sodapy import Socrata

pd.set_option('display.max_columns', None)


def fetch_data(domain: str, dataset_id: str, limit: int, date: str) -> pd.DataFrame:
    """
    Fetch data from a Socrata API and return it as a pandas DataFrame.

    Parameters:
    domain (str): The domain of the Socrata API.

    Returns:
    pd.DataFrame: A DataFrame containing the fetched data.
    """
    client = Socrata(domain, None)  # No authentication needed for public datasets
    results = client.get(dataset_id, limit=limit, where=date)

    df = pd.DataFrame.from_records(results)

    return df


def data_standardization(df: pd.DataFrame, city_name: str) -> pd.DataFrame:
    """
    Standardize the Seattle dataset by renaming columns and converting data types.

    Parameters:
    df (pd.DataFrame): The original Seattle dataset.
    city_name (str): The name of the city.

    Returns:
    pd.DataFrame: The standardized Seattle dataset.
    """
    # Rename columns for consistency
    standard_df = df.copy()
    standard_columns = [ 
    'type', 
    'start date', 
    'end date', 
    'location', 
    'from intersection', 
    'to intersection'
    ]

    if city_name == 'Seattle':
        standard_df = standard_df[['permit_type', 'start_date', 'end_date',
                                   'street_on', 'street_from', 'street_to']]
        standard_df = standard_df.rename(columns={
            'permit_type': 'type',
            'street_on': 'location',
            'street_from': 'from intersection',
            'street_to': 'to intersection',
        })

    elif city_name == 'San_Francisco':
        standard_df = standard_df[['type', 'start_date', 'end_date',
                                   'street', 'from_st', 'to_st']]
        standard_df = standard_df.rename(columns={
            'type': 'type',
            'street': 'location',
            'from_st': 'from intersection',
            'to_st': 'to intersection',
        })
        
    standard_df['start date'] = pd.to_datetime(standard_df['start_date'])
    standard_df['end date'] = pd.to_datetime(standard_df['end_date'])
    standard_df = standard_df.drop(columns=['start_date', 'end_date'])
    standard_df = standard_df.reindex(columns=standard_columns)


    return standard_df


def data_dimensions(df: pd.DataFrame, name: str) -> None:
    """
    Print the dimensions of the DataFrame and check for missing data.
    """
    # Basic EDA inspection fulfilling project requirements
    print(f'{name} Dataset Dimensions: {df.shape[0]} rows, {df.shape[1]} columns')

    # Check for missing data
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df)) * 100
    missing_pct = missing_pct[missing_pct > 0]

    if missing_pct.empty:
        print(f'{name} has no missing data.')
    else:
        print(f'{name} Missing Data Percentage:')
        print(missing_pct)

    if 'city' in df.columns:
        per_city = df.isnull().groupby(df['city']).mean().mul(100)
        per_city = per_city.loc[:, (per_city > 0).any(axis=0)]
        if not per_city.empty:
            print(f'{name} Missing Data Percentage by city:')
            print(per_city)


def category_comparison(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Compare the specified category between Seattle and San Francisco datasets.

    Parameters:
    combined_df (pd.DataFrame): The combined DataFrame containing both datasets.
    category (str): The category to compare.

    Returns:
    pd.DataFrame: A DataFrame showing the comparison of the specified category.
    """
    if category not in df.columns:
        raise KeyError(f"'{category}' is not a column of the DataFrame")

    comparison_df = (df.groupby('city')[category]
                     .value_counts().unstack(level=0)
                     .fillna(0).astype(int))

    return comparison_df


def data_summary(df: pd.DataFrame, numeric1: str, numeric2: str) -> pd.DataFrame:
    """
    Print a summary of the DataFrame, including data types and basic statistics.
    Which are the seven-number summary
    """
    df = df.copy()

    df['duration hours'] = (df[numeric2] - df[numeric1]).dt.total_seconds() / 3600
    summary = df.groupby('city').describe()

    return summary


def main():
    datasets = {
        'Seattle': {
            'domain': 'data.seattle.gov',
            'dataset_id': 'ium9-iqtc'
        },
        'San_Francisco': {
            'domain': 'data.sf.gov',
            'dataset_id': '8x25-yybr'
        }
    }
    where_clause = "start_date >= '2025-01-01T00:00:00'"

    seattle_df = fetch_data(datasets['Seattle']['domain'],
                             datasets['Seattle']['dataset_id'], limit=100, date=where_clause)
    san_francisco_df = fetch_data(datasets['San_Francisco']['domain'],
                                  datasets['San_Francisco']['dataset_id'], limit=100, date=where_clause)

    seattle_df = data_standardization(seattle_df, 'Seattle')
    sf_df = data_standardization(san_francisco_df, 'San_Francisco')
    
    combined_df = pd.concat([seattle_df.assign(city='Seattle'),
                             sf_df.assign(city='San_Francisco')],
                             axis=0, ignore_index=True)

    # summary = data_summary(combined_df, 'start date', 'end date')
    # print(summary)
    # print(combined_df.head())
    print(data_dimensions(combined_df, 'Combined'))

if __name__ == "__main__":
    main()