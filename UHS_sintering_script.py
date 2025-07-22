import time
import pandas as pd
import os
import plotly.graph_objects as go
import streamlit as st
import sys
import numpy as np

# Setup
st.set_page_config(
    page_title="EA Ramp Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔧 EA-PS 9080-100 1U UHS Sequence")
status = st.empty()
plot_placeholder = st.empty()

# State tracking
if "is_running" not in st.session_state:
    st.session_state["is_running"] = False
if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame(columns=["Time", "Set Voltage", "Measured Voltage", "Current", "Power"])
if "awaiting_filename" not in st.session_state:
    st.session_state["awaiting_filename"] = False


def ramp_voltage(start, stop, time, step_resolution=0.1):
    num_steps = int(time / step_resolution)
    array = np.linspace(start, stop, num=num_steps)
    return array.tolist()

def plot_voltage(n):
    df = pd.DataFrame(st.session_state.steps)
    voltage_array = []
    total_time = sum(df["step_time"]) * (int(n)+1)
    for a in range(int(n)+1):
        for i, row in df.iterrows():
            voltage_array = voltage_array + ramp_voltage(row["start_voltage"], row["final_voltage"], row["step_time"])
    time_array = np.linspace(0, total_time, len(voltage_array))
    fig = go.Figure()

    # Voltage on primary y-axis (left)
    fig.add_trace(go.Scatter(
        x=time_array, y=voltage_array,
        mode="lines", name="Voltage",
        line=dict(color="deepskyblue", width=4),  # Thicker line
        yaxis="y1"
    ))

    fig.update_layout(
        title="Selected Voltage Profile",
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent for dark mode
        paper_bgcolor="rgba(0, 0, 0, 0)",

        xaxis=dict(
            title=dict(text="Time (s)", font=dict(size=18, color="white")),
            tickfont=dict(size=14, color="white"),
            range=[0, max(time_array) * 1.01],
            showgrid=True,
            gridcolor="gray",
            showline=True,
            linecolor="white",
            mirror=True,
            zeroline=False
        ),

        yaxis=dict(  # Voltage axis (left)
            title=dict(text="Voltage (V)", font=dict(size=18, color="deepskyblue")),
            tickfont=dict(size=14, color="deepskyblue"),
            range=[0, 25],
            showgrid=True,
            gridcolor="gray",
            showline=True,
            linecolor="deepskyblue",
            zeroline=False
        )
    )

    plot_placeholder.plotly_chart(fig, use_container_width=True)


# Initialize session state for voltage steps
if "repeat_times" not in st.session_state:
    st.session_state.repeat_times = "0"  # or a sensible default like 1

if "steps" not in st.session_state:
    st.session_state.steps = []

if st.session_state.steps:
    plot_voltage(st.session_state.repeat_times)


# Sidebar inputs
with st.sidebar:
    col_add, col_refresh = st.columns([1, 1])

    with col_add:
        if st.button("➕ Add Voltage Step"):
            st.session_state.steps.append({
                "start_voltage": 0.0,
                "final_voltage": 5.0,
                "step_time": 10.0
            })

    with col_refresh:
        if st.button("📈 Refresh Graph"):
            st.rerun()

    # Render each step
    for i, step in enumerate(st.session_state.steps):
        try:
            title = f"**Step {i + 1}:** {step['start_voltage']} V → {step['final_voltage']} V in {step['step_time']} sec"
        except KeyError:
            title = f"🔧 Step #{i + 1}"

        with st.expander(title, expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                step["start_voltage"] = st.number_input(
                    f"Start V #{i+1}", value=step["start_voltage"], key=f"start_{i}"
                )
            with col2:
                step["final_voltage"] = st.number_input(
                    f"Final V #{i+1}", value=step["final_voltage"], key=f"final_{i}"
                )
            with col3:
                step["step_time"] = st.number_input(
                    f"Time #{i+1} (s)", value=step["step_time"], key=f"time_{i}"
                )

            # Remove button
            if st.button(f"🗑 Remove Step #{i+1}", key=f"remove_{i}"):
                st.session_state.steps.pop(i)
                st.rerun()

    st.text_input("Number of times to repeat: ", value="0", key="repeat_times")

    st.markdown("---")

    df = pd.DataFrame(st.session_state.steps)
    voltage_array = []
    step_resolution = 0.1

    # Build voltage array with repeats
    repeat_times = int(st.session_state.get("repeat_times", "0")) + 1
    for _ in range(repeat_times):
        for _, row in df.iterrows():
            voltage_array += ramp_voltage(row["start_voltage"], row["final_voltage"], row["step_time"], step_resolution)
    voltage_array.append(0)  # Final shutdown

    # Assemble CSV rows
    current = 80
    power = 2000
    timestep_ms = int(step_resolution * 1000)

    rows = []
    for i, volt in enumerate(voltage_array):
        rows.append({
            "Step": i + 1,
            "Description": f"Set PS U set= {volt:.3f}V Iset= {current:.3f}A output/input= on",
            "U set (V)": round(volt, 3),
            "I set (A)": current,
            "P set (W)": power,
            "Output/Input": "ON",
            "Hour": 0,
            "Minute": 0,
            "Second": 0,
            "Millisecond": timestep_ms,
            "R mode": "OFF",
            "R set": 1
        })

    output_df = pd.DataFrame(rows)
    csv_data = output_df.to_csv(sep=";", index=False).encode("utf-8")

    st.download_button(
        label="📥 Generate UHS Sequence",
        data=csv_data,
        file_name="uhs_sequence.csv",
        mime="text/csv"
    )

with st.sidebar:
    st.markdown("---")
    if st.button("💾 Download Config"):
        st.session_state["awaiting_filename"] = True

    if st.session_state["awaiting_filename"]:
        filename_input = st.text_input("Filename to download", value="ramp_config.csv", key="download_filename")
        df = pd.DataFrame(st.session_state.steps)
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Click to Download",
            data=csv_data,
            file_name=filename_input,
            mime="text/csv"
        )
        st.session_state["awaiting_filename"] = False

    st.markdown("---")

    uploaded_file = st.file_uploader("Upload Config CSV", type="csv", key="config_file")
    if uploaded_file is not None and st.button("📂 Load Uploaded Config"):
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.steps = df.to_dict(orient="records")  # Load into list of dicts
            st.success("Configuration loaded from uploaded file.")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading uploaded config: {e}")

