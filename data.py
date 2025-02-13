import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go

# Load the CSV file into a DataFrame
#change the location of data file as required
df = pd.read_csv('data.csv')

# Create a 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=df['x'],
    y=df['y'],
    z=df['z'],
    mode='markers',
    marker=dict(
        size=5,
        color=df['time'],  # Use time as color
        colorscale='Viridis',  # You can choose your preferred color scale
        opacity=0.8
    )
)])

# Add time bar
fig.update_layout(
    scene=dict(
        zaxis=dict(title='Z'),
        yaxis=dict(title='Y'),
        xaxis=dict(title='X')
    ),
    title='3D Scatter Plot with Time Bar',
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Time:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': [{'args': [[str(time)], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                   'label': str(time),
                   'method': 'animate'} for time in df['time']]
    }]
)

# Show the plot
fig.show()
