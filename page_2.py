from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import pytz
import streamlit as st

from utils import (
    calculate_standings,
    read_matches_from_blob,
)


def app():
    st.subheader("🏆 League Standings")

    matches = read_matches_from_blob()

    if matches.empty:
        st.info("No matches have been recorded yet.")
        return

    timezone = pytz.timezone("Europe/Amsterdam")

    # Date range filter
    st.subheader("Filter Match Results")

    start_date = st.date_input(
        "Start date",
        datetime.now(timezone).date() - timedelta(days=30),
    )

    end_date = st.date_input(
        "End date",
        datetime.now(timezone).date(),
    )

    if start_date > end_date:
        st.error("End date must be after start date.")
        return

    # Ensure datetime format
    matches["datetime"] = pd.to_datetime(matches["datetime"])

    # Filter matches
    filtered_matches = matches[
        (matches["datetime"].dt.date >= start_date)
        & (matches["datetime"].dt.date <= end_date)
    ]

    if filtered_matches.empty:
        st.warning("No matches found in selected period.")
        return

    # Standings
    st.subheader("🥇 Current Standings")

    standings = calculate_standings(filtered_matches)

    st.dataframe(
        standings,
        use_container_width=True,
        hide_index=True,
    )

    # Match count by player
    st.subheader("🎾 Matches Played")

    matches_played = {}

    for _, row in filtered_matches.iterrows():
        matches_played[row["player1"]] = (
            matches_played.get(row["player1"], 0) + 1
        )
        matches_played[row["player2"]] = (
            matches_played.get(row["player2"], 0) + 1
        )

    matches_played_df = pd.DataFrame(
        {
            "player": matches_played.keys(),
            "matches": matches_played.values(),
        }
    ).sort_values(
        by="matches",
        ascending=False,
    )

    fig_matches = px.bar(
        matches_played_df,
        x="player",
        y="matches",
        title="Matches Played",
        text="matches",
    )

    st.plotly_chart(fig_matches, use_container_width=True)

    # Wins chart
    st.subheader("🏅 Total Wins")

    fig_wins = px.bar(
        standings,
        x="player",
        y="wins",
        title="Wins by Player",
        text="wins",
    )

    st.plotly_chart(fig_wins, use_container_width=True)

    # Recent matches
    st.subheader("📜 Match History")

    display_matches = filtered_matches.sort_values(
        by="datetime",
        ascending=False,
    )

    st.dataframe(
        display_matches,
        use_container_width=True,
        hide_index=True,
    )