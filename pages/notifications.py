import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
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

capsule_wrapper_style = {
    'borderRadius': '50px',  # Rounded corners for the capsule shape
    'border': '1px solid #ccc',  # A light grey border
    'padding': '10px',  # Padding inside the capsule
    'margin': '5px 0',  # Margin around each capsule
    'display': 'flex',  # Use flexbox layout to align label and dropdown inline
    'flexDirection': 'row',  # Arrange items in a row
    'alignItems': 'center',  # Center items vertically within the capsule
    'justifyContent': 'space-between',  # Space out the label and dropdown
}

# Style for the dropdown within the capsule
capsule_dropdown_style = {
    'width': '70%',  # Dropdown takes 70% of the capsule's width
    'borderRadius': '20px',  # Slightly rounded corners for the dropdown itself
    'margin': '0',  # Remove default margin around the dropdown
}

left_side_style = {
    'width': '49%',
    'display': 'inline-block',
    'padding': '20px',
    'verticalAlign': 'top',
    'margin-right': '1%'  # Add some space between the left and right sides
}

button_style = {
    'backgroundColor': 'blue',  # A blue color from the Tesco scheme
    'border': 'none',
    'color': 'white',
    'padding': '10px 20px',
    'textAlign': 'center',
    'textDecoration': 'none',
    'display': 'block',  # Change to block for stacking
    'fontSize': '16px',
    'margin': '10px 0',  # Increased space between buttons
    'cursor': 'pointer',
    'borderRadius': '50px',  # Makes the buttons capsule-like
    'width': 'auto'  # Allows buttons to expand as text width
}

input_group_style = {
    'borderRadius': '50px',  # Rounded corners for the capsule shape
    'border': '1px solid #ccc',  # A light grey border
    'padding': '10px',  # Padding inside the wrapper
    'margin': '5px 0',  # Margin around each group
    'display': 'flex',  # Use flexbox layout
    'alignItems': 'center',  # Center items vertically
}

# Style for each input within the group
input_style = {
    'borderRadius': '20px',  # Slightly rounded corners for the inputs
    'margin': '0 10px',  # Margin around the inputs
    'flex': '1',  # Each input will flexibly fill the space
}

# Style for the vertical line separator
separator_style = {
    'borderLeft': '1px solid #ccc',  # A light grey line
    'height': '30px',  # Match the height of the inputs
    'margin': '0 10px',  # Spacing around the line
}

button_container_style = {
    'display': 'flex',  # Use flexbox layout to align items in a row
    'justifyContent': 'space-between',  # Space out the buttons
    'margin-bottom': '10px',  # Margin at the bottom of the button container
}

# Style for the description label
description_label_style = {
    'display': 'block',  # The label is a block element to allow for margin and centering
    'textAlign': 'center',  # Center the text
    'margin': '20px 0',  # Margin on top and bottom
    'fontSize': '20px',  # Larger font size
    'fontWeight': 'bold',  # Bold text
}

h2_style_top = {
    'textAlign': 'center',
    'width': '100%',
    'fontSize': '24px',
    'fontWeight': 'bold',
}

h2_style_half = {
    'textAlign': 'center',
    'width': '100%',
    'fontSize': '24px',
    'fontWeight': 'bold',
    'position': 'absolute',  # Absolute position within a relative container
    'top': '50%',  # Center at half the height of the container
    'left': '50%',  # Center horizontally
    'transform': 'translate(-50%, -50%)',  # Adjust the positioning
}

h2_style_details = {
    'textAlign': 'center',  # Center the text horizontally
    'width': '100%',  # Full width to ensure it's centered in the container
    'fontSize': '24px',  # Adjust font size as needed
    'fontFamily': 'Arial, sans-serif',  # More straightforward, non-handwritten font
    'fontWeight': 'bold',  # Bold font weight
    'marginBottom': '0',  # Remove bottom margin to bring it closer to the line
    'paddingBottom': '10px',  # Add some padding to lift it off from the line slightly
}

