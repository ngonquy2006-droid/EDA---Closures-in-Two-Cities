# Najat Alnuaimi
# CSE 163, Section AD
# Test the monthly and street counts used in the closure charts.

import pandas as pd

from visualization import monthly_counts, street_counts


def main() -> None:
    """Check monthly and street counts using four sample records."""
    data = pd.DataFrame({
        'start date': pd.to_datetime([
            '2026-01-01', '2026-01-03', '2026-03-01', '2026-12-01'
        ]),
        'location': ['Pine St', 'Pine St', None, 'Oak St']
    })

    expected_months = [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    assert monthly_counts(data).tolist() == expected_months
    assert street_counts(data).to_dict() == {'Pine St': 2, 'Oak St': 1}
    print('Visualization tests passed.')


if __name__ == '__main__':
    main()