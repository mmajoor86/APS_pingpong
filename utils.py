from datetime import datetime
from io import StringIO

import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient


# ============================================================
# Generic Blob Helpers
# ============================================================

def download_file_from_blob(blob_name: str) -> pd.DataFrame:
    """Download a CSV from Azure Blob Storage into a DataFrame."""

    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )

    blob_client = blob_service_client.get_blob_client(
        container=st.secrets["env"],
        blob=blob_name,
    )

    blob_data = blob_client.download_blob().readall()

    return pd.read_csv(StringIO(blob_data.decode("utf-8")))


def upload_dataframe_to_blob(
    df: pd.DataFrame,
    blob_name: str,
) -> None:
    """Upload a DataFrame to Azure Blob Storage."""

    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )

    blob_client = blob_service_client.get_blob_client(
        container=st.secrets["env"],
        blob=blob_name,
    )

    blob_client.upload_blob(
        df.to_csv(index=False),
        overwrite=True,
    )


# ============================================================
# Match Helpers
# ============================================================

MATCHES_FILE = "matches.csv"


def read_matches_from_blob() -> pd.DataFrame:
    """Read match history."""

    try:
        df = download_file_from_blob(MATCHES_FILE)

        if len(df) > 0:
            df["datetime"] = pd.to_datetime(df["datetime"])

        return df

    except Exception:
        return pd.DataFrame(
            columns=[
                "datetime",
                "player1",
                "player2",
                "score1",
                "score2",
            ]
        )


def store_match_to_blob(
    date_time: datetime,
    player1: str,
    player2: str,
    score1: int,
    score2: int,
) -> pd.DataFrame:
    """Append a match to matches.csv."""

    df_matches = read_matches_from_blob()

    new_match = pd.DataFrame(
        {
            "datetime": [date_time],
            "player1": [player1.lower()],
            "player2": [player2.lower()],
            "score1": [score1],
            "score2": [score2],
        }
    )

    df_matches = pd.concat(
        [df_matches, new_match],
        ignore_index=True,
    )

    df_matches["datetime"] = pd.to_datetime(
        df_matches["datetime"]
    )

    df_matches = df_matches.sort_values(
        by="datetime",
        ascending=False,
    )

    upload_dataframe_to_blob(
        df_matches,
        MATCHES_FILE,
    )

    return df_matches


# ============================================================
# Standings
# ============================================================

def calculate_standings(df_matches: pd.DataFrame) -> pd.DataFrame:

    standings = {}

    for _, row in df_matches.iterrows():

        p1 = row["player1"]
        p2 = row["player2"]

        standings.setdefault(
            p1,
            {"wins": 0, "losses": 0},
        )

        standings.setdefault(
            p2,
            {"wins": 0, "losses": 0},
        )

        if row["score1"] > row["score2"]:
            standings[p1]["wins"] += 1
            standings[p2]["losses"] += 1
        else:
            standings[p2]["wins"] += 1
            standings[p1]["losses"] += 1

    df = (
        pd.DataFrame.from_dict(
            standings,
            orient="index",
        )
        .reset_index()
        .rename(columns={"index": "player"})
    )

    if len(df) > 0:
        df["matches"] = df["wins"] + df["losses"]

        df["win_pct"] = (
            df["wins"] / df["matches"]
        ).round(3)

        df = df.sort_values(
            ["wins", "win_pct"],
            ascending=False,
        )

    return df