import matplotlib.pyplot as plt
import pandas as pd
import os

from summarization import fetch_data


def monthly_counts(data: pd.DataFrame) -> pd.Series:
    """Count records by start month, including months with zero records."""
    counts = data['start date'].dt.month.value_counts()
    return counts.reindex(range(1, 13), fill_value=0)


def street_counts(data: pd.DataFrame) -> pd.Series:
    """Return the five most frequent street names and their counts."""
    return data['location'].value_counts().head(5)


def plot_months(data: pd.DataFrame, city: str, folder: str) -> None:
    """Save a bar chart of sampled closure records by start month."""
    counts = monthly_counts(data)
    fig, ax = plt.subplots()
    ax.bar(counts.index, counts.values)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel('Start month (1 = January)')
    ax.set_ylabel('Number of sampled records')
    ax.set_title(f'{city}: Closure start months in the 2026 sample')
    fig.tight_layout()

    output_folder = folder
    file_path = os.path.join(output_folder, f'{city}_months.png')
    fig.savefig(file_path)
    plt.close(fig)


def plot_streets(data: pd.DataFrame, city: str, folder: str) -> None:
    """Save a bar chart of the most frequent streets in the sample."""
    counts = street_counts(data)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(counts.index, counts.values)
    ax.invert_yaxis()
    ax.set_xlabel('Number of sampled records')
    ax.set_ylabel('Reported street')
    ax.set_title(f'{city}: Most frequent streets in the 2026 sample')
    fig.tight_layout()

    output_folder = folder
    file_path = os.path.join(output_folder, f'{city}_streets.png')
    fig.savefig(file_path)
    plt.close(fig)


def main() -> None:
    """Fetch up to 100 records per city with start dates during 2026."""
    dates = ("start_date >= '2026-01-01T00:00:00' AND "
             "start_date < '2027-01-01T00:00:00'")

    seattle = fetch_data('data.seattle.gov', 'ium9-iqtc', 100, dates)
    sf = fetch_data('data.sf.gov', '8x25-yybr', 100, dates)

    print(f'Seattle records returned: {len(seattle)}')
    print(f'San Francisco records returned: {len(sf)}')

    if seattle.empty or sf.empty:
        print('Both cities need 2026 records for this comparison.')
        return

    seattle = seattle.rename(columns={'street_on': 'location'})
    sf = sf.rename(columns={'street': 'location'})

    seattle['start date'] = pd.to_datetime(seattle['start_date'])
    sf['start date'] = pd.to_datetime(sf['start_date'])

    folder = 'visualization images'
    os.makedirs(folder, exist_ok=True)

    plot_months(seattle, 'Seattle', folder)
    plot_streets(seattle, 'Seattle', folder)
    plot_months(sf, 'San Francisco', folder)
    plot_streets(sf, 'San Francisco', folder)
    print('Saved all four charts.')


if __name__ == '__main__':
    main()