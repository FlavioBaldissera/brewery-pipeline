from datetime import datetime
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


BRONZE_PATH = "/opt/airflow/data_lake/bronze"
SILVER_PATH = "/opt/airflow/data_lake/silver"
GOLD_PATH = "/opt/airflow/data_lake/gold"


def transform_breweries():
    os.makedirs(SILVER_PATH, exist_ok=True)
    
    json_file = f"{BRONZE_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.json"
    parquet_file = f"{SILVER_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.parquet"

    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_file}")

    df = pd.read_json(json_file)

    required_columns = ["state", "brewery_type"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    df = df.dropna(subset=required_columns)
    df = df[df["state"].astype(str).str.strip() != ""]

    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    schema = pa.schema([
        ("id", pa.string()),
        ("name", pa.string()),
        ("brewery_type", pa.string()),
        ("address_1", pa.string()),
        ("address_2", pa.string()),
        ("address_3", pa.string()),
        ("city", pa.string()),
        ("state_province", pa.string()),
        ("postal_code", pa.string()),
        ("country", pa.string()),
        ("longitude", pa.float64()),
        ("latitude", pa.float64()),
        ("phone", pa.string()),
        ("website_url", pa.string()),
        ("state", pa.string()),
        ("street", pa.string()),
    ])

    for field in schema.names:
        if field not in df.columns:
            df[field] = None

    df = df[schema.names]

    if df.empty:
        raise ValueError("DataFrame vazio após limpeza e validação. Nada será salvo.")

    for state, group in df.groupby("state"):
        path = os.path.join(parquet_file, f"state={state}")
        os.makedirs(path, exist_ok=True)

        try:
            table = pa.Table.from_pandas(group, schema=schema, preserve_index=False)
            pq.write_table(table, os.path.join(path, "breweries.parquet"))
        except Exception as e:
            print(f"Erro ao salvar dados para o estado '{state}': {e}")


def transform_breweries_gold():
    silver_path = f"{SILVER_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.parquet"
    gold_path = f"{GOLD_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.parquet"

    all_files = []
    for root, _, files in os.walk(silver_path):
        for file in files:
            if file.endswith(".parquet"):
                all_files.append(pd.read_parquet(os.path.join(root, file)))

    df = pd.concat(all_files)
    agg = df.groupby(["state", "brewery_type"]).size().reset_index(name="brewery_count")
    agg.to_parquet(gold_path, index=False)


def show_sample():
    from datetime import datetime
    import pandas as pd

    path = f"{GOLD_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.parquet"
    if os.path.exists(path):
        df = pd.read_parquet(path)
        print(df.head())
    else:
        print("Gold file not found.")