left_side_layout = html.Div([
    dl.Map(center=[50, 10], zoom=4, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="marker-layer", children=[
            dl.Marker(position=(info["lat"], info["lon"]),
                      id={"type": "city-marker", "index": city},
                      children=[dl.Tooltip(city), dl.Popup(city)]
                     ) for city, info in cities.items()
        ]),
    ], style={'width': '100%', 'height': '700px', 'margin-bottom': '20px'}),
    html.Div([
        html.Label('Disaster Type:', style={'margin-right': '10px'}),
        # Add some space between the label and the dropdown
        dcc.Dropdown(id='disaster-dropdown', options=disaster_options, placeholder="Select a disaster type",
                     style=capsule_dropdown_style),
    ], style=capsule_wrapper_style),
    html.Div([
        html.Label('Severity:', style={'margin-right': '10px'}),
        dcc.Dropdown(id='gravity-dropdown', options=gravity_options, placeholder="Select the gravity of the situation",
                     style=capsule_dropdown_style),
    ], style=capsule_wrapper_style),
    html.Div([
        html.Label('Title:', style={'margin-right': '10px'}),
        dcc.Input(id='title-input', type='text', placeholder='Title',
                  style=input_style),
        html.Div(style=separator_style),  # The vertical line separator
        html.Label('Range:', style={'margin-right': '10px'}),
        dcc.Input(id='range-input', type='number', placeholder='Range in km (10-100)',
                  min=10, max=100, step=10, value=50,
                  style=input_style),
    ], style=input_group_style),
    html.Label('Description:', style=description_label_style),
    dcc.Textarea(id='description-input', placeholder='Enter a detailed description of the situation...',
                 style={'width': '100%', 'height': 100}),
    html.Div([
        html.Button('Submit', id='submit-btn', n_clicks=0, style=button_style),
        html.Button('Update Map', id='update-map-btn', n_clicks=0, style=button_style),
    ], style=button_container_style),
    html.Div(id='output-div', style={'margin-top': '20px'}),
    dcc.Store(id='circles-store'),
    dcc.Store(id='selected-city')
], style=left_side_style)

right_side_style = {
    'width': '49%',
    'display': 'inline-block',
    'padding': '20px',
    'verticalAlign': 'top'
}


# Function to generate the button style, with optional parameter to make it red when active
def generate_button_style(is_active=False):
    return {
        'backgroundColor': 'red' if is_active else 'blue',  # Changed 'dark_blue' to 'blue' for consistency
        'border': 'none',
        'color': 'white',
        'padding': '10px 20px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'block',
        'fontSize': '16px',
        'margin': '10px 0',
        'cursor': 'pointer',
        'borderRadius': '50px',
        'width': '100%'
    }


right_side_layout = html.Div([
    # Upper Part - Incident Overview with Buttons
    html.Div([
        html.H2('Possible & Ongoing Incidents', style=h2_style_top),
        html.Hr(style={'marginBottom': '20px'}),  # Line under the title
        # Container for the buttons
        html.Div([
            html.Div([
                html.Button(f"{data['disaster']} - {data['city']}",
                            id={'type': 'disaster-button', 'index': data['city']},
                            n_clicks=0,
                            style=generate_button_style()),
                # Hidden div that will show the details when a button is clicked
                html.Div(
                    id={'type': 'details-container', 'index': data['city']},
                    style={'display': 'none'}
                )
            ]) for data in data_for_buttons
        ], id='disaster-buttons-container', style={'display': 'flex', 'flexDirection': 'column'}),
    ]),
    html.Div(style={'height': '35%'}),  # Adjust the height as needed to position the second H2

    # Lower Part - Details Section
    html.Div([
        html.H2('Details', style=h2_style_details),
        html.Hr(style={'marginBottom': '20px'}),  # Line under the title, directly below the "Details" H2
        html.Div(id='city-details', style={'marginTop': '20px'}),
        html.Div(id='description-section', style={'marginTop': '20px'})
    ]),
], style=right_side_style)

layout = html.Div([
    left_side_layout,
    html.Div(style={'width': '3px', 'backgroundColor': 'black'}),
    right_side_layout
], style={'width': '100%', 'display': 'flex', 'height': '100%', 'fontFamily': '"Arial", sans-serif'})

