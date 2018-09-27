import pandas as pd


def split_col(df, col_name, delimiter=","):
    """
    splits the given column of a dataframe by the given delimiter
    and creates for each entry from the split a separate row
    """
    # split column and stack it
    items = df[col_name].str.split(pat=delimiter).apply(
        pd.Series, "columns"
    ).stack()

    # drop index and rename series to column name
    items.index = items.index.droplevel(-1)
    items.name = col_name

    # remove old column and join split new column
    del df[col_name]
    df = df.join(pd.DataFrame(items))

    return df
