from datetime import datetime

import pytz
import streamlit as st

from utils import store_match_to_blob


def app():
    # Define the timezone for Amsterdam
    timezone = pytz.timezone("Europe/Amsterdam")
    # Get the current date and time in the Amsterdam timezone and remove microseconds
    if "current_time_amsterdam" not in st.session_state:
        st.session_state["current_time_amsterdam"] = datetime.now(timezone).replace(
            microsecond=0
        )

    current_time_amsterdam = datetime.now(timezone).replace(microsecond=0)
    # Record Date and Time
    date = st.date_input("📅 Date", current_time_amsterdam.date())
    time = st.time_input("⏰ Time", value=current_time_amsterdam)
    date_time = datetime.combine(date, time)

    # Record Match
    st.subheader("🎾 Record Match")

    player1 = st.text_input("Player 1")
    player2 = st.text_input("Player 2")

    score1 = st.number_input(f"Score {player1 or 'Player 1'}", min_value=0, step=1)

    score2 = st.number_input(f"Score {player2 or 'Player 2'}", min_value=0, step=1)

    if st.button("Save Match"):
        try:
            st.write("Saving...")

            df = store_match_to_blob(
                date_time=date_time,
                player1=player1,
                player2=player2,
                score1=score1,
                score2=score2,
            )

            st.success("✅ Match recorded!")

            st.write(df.tail())

        except Exception as e:
            st.exception(e)
