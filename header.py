import pandas as pd
from sodapy import Socrata


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


def standardize_data(df: pd.DataFrame, city_name: str) -> pd.DataFrame:
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

    if city_name == 'Seattle':
        standard_df = standard_df[['permit_type', 'start_date', 'end_date',
                                   'street_on', 'street_from', 'street_to']]
        standard_df = standard_df.rename(columns={
            'permit_type': 'type',
            'street_on': 'location',
            'street_from': 'from_intersection',
            'street_to': 'to_intersection',
        })
        standard_df['start_date'] = pd.to_datetime(standard_df['start_date'])
        standard_df['end_date'] = pd.to_datetime(standard_df['end_date'])
        standard_df.insert(0, 'city', city_name)

    elif city_name == 'San_Francisco':
        standard_df = standard_df[['type', 'start_dt', 'end_dt',
                                   'street', 'from_st', 'to_st']]
        standard_df = standard_df.rename(columns={
            'type': 'type',
            'street': 'location',
            'from_st': 'from_intersection',
            'to_st': 'to_intersection',
        })
        standard_df['start_date'] = pd.to_datetime(standard_df['start_dt'])
        standard_df['end_date'] = pd.to_datetime(standard_df['end_dt'])
        standard_df.insert(0, 'city', city_name)

    return standard_df


def data_dimensions(df: pd.DataFrame, city_name: str) -> None:
    # Basic EDA inspection fulfilling project requirements
    print(f'{city_name} Dataset Dimensions: {df.shape[0]} rows, {df.shape[1]} columns')

    # Check for missing data
    missing_counts = df.isnull().sum()
    missing_percentage = (missing_counts / len(df)) * 100
    
    print(f'{city_name} Missing Data Summary (Top columns with nulls):')
    print(missing_counts[missing_counts > 0].head())
    print(f'{city_name} Missing Data Percentage:')
    print(missing_percentage[missing_percentage > 0].head())


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

    for city_name, config in datasets.items():
        print(f'=== Processing {city_name} ===')
        df = fetch_data(config['domain'], config['dataset_id'], limit=100, date=where_clause)
        standardized_df = standardize_data(df, city_name)
        print(standardized_df.head())
        

if __name__ == "__main__":
    main()