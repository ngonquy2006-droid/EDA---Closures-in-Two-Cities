import pandas as pd 
import summarization
from pandas.testing import assert_frame_equal
import pytest

seattle_df = pd.DataFrame({
        'permit_type': ['Play Street', 'Farmers Market'],
        'start_date': ['2026-07-08', '2026-06-03'],
        'end_date': ['2027-01-03', '2027-06-02'],
        'street_on': ['INTERLAKE AVE N', 'BALLARD AVE NW'],
        'street_from': ['N 39TH ST', '20TH AVE NW'],
        'street_to': ['N 40TH ST', 'NW VERNON PL']
    })

san_francisco_df = pd.DataFrame({
        'type': ['Special Event', 'Special Traffic Permit'],
        'start_date': ['2027-02-07', '2026-11-18'],
        'end_date': ['2027-02-07', '2026-11-20'],
        'street': ['OAK ST', 'MISSION ST'],
        'from_st': ['OAK ACCESS RD', 'SAINT MARYS AVE'],
        'to_st': ['JOHN F KENNEDY DR', 'BOSWORTH ST']
    })

standardized_seattle = summarization.data_standardization(seattle_df, 'Seattle')
standardized_sf = summarization.data_standardization(san_francisco_df, 'San_Francisco')
combined_df = pd.concat([standardized_seattle.assign(city='Seattle'),
                             standardized_sf.assign(city='San_Francisco')],
                             axis=0, ignore_index=True)


def test_seattle_standardization(seattle_df: pd.DataFrame) -> None:
    """Test the data_standardization function for Seattle dataset."""
    standardized = summarization.data_standardization(seattle_df, 'Seattle')

    expected_columns = ['type', 'start date', 'end date', 'location',
                        'from intersection', 'to intersection']

    assert list(standardized.columns) == expected_columns
    assert pd.api.types.is_datetime64_any_dtype(standardized['start date'])
    assert pd.api.types.is_datetime64_any_dtype(standardized['end date'])
    assert len(standardized) == len(seattle_df)
    assert standardized.loc[0, 'type'] == 'Play Street'
    assert standardized.loc[0, 'location'] == 'INTERLAKE AVE N'


def test_sf_standardization(san_francisco_df: pd.DataFrame) -> None:
    """Test the data_standardization function for San Francisco dataset."""
    standardized = summarization.data_standardization(san_francisco_df, 'San_Francisco')

    expected_columns = ['type', 'start date', 'end date', 'location',
                        'from intersection', 'to intersection']

    assert list(standardized.columns) == expected_columns
    assert pd.api.types.is_datetime64_any_dtype(standardized['start date'])
    assert pd.api.types.is_datetime64_any_dtype(standardized['end date'])
    assert len(standardized) == len(san_francisco_df)
    assert standardized.loc[0, 'type'] == 'Special Event'
    assert standardized.loc[0, 'location'] == 'OAK ST'


def test_category_comparison(combined_df: pd.DataFrame) -> None:
    """Test that the 'type' column has the expected unique values."""
    comparison_df = summarization.category_comparison(combined_df, 'type')

    assert 'Seattle' in comparison_df.columns
    assert 'San_Francisco' in comparison_df.columns
    assert comparison_df.loc['Play Street', 'Seattle'] == 1
    assert comparison_df.loc['Play Street', 'San_Francisco'] == 0
    assert comparison_df.loc['Special Event', 'San_Francisco'] == 1
    assert comparison_df.loc['Special Event', 'Seattle'] == 0


def test_data_summary(combined_df: pd.DataFrame) -> None:
    """Test that the data_summary function returns a DataFrame with expected statistics."""
    summary_df = summarization.data_summary(combined_df, 'start date', 'end date')
    expected_stats = {'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'}

    assert isinstance(summary_df.columns, pd.MultiIndex)
    assert len(summary_df.columns) == len(expected_stats)
    assert set(summary_df.columns.get_level_values(0)) == {'duration hours'}
    assert set(summary_df.columns.get_level_values(1)) == expected_stats

    seattle_mean = summary_df.loc['Seattle', ('duration hours', 'mean')]
    assert seattle_mean == pytest.approx(6516.0)
    sf_mean = summary_df.loc['San_Francisco', ('duration hours', 'mean')]
    assert sf_mean == pytest.approx(24.0)

    seattle_min = summary_df.loc['Seattle', ('duration hours', 'min')]
    seattle_max = summary_df.loc['Seattle', ('duration hours', 'max')]
    assert seattle_min == pytest.approx(4296.0)
    assert seattle_max == pytest.approx(8736.0)

    sf_min = summary_df.loc['San_Francisco', ('duration hours', 'min')]
    sf_max = summary_df.loc['San_Francisco', ('duration hours', 'max')]
    assert sf_min == pytest.approx(0.0)
    assert sf_max == pytest.approx(48.0)

    assert summary_df.loc['Seattle', ('duration hours', 'count')] == len(standardized_seattle)
    assert summary_df.loc['San_Francisco', ('duration hours', 'count')] == len(standardized_sf)

    with pytest.raises(KeyError):
        summarization.data_summary(combined_df, 'begin date', 'end date')

def main():
    test_seattle_standardization(seattle_df)
    test_sf_standardization(san_francisco_df)
    test_category_comparison(combined_df)
    test_data_summary(combined_df)
    print("All tests passed.")
    

if __name__ == "__main__":
    main()