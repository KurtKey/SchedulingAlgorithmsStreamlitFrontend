# app.py
import requests
import streamlit as st
from gantt_chart_drawer import gantt_chart
import google.generativeai as genai

GOOGLE_API_KEY = 'YOUR_API_KEY'
api_url = "http://127.0.0.1:8000/schedule"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def fcfsOrSJF_page(algorithm):
    st.subheader(f"{algorithm} Scheduling Algorithm")
    st.subheader(f"Ask about {algorithm} :")
    # Text area for user input
    user_input = st.text_input("Enter your question:")
    # Button to trigger processing
    if st.button("Process"):
        result = model.generate_content(f"here is a question about the algorithm {algorithm}, {user_input}")
        st.text_area("Result:", result.text, height=200)
    st.subheader("Try it :")
    # Initialize the data in session state
    if "data" not in st.session_state:
        st.session_state["data"] = {
            "Task": [],
            "Burst Time": [],
            "Arrival Time": []
        }

    data = st.session_state["data"]

    with st.form("Input Data"):
        # Display the current data
        st.table(data)

        # Allow adding new rows
        new_burst_time = st.number_input("Enter Burst Time:")
        new_arrival_time = st.number_input("Enter Arrival Time:")
        add_button = st.form_submit_button("Add")

        if add_button:
            # Add new row to the data
            data["Task"].append("T" + str(len(st.session_state.data["Arrival Time"])))
            data["Burst Time"].append(new_burst_time)
            data["Arrival Time"].append(new_arrival_time)
            st.session_state["data"] = data

            # Update the displayed table
            st.table(data)

    if st.button(f"Run {algorithm}"):
        # Extract the lists of burst time and arrival time from the "data" dictionary
        tasks = st.session_state.data["Task"]
        burst_times = st.session_state.data["Burst Time"]
        arrival_times = st.session_state.data["Arrival Time"]

        # Create a list of dictionaries representing processes
        processes = [
            {"Process_ID": i + 1, "Task": i + 1, "Arrival_Time": arrival_times[i],
             "Burst_Time": burst_times[i], "Deadline": 0, "Period": 0}
            for i in range(len(burst_times))
        ]
        if algorithm == "First Come First Served (FCFS)":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)
        elif algorithm == "SJF Without Preemption":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)
        else:
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)

        st.subheader("Response :")
        st.text(f"waiting_times: {wts}, average_waiting_time: {awt}")
        gantt_chart(gantt_tab)


def dm_rm_edf_llf_page(algorithm):
    st.subheader(f"{algorithm} Scheduling Algorithm")
    st.subheader(f"Ask about {algorithm} :")
    # Text area for user input
    user_input = st.text_input("Enter your question:")
    # Button to trigger processing
    if st.button("Process"):
        result = model.generate_content(f"here is a question about the algorithm {algorithm}, {user_input}")
        st.text_area("Result:", result.text, height=200)
    st.subheader("Try it :")
    # Initialize the data in session state
    if "data" not in st.session_state:
        st.session_state["data"] = {
            "Task": [],
            "Arrival Time": [],
            "Burst Time": [],
            "Deadline": [],
            "Period": []
        }

    data = st.session_state["data"]

    with st.form("Input Data"):
        # Display the current data
        st.table(data)

        # Allow adding new rows
        new_arrival_time = st.number_input("Enter Arrival Time:")
        new_burst_time = st.number_input("Enter Burst Time:")
        new_deadline = st.number_input("Enter Deadline:")
        new_period = st.number_input("Enter Period:")
        add_button = st.form_submit_button("Add")

        if add_button:
            # Add new row to the data
            data["Task"].append("T" + str(len(st.session_state.data["Arrival Time"])))
            data["Arrival Time"].append(new_arrival_time)
            data["Burst Time"].append(new_burst_time)
            data["Deadline"].append(new_deadline)
            data["Period"].append(new_period)
            st.session_state["data"] = data  # Update session state

            # Update the displayed table
            st.table(data)

    if st.button(f"Run {algorithm}"):
        # Extract the lists of burst time and arrival time from the "data" dictionary
        tasks = st.session_state.data["Task"]
        arrival_times = st.session_state.data["Arrival Time"]
        burst_times = st.session_state.data["Burst Time"]
        deadlines = st.session_state.data["Deadline"]
        periods = st.session_state.data["Period"]

        # Create a list of dictionaries representing processes
        processes = [
            {"Process_ID": i + 1, "Task": i + 1, "Arrival_Time": arrival_times[i],
             "Burst_Time": burst_times[i], "Deadline": deadlines[i], "Period": periods[i]}
            for i in range(len(burst_times))
        ]
        if algorithm == "Rate Monotonic (RM)":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)
        elif algorithm == "Deadline Monotonic (DM)":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)
        elif algorithm == "Earliest Deadline First (EDF)":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)
        elif algorithm == "Least Laxity First (LLF)":
            wts, awt, cpu_utz, gantt_tab = send_request(algorithm, processes)

        st.subheader("Response :")
        if cpu_utz > 1:
            utilizationnote = f"{cpu_utz}, tasks are not schedulable"
        else:
            utilizationnote = f"{cpu_utz}, tasks are schedulable"
        st.text(f"CPU occupation : {utilizationnote}")
        gantt_chart(gantt_tab)


def send_request(algo, tasks):
    request_data = {
        "algorithm": algo,
        "table": tasks
    }

    try:
        response = requests.post(api_url, json=request_data)
        print(response.raise_for_status())
        result = response.json()
        # Extract values from the response
        wts = result['wts']
        awt = result['awt']
        cpu_utz = result['cpu_utz']
        gantt_tab = result['gantt']
        return wts, awt, cpu_utz, gantt_tab
    except requests.RequestException as e:
        print(f"Error during the request: {e}")
        return None  # Handle the error as needed


def main():
    st.title("Scheduling Algorithm Simulator")

    # Sidebar
    selected_algorithm = st.sidebar.selectbox("Select Scheduling Algorithm",
                                              ["Earliest Deadline First (EDF)", "First Come First Served (FCFS)", "SJF Without Preemption", "SJF With Preemption", "Deadline Monotonic (DM)",
                                               "Rate Monotonic (RM)", "Least Laxity First (LLF)"])

    # Main page content
    if selected_algorithm == "First Come First Served (FCFS)" or selected_algorithm == "SJF Without Preemption" or selected_algorithm == "SJF With Preemption":
        fcfsOrSJF_page(selected_algorithm)
    else:
        dm_rm_edf_llf_page(selected_algorithm)


if __name__ == "__main__":
    main()
