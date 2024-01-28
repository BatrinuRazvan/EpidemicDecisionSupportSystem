import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

# Define some CSS styles for the navbar
navbar_style = {
    'display': 'flex',
    'justify-content': 'space-around',
    'align-items': 'center',
    'background-color': '#007BFF',
    'padding': '10px',
    'font-family': 'sans-serif',
    'color': 'white'
}

link_style = {
    'text-decoration': 'none',
    'color': 'white',
    'font-size': '20px',
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

