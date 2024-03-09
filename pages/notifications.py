import dash
from dash import html, dcc, callback, Input, Output, State
import dash_leaflet as dl
import json

from backend.helperfunctions import post_message, get_messages

dash.register_page(__name__)

cities = {
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Rome": {"lat": 41.9028, "lon": 12.4964}
}

gravity_options = [
    {'label': 'None', 'value': 'none'},
    {'label': 'Moderate', 'value': 'moderate'},
    {'label': 'Bad', 'value': 'bad'},
    {'label': 'Fatal', 'value': 'fatal'}
]

gravity_colors = {
    'none': 'green',
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
    dcc.Textarea(
        id='description-textarea',
        placeholder='Enter a detailed description of the situation...',
        style={'width': '100%', 'height': 100, 'margin-top': '10px'},
    ),
    html.Button('Submit', id='submit-btn', n_clicks=0, style={'margin-top': '10px'}),
    html.Div(id='output-div', style={'margin-top': '20px'}),
    dcc.Store(id='circles-store'),  # Store for keeping track of circles
    dcc.Store(id='selected-city')
])


@callback(
    Output('selected-city', 'data'),
    Input({'type': 'city-marker', 'index': dash.ALL}, 'n_clicks'),
    State({'type': 'city-marker', 'index': dash.ALL}, 'id'),
    prevent_initial_call=True
)
def handle_city_selection(n_clicks, ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    triggered_id_str = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_id = json.loads(triggered_id_str)
    selected_city = triggered_id['index']
    return selected_city


# Callback for updating the map based on the selected city, gravity, and range
@callback(
    [Output('marker-layer', 'children'), Output('circles-store', 'data')],
    [Input('submit-btn', 'n_clicks')],
    [State('selected-city', 'data'),
     State('title-input', 'value'),
     State('gravity-dropdown', 'value'),
     State('range-input', 'value'),
     State('description-input', 'value'),  # New description input state
     State('circles-store', 'data')],  # Add this to read the current circles
    prevent_initial_call=True
)
def update_map(n_clicks_submit, n_clicks_refresh, selected_city, title, gravity, range_km, description):
    if not selected_city or not gravity or not description:
        return dash.no_update, dash.no_update

    markers = [
        dl.Marker(
            position=(info["lat"], info["lon"]),
            children=[dl.Tooltip(city), dl.Popup(city)],
            id={"type": "city-marker", "index": city}
        ) for city, info in cities.items()
    ]

    # If submission was made, post the data
    if n_clicks_submit:
        post_message(selected_city, title, gravity, range_km, description)

    # Fetch messages to update circles
    messages = get_messages()
    circles = []
    for message in messages:
        if message['city'] in cities:
            city_info = cities[message['city']]
            circle = dl.Circle(
                center=(city_info["lat"], city_info["lon"]),
                radius=message['range_km'] * 1000,  # Assuming 'range_km' is stored in the database
                color=gravity_colors[message['gravity']],  # Assuming 'gravity' is stored in the database
                fill=True,
                fillOpacity=0.5
            )
            circles.append(circle)

    return markers + circles


@callback(
    Output('output-div', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('title-input', 'value'),
    State('disaster-dropdown', 'value'),
    State('selected-city', 'data'),
    prevent_initial_call=True
)
def submit_message(n_clicks, title, disaster, selected_city):
    if n_clicks > 0 and selected_city:
        return f"Submitted: {title}, Disaster: {disaster}, City: {selected_city}"
    return "Please select a city and fill out all fields before submitting."