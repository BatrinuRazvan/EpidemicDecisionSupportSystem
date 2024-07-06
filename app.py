import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

navbar_style = {
    'display': 'flex',
    'justifyContent': 'space-around',
    'alignItems': 'center',
    'backgroundColor': '#007BFF',
    'padding': '10px',
    'fontFamily': 'sans-serif',
    'color': 'white'
}

link_style = {
    'textDecoration': 'none',
    'color': 'white',
    'fontSize': '30px',
    'margin': '0 15px',
    'position': 'relative',
    'padding': '0 5px'
}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1('Disaster Decision Support System', style={'textAlign': 'center'}),

    # Navbar
    html.Div([
        html.Nav([
            dcc.Link(f"{page['name']}", href=page["relative_path"], style=link_style, className='nav-link')
            for page in dash.page_registry.values()
        ], style=navbar_style)
    ]),

    dash.page_container
])

app.clientside_callback(
    """
    function(href) {
        const links = document.querySelectorAll('.nav-link');
        links.forEach(link => {
            if (link.href === window.location.href) {
                link.style.borderBottom = '2px solid orange';
                link.style.paddingBottom = '3px';
                link.style.color = 'orange';
                link.style.fontWeight = 'bold';
            } else {
                link.style.borderBottom = 'none';
                link.style.color = 'white';  // Reset to default color when not active
                link.style.fontWeight = 'normal';  // Reset to
            }
        });
        return null;
    }
    """,
    output=dash.Output('dummy-div', 'children'),
    inputs=[dash.Input('url', 'href')]
)

app.layout.children.append(html.Div(id='dummy-div', style={'display': 'none'}))

if __name__ == '__main__':
    app.run_server(debug=True)
