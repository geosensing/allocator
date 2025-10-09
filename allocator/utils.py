from __future__ import annotations

import pandas as pd


def column_exists(df: pd.DataFrame, col: str) -> bool:
    """Check the column name exists in the DataFrame.

    Args:
        df: Pandas DataFrame.
        col: Column name.

    Returns:
        True if exists, False if not exists.
    """
    if col and (col not in df.columns):
        print(f"The specify column `{col}` not found in the input file")
        return False
    else:
        return True


def fixup_columns(cols: list[str | int]) -> list[str]:
    """Replace index location column to name with `col` prefix.

    Args:
        cols: List of original columns

    Returns:
        List of column names
    """
    out_cols = []
    for col in cols:
        if isinstance(col, int):
            out_cols.append(f'col{col:d}')
        else:
            out_cols.append(col)
    return out_cols
