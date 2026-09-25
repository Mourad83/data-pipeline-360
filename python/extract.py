import pandas as pd

from config import LANDING_DIR


def get_sales_files():

    sales_files = sorted(
        LANDING_DIR.glob("sales_*.csv")
    )

    return sales_files


def read_sales_file(file_path):

    df = pd.read_csv(file_path)

    return df
