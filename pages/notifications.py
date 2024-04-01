import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_leaflet as dl
import json

from backend.helperfunctions import post_message, get_messages, get_citiesAndMarkers, get_decisionResponses

dash.register_page(__name__)

cities = get_citiesAndMarkers()

data_for_buttons = get_decisionResponses()

gravity_options = [
    {'label': 'Minor', 'value': 'minor'},
    {'label': 'Moderate', 'value': 'moderate'},
    {'label': 'Bad', 'value': 'bad'},
    {'label': 'Fatal', 'value': 'fatal'}
]

gravity_colors = {
    'minor': 'green',
    'moderate': 'yellow',
    'bad': 'orange',
    'fatal': 'red'
}

disaster_options = [
    {'label': 'Earthquake', 'value': 'EARTHQUAKE'},
    {'label': 'Hurricane', 'value': 'HURRICANE'},
    {'label': 'Flood', 'value': 'FLOOD'},
    {'label': 'Pandemic', 'value': 'PANDEMIC'},
]

layout = html.Div([
    html.Div([  # Left Side
        dl.Map(center=[50, 10], zoom=4, children=[
            dl.TileLayer(),
            dl.LayerGroup(id="marker-layer", children=[
                dl.Marker(position=(info["lat"], info["lon"]), id={"type": "city-marker", "index": city}, children=[
                    dl.Tooltip(city),
                    dl.Popup(city),
                ]) for city, info in cities.items()
            ]),
        ], style={'width': '600px', 'height': '400px'}),
        dcc.Dropdown(id='disaster-dropdown', options=disaster_options, placeholder="Select a disaster type", style={'margin-top': '10px'}),
        dcc.Dropdown(id='gravity-dropdown', options=gravity_options, placeholder="Select the gravity of the situation", style={'margin-top': '10px'}),
        dcc.Input(id='title-input', type='text', placeholder='Title', style={'margin-top': '10px'}),
        dcc.Input(id='range-input', type='number', placeholder='Range in km (10-100)', min=10, max=100, step=10, value=50, style={'margin-top': '10px'}),
        dcc.Textarea(id='description-input', placeholder='Enter a detailed description of the situation...', style={'width': '100%', 'height': 100, 'margin-top': '10px'}),
        html.Button('Submit', id='submit-btn', n_clicks=0, style={'margin-top': '10px'}),
        html.Button('Update Map', id='update-map-btn', n_clicks=0, style={'margin-top': '10px'}),
        html.Div(id='output-div', style={'margin-top': '20px'}),
        dcc.Store(id='circles-store'),  # Store for keeping track of circles
        dcc.Store(id='selected-city')
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px'}),
    html.Div([  # Right Side
        html.Div([
            html.Button(data['city'],
                        id={'type': 'city-button', 'index': index},
                        className="mr-1",
                        style={'borderRadius': '50px',
                               'margin': '5px',
                               'backgroundColor': 'red' if data['state'] == 'ONGOING' else 'yellow',
                               'color': 'white' if data['state'] == 'ONGOING' else 'black'})
            for index, data in enumerate(data_for_buttons)
        ], style={'padding': '20px'}),
        html.Div(id='city-details', style={'margin-top': '20px'})  # Container for city details
    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'})
], style={'width': '100%', 'display': 'flex'})



@callback(
    [Output('selected-city', 'data'), Output('disaster-dropdown', 'value')],
    [Input({'type': 'city-marker', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'city-button', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'city-marker', 'index': dash.ALL}, 'id'),
     State({'type': 'city-button', 'index': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def unified_city_selection(city_marker_clicks, city_button_clicks, city_marker_ids, city_button_ids):
    triggered_id, trigger_value = callback_context.triggered[0]['prop_id'].split('.')
    index = json.loads(triggered_id)['index']

    # Determine the trigger source - map marker or button
    if 'city-marker' in triggered_id:
        # Map marker was clicked
        selected_city = city_marker_ids[index]  # Assuming this is the city name; adjust as necessary
        disaster_value = None  # Map click doesn't change the disaster dropdown
    elif 'city-button' in triggered_id:
        # City button was clicked
        selected_data = data_for_buttons[index]
        selected_city = selected_data['city']
        disaster_value = selected_data['disaster']
    else:
        return dash.no_update, dash.no_update

    return selected_city, disaster_value


# Callback for updating the map based on the selected city, gravity, and range
@callback(
    Output('marker-layer', 'children'),
    Input('update-map-btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_map(n_clicks):
    if n_clicks > 0:
        markers = [
            dl.Marker(
                position=(info["lat"], info["lon"]),
                children=[dl.Tooltip(city), dl.Popup(city)],
                id={"type": "city-marker", "index": city}
            ) for city, info in cities.items()
        ]

        # Fetch messages to update circles
        messages = get_messages()
        circles = []
        for message in messages:
            if message['city'] in cities:
                city_info = cities[message['city']]
                circle = dl.Circle(
                    center=(city_info["lat"], city_info["lon"]),
                    radius=message['range'] * 1000,  # Ensure 'range_km' matches the key in your message objects
                    color=gravity_colors[message['severity']],
                    # Ensure 'gravity' matches the key in your message objects
                    fill=True,
                    fillOpacity=0.5
                )
                circles.append(circle)

        return markers + circles
    return dash.no_update


@callback(
    Output('output-div', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('title-input', 'value'),
    State('disaster-dropdown', 'value'),
    State('description-input', 'value'),
    State('gravity-dropdown', 'value'),
    State('range-input', 'value'),
    State('selected-city', 'data'),
    prevent_initial_call=True
)
def submit_message(n_clicks, title, disaster, description, gravity, range_km, selected_city):
    if n_clicks > 0 and selected_city:
        color = gravity_colors.get(gravity, 'default_color')
        post_message(selected_city, title, gravity, range_km, description, color)
        return f"Submitted: {title}, Disaster: {disaster}, City: {selected_city}"
    return "Please select a city and fill out all fields before submitting."