# layout = html.Div([
#     html.Div([  # Left Side
#         dl.Map(center=[50, 10], zoom=4, children=[
#             dl.TileLayer(),
#             dl.LayerGroup(id="marker-layer", children=[
#                 dl.Marker(position=(info["lat"], info["lon"]), id={"type": "city-marker", "index": city}, children=[
#                     dl.Tooltip(city),
#                     dl.Popup(city),
#                 ]) for city, info in cities.items()
#             ]),
#         ], style={'width': '100%x', 'height': '700px'}),
#         dcc.Dropdown(id='disaster-dropdown', options=disaster_options, placeholder="Select a disaster type", style={'margin-top': '10px'}),
#         dcc.Dropdown(id='gravity-dropdown', options=gravity_options, placeholder="Select the gravity of the situation", style={'margin-top': '10px'}),
#         dcc.Input(id='title-input', type='text', placeholder='Title', style={'margin-top': '10px'}),
#         dcc.Input(id='range-input', type='number', placeholder='Range in km (10-100)', min=10, max=100, step=10, value=50, style={'margin-top': '10px'}),
#         dcc.Textarea(id='description-input', placeholder='Enter a detailed description of the situation...', style={'width': '100%', 'height': 100, 'margin-top': '10px'}),
#         html.Button('Submit', id='submit-btn', n_clicks=0, style={'margin-top': '10px'}),
#         html.Button('Update Map', id='update-map-btn', n_clicks=0, style={'margin-top': '10px'}),
#         html.Div(id='output-div', style={'margin-top': '20px'}),
#         dcc.Store(id='circles-store'),  # Store for keeping track of circles
#         dcc.Store(id='selected-city')
#     ], style={'width': '49%', 'display': 'inline-block', 'padding': '20px', 'verticalAlign': 'top'}),
#
#     # Vertical Separator
#     html.Div(style={'width': '2px',  'backgroundColor': 'black'}),
#
#     # Right Side
#     html.Div([
#         html.Div([
#             html.Div([
#                 html.Button(
#                     f"{data['disaster']} - {data['city']}",
#                     id={'type': 'disaster-button', 'index': data['city']},
#                     n_clicks=0,
#                     style={
#                         'backgroundColor': gravity_colors.get(data.get('severity', 'default'), 'grey'),
#                         'border': 'none',
#                         'color': 'white',
#                         'padding': '10px 20px',
#                         'textAlign': 'center',
#                         'textDecoration': 'none',
#                         'display': 'block',  # Change to block for stacking
#                         'fontSize': '14px',
#                         'margin': '5px 0',  # Adjusted for spacing between buttons
#                         'cursor': 'pointer',
#                         'borderRadius': '20px',
#                         'width': '100%'  # Optional: Makes button full-width
#                     }
#                 ),
#                 html.Div(id={'type': 'details-container', 'index': data['city']}, style={'display': 'none', 'padding': '5px'})
#             ]) for data in data_for_buttons
#         ], id='disaster-buttons-container', style={'display': 'flex', 'flexDirection': 'column'}),
#         html.Div(id='city-details')  # Container for city details
#     ], style={'width': '49%', 'display': 'inline-block', 'padding': '20px', 'verticalAlign': 'top'})
# ], style={'width': '100%', 'display': 'flex', 'height': '100%'})


@callback(
    [Output({'type': 'disaster-button', 'index': dash.ALL}, 'style'),
     Output('description-section', 'children')],
    [Input({'type': 'disaster-button', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'disaster-button', 'index': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def update_button_styles_and_description(n_clicks, ids):
    ctx = callback_context
    triggered = ctx.triggered[0]['prop_id']

    if not triggered or triggered == '.':
        raise PreventUpdate

    try:
        button_id_json = json.loads(triggered.split('.')[0])
        triggered_index = button_id_json['index']
    except (ValueError, json.JSONDecodeError):
        raise PreventUpdate

    # Initialize all button styles to default and no description content
    button_styles = [generate_button_style(False) for _ in ids]
    description_content = None

    # Find the index of the clicked button
    for i, btn_id in enumerate(ids):
        if btn_id['index'] == triggered_index:
            # Change style for the clicked button
            button_styles[i] = generate_button_style(True)
            # Assuming you have data matching the button index to extract details
            selected_data = next((item for item in data_for_buttons if item['city'] == triggered_index), None)
            if selected_data:
                # Set description content for the clicked button
                description_content = html.Div([
                    html.H4(f"City: {selected_data['city']}"),
                    html.P(f"Disaster: {selected_data['disaster']}"),
                    html.P(f"State: {selected_data['state']}"),
                    # Add more details as needed
                ])
            break

    return button_styles, description_content


@callback(
    [Output('selected-city', 'data'), Output('city-details', 'children'), Output('disaster-dropdown', 'value')],
    [Input({'type': 'disaster-button', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'city-marker', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'disaster-button', 'index': dash.ALL}, 'id'),
     State({'type': 'city-marker', 'index': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def update_city_details_and_selection(button_n_clicks, marker_n_clicks, button_ids, marker_ids):
    ctx = callback_context
    triggered = ctx.triggered[0]
    triggered_id = triggered['prop_id']
    triggered_value = triggered['value']

    if not triggered_id or triggered_value is None:
        raise PreventUpdate

    prop_id_json = json.loads(triggered_id.split('.')[0])
    triggered_type = prop_id_json['type']
    selected_city = prop_id_json['index']

    if triggered_type == 'city-marker':
        # For city markers, set the city and clear the disaster dropdown
        disaster_dropdown_value = None
        selected_data = next((item for city, item in cities.items() if city == selected_city), None)
        if not selected_data:
            raise PreventUpdate
        details = html.Div([
            html.H4(f"City: {selected_city}"),
            # Add more details if necessary
        ])
    else:
        # For disaster buttons, set both the city and the disaster
        selected_data = next((item for item in data_for_buttons if item['city'] == selected_city), None)
        if not selected_data:
            raise PreventUpdate
        disaster_dropdown_value = selected_data['disaster'].upper()
        details = None

    # Return the selected city, the details for rendering, and the disaster dropdown value (if applicable)
    return selected_city, details, disaster_dropdown_value


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
