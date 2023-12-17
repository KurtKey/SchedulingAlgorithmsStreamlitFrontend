import plotly.figure_factory as ff
import streamlit as st

def gantt_chart(c):
    # Create a list to store the Gantt chart data
    gantt_data = []

    # Set a color for all tasks (e.g., blue)
    task_color = 'rgb(0, 0, 255)'

    # Iterate through the gantt_representation and create Gantt chart data
    current_time_slot = 0
    for task, duration in c:
        if task == 'Task No Task' or task == 'No Task':
            current_time_slot += duration
            continue  # Skip Task No Task
        gantt_data.append(
            dict(Task=task, Start=current_time_slot, Finish=current_time_slot + duration, Color=task_color))
        current_time_slot += duration

    # Create a Gantt chart figure
    fig = ff.create_gantt(
        gantt_data,
        show_colorbar=True,
        showgrid_y=True,
        showgrid_x=True,
        index_col='Task',
        group_tasks=True,
    )

    # # Add vertical lines to the chart for each value of the x-axis
    # for time_slot in range(0, current_time_slot + 1):
    #     fig.add_shape(
    #         dict(
    #             type='line',
    #             x0=time_slot,
    #             x1=time_slot,
    #             y0=0,
    #             y1=len(c),
    #             line=dict(color='black', width=0.2)
    #         )
    #     )

    fig.update_layout(
        title_text='Gantt Chart Representation',
        xaxis_title='Time Slots',
        yaxis_title='Tasks',
        xaxis_type='linear',
        xaxis=dict(range=[0, current_time_slot]),  # Set the range of x-axis
    )

    # Display the Gantt chart using Streamlit
    st.plotly_chart(fig)

# Example usage
#gantt_data = [('Task 1', 2), ('Task 2', 3), ('Task 3', 1)]
#gantt_chart(gantt_data)
