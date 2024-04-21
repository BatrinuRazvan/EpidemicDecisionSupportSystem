import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

# Define some CSS styles for the navbar
navbar_style = {
    'display': 'flex',
    'justifyContent': 'space-around',  # Updated to camelCase
    'alignItems': 'center',  # Updated to camelCase
    'backgroundColor': '#007BFF',  # Updated to camelCase
    'padding': '10px',
    'fontFamily': 'sans-serif',  # Updated to camelCase
    'color': 'white'
}

link_style = {
    'textDecoration': 'none',  # Updated to camelCase
    'color': 'white',
    'fontSize': '20px',  # Updated to camelCase
    'margin': '0 15px'
}

app.layout = html.Div([
    html.H1('Epidemic Decision Support System', style={'textAlign': 'center'}),

    # Navbar
    html.Div([
        html.Nav([
            dcc.Link(f"{page['name']}", href=page["relative_path"], style=link_style)
            for page in dash.page_registry.values()
        ], style=navbar_style)
    ]),

    # Page content
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)

