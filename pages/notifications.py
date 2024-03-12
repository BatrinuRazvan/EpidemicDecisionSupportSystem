import dash
from dash import html, dcc, callback, Input, Output, State
import dash_leaflet as dl
import json

from backend.helperfunctions import post_message, get_messages, get_citiesAndMarkers

dash.register_page(__name__)

cities = get_citiesAndMarkers()

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
        id='description-input',
        placeholder='Enter a detailed description of the situation...',
        style={'width': '100%', 'height': 100, 'margin-top': '10px'},
    ),
    html.Button('Submit', id='submit-btn', n_clicks=0, style={'margin-top': '10px'}),
    html.Button('Update Map', id='update-map-btn', n_clicks=0, style={'margin-top': '10px'}),
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