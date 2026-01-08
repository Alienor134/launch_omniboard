"""Dash layout components for AltarViewer."""
import os
from dash import html, dcc
import dash_bootstrap_components as dbc


def build_layout():
    """Build the main application layout."""
    return dbc.Container(
        [
            # Storage components
            dcc.Store(id="connection-store", storage_type="session"),
            dcc.Store(id="databases-store", storage_type="session"),
            dcc.Store(id="selected-db-store", storage_type="session"),
            dcc.Store(id="launched-containers-store", storage_type="session", data=[]),
            
            # Navbar with Altar branding
            dbc.Navbar(
                dbc.Container(
                    [
                        html.Div(
                            [
                                dbc.NavbarBrand(
                                    "AltarViewer",
                                    class_name="mb-0 h4",
                                    style={"fontWeight": "600"}
                                ),
                                html.Span(
                                    " Omniboard Launcher",
                                    style={"color": "var(--muted)", "marginLeft": "0.5rem"}
                                ),
                            ],
                            style={"display": "flex", "alignItems": "center"}
                        ),
                    ],
                    fluid=True,
                ),
                dark=True,
                sticky="top",
                class_name="mb-4",
                style={"background": "var(--panel)", "borderBottom": "1px solid var(--stroke)"}
            ),
            
            # Connection Section
            build_connection_section(),
            
            # Database Selection Section
            build_database_section(),
            
            # Omniboard Control Section
            build_omniboard_section(),
            
        ],
        fluid=False,
        style={"maxWidth": "800px"},
    )


def build_connection_section():
    """Build MongoDB connection configuration section."""
    # Default Mongo URL can be overridden via environment (e.g. Docker)
    default_mongo_url = os.environ.get("MONGO_DEFAULT_URL", "mongodb://localhost:27017/")
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Connect to MongoDB", className="card-title mb-2", style={"fontSize": "0.95rem"}),
                
                # Connection mode selector
                dbc.RadioItems(
                    id="connection-mode",
                    options=[
                        {"label": "Connect by Port", "value": "port"},
                        {"label": "Connect by Full URL", "value": "url"},
                    ],
                    value="port",
                    inline=True,
                    className="mb-2",
                    style={"fontSize": "13px"},
                ),
                
                # Port input (visible by default)
                html.Div(
                    id="port-input-container",
                    children=[
                        dbc.Label("MongoDB Port:"),
                        dbc.Input(
                            id="port-input",
                            type="text",
                            placeholder="27017",
                            value="27017",
                        ),
                    ],
                    className="mb-3",
                ),
                
                # URL input (hidden by default)
                html.Div(
                    id="url-input-container",
                    children=[
                        dbc.Label("MongoDB URL:"),
                        dbc.Input(
                            id="url-input",
                            type="text",
                            placeholder=default_mongo_url,
                            value=default_mongo_url,
                        ),
                    ],
                    className="mb-3",
                    style={"display": "none"},
                ),
                
                # Connect button
                dbc.Button(
                    "Connect to MongoDB",
                    id="connect-btn",
                    color="primary",
                    className="w-100",
                ),
                
                # Connection status
                html.Div(id="connection-status", className="mt-2"),
            ]
        ),
        className="mb-3",
    )


def build_database_section():
    """Build database selection section."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Available Databases", className="card-title mb-2", style={"fontSize": "0.95rem"}),
                
                # Database list container - white background, 2 columns
                html.Div(
                    id="database-list-container",
                    children=[
                        html.P(
                            "Connect to MongoDB to see available databases",
                            className="text-muted",
                            style={"padding": "1rem", "fontSize": "13px"},
                        )
                    ],
                    style={
                        "maxHeight": "280px",
                        "overflowY": "auto",
                        "padding": "0.75rem",
                        "background": "white",
                        "borderRadius": "6px",
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "0.25rem",
                    },
                ),
                
                # Selected database display
                html.Div(id="selected-database", className="mt-2", style={"fontSize": "13px"}),
            ]
        ),
        className="mb-3",
    )


def build_omniboard_section():
    """Build Omniboard control section."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Omniboard Controls", className="card-title mb-2", style={"fontSize": "0.95rem"}),
                
                # Launch button
                dbc.Button(
                    "Launch Omniboard for Selected Database",
                    id="launch-btn",
                    color="primary",
                    className="w-100 mb-2",
                    disabled=True,
                ),
                
                # Clear containers button
                dbc.Button(
                    "Clear All Omniboard Containers",
                    id="clear-btn",
                    color="warning",
                    className="w-100 mb-3",
                    outline=True,
                ),
                
                # Launched instances display (no extra loading spinner; Omniboard
                # startup time is left to the user)
                html.Div(
                    id="launched-instances",
                    children=[
                        html.P(
                            "No Omniboard instances launched yet",
                            className="text-muted text-center mb-0",
                        )
                    ],
                    style={
                        "border": "1px solid #dee2e6",
                        "borderRadius": "0.25rem",
                        "padding": "1rem",
                        "minHeight": "100px",
                    },
                ),
                html.Small(
                    "Note: Omniboard may take a few seconds to start after launch. "
                    "If the page opens blank, wait a bit and refresh.",
                    className="text-muted d-block mt-1",
                    style={"fontSize": "11px"},
                ),
            ]
        ),
    )
