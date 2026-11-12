import pandas as pd
from sodapy import Socrata


def fetch_data(domain: str, dataset_id: str, limit: int) -> pd.DataFrame:
    """
    Fetch data from a Socrata API and return it as a pandas DataFrame.

    Parameters:
    domain (str): The domain of the Socrata API.

    Returns:
    pd.DataFrame: A DataFrame containing the fetched data.
    """
    client = Socrata(domain, None)  # No authentication needed for public datasets
    results = client.get(dataset_id, limit=limit)

    df = pd.DataFrame.from_records(results)

    return df


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
    dataframes = {}

    for city_name, config in datasets.items():
        print(f'=== Processing {city_name} ===')
        df = fetch_data(config['domain'], config['dataset_id'], limit=1000)
        dataframes[city_name] = df

        # Basic EDA inspection fulfilling project requirements
        print(f'{city_name} Dataset Dimensions: {df.shape[0]} rows, {df.shape[1]} columns')

        # Check for missing data
        missing_counts = df.isnull().sum()
        print(f'{city_name} Missing Data Summary (Top columns with nulls):')
        print(missing_counts[missing_counts > 0].head())


if __name__ == "__main__":
    main()