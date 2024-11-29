"""
Streamlit App for Cost Tracker (Open WebUI function) Data Visualization

This Streamlit application processes and visualizes cost data from a JSON file.
It generates plots for total tokens used and total costs by model and user.

Author: bgeneto
Version: 0.2.1
Date: 2024-11-29
"""

import datetime
import json
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache
def load_data(file: Any) -> Optional[List[Dict[str, Any]]]:
    """Load data from a JSON file.

    Args:
        file: A file-like object containing JSON data.

    Returns:
        A list of dictionaries with cost records if the JSON is valid, otherwise None.
    """
    try:
        data = json.load(file)
        return data
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON file.")
        return None


def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process the data by extracting the month, model, cost, and user.

    Args:
        data: A list of dictionaries containing cost records.

    Returns:
        A pandas DataFrame with processed data.
    """
    processed_data = []
    for record in data:
        timestamp = datetime.datetime.strptime(
            record["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        month = timestamp.strftime("%Y-%m")
        model = record["model"]
        cost = record["total_cost"]
        try:
            if isinstance(cost, str):
                cost = float(cost)
        except ValueError:
            st.error(f"Invalid cost value for model {model}.")
            continue
        total_tokens = record["input_tokens"] + record["output_tokens"]
        user = record["user"]
        processed_data.append(
            {
                "month": month,
                "model": model,
                "total_cost": cost,
                "user": user,
                "total_tokens": total_tokens,
            }
        )
    return pd.DataFrame(processed_data)


def plot_data(data: pd.DataFrame, month: str) -> None:
    """Plot the data for a specific month.

    Args:
        data: A pandas DataFrame containing processed data.
        month: A string representing the month to filter data.
    """
    month_data = data[data["month"] == month]

    if month_data.empty:
        st.error(f"No data available for {month}.")
        return

    # ---------------------------------
    # Model Usage Bar Plot (Total Tokens)
    # ---------------------------------
    month_data_models_tokens = (
        month_data.groupby("model")["total_tokens"].sum().reset_index()
    )
    month_data_models_tokens = month_data_models_tokens.sort_values(
        by="total_tokens", ascending=False
    ).head(10)
    fig_models_tokens = px.bar(
        month_data_models_tokens,
        x="model",
        y="total_tokens",
        title=f"Total Tokens Used for {month} by Model",
    )
    st.plotly_chart(fig_models_tokens, use_container_width=True)

    # ---------------------------------
    # Model Cost Bar Plot (Total Cost)
    # ---------------------------------
    month_data_models_cost = (
        month_data.groupby("model")["total_cost"].sum().reset_index()
    )
    month_data_models_cost = month_data_models_cost.sort_values(
        by="total_cost", ascending=False
    ).head(10)
    fig_models_cost = px.bar(
        month_data_models_cost,
        x="model",
        y="total_cost",
        title=f"Total Cost for {month} by Model",
    )
    st.plotly_chart(fig_models_cost, use_container_width=True)

    # ---------------------------------
    # User Cost Bar Plot (Total Cost)
    # ---------------------------------
    month_data_users = month_data.groupby("user")["total_cost"].sum().reset_index()
    month_data_users = month_data_users.sort_values(by="total_cost", ascending=False)
    month_data_users["total"] = month_data_users["total_cost"].sum()
    month_data_users = pd.concat(
        [
            month_data_users,
            pd.DataFrame(
                {"user": ["Total"], "total_cost": [month_data_users["total"].iloc[0]]}
            ),
        ]
    )
    fig_users = px.bar(
        month_data_users, x="user", y="total_cost", title=f"Cost for {month} by User"
    )
    st.plotly_chart(fig_users, use_container_width=True)

    # ---------------------------------
    # Collapsible DataFrames
    # ---------------------------------
    with st.expander("Show DataFrames"):
        st.subheader("Month Data")
        st.dataframe(month_data)
        st.subheader("Month Data Models Tokens")
        st.dataframe(month_data_models_tokens)
        st.subheader("Month Data Models Cost")
        st.dataframe(month_data_models_cost)
        st.subheader("Month Data Users")
        st.dataframe(month_data_users)


def main():
    st.set_page_config(layout="wide")
    st.title("Open Webui")
    st.subheader("Cost Tracker App", divider=False)
    st.page_link(
        "https://github.com/bgeneto/open-webui-cost-tracker/",
        label="App Home",
        icon="🏠",
    )
    file = st.file_uploader("Upload a JSON file", type=["json"])
    if file is not None:
        data = load_data(file)
        if data is not None:
            processed_data = process_data(data)
            months = processed_data["month"].unique()
            month = st.selectbox("Select a month", months)
            if st.button("Plot Data"):
                plot_data(processed_data, month)


if __name__ == "__main__":
    main()
