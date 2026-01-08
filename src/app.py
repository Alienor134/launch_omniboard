"""Dash application for AltarViewer."""
from dash import Dash
import dash_bootstrap_components as dbc
from layout import build_layout


def create_dash_app():
    """Create and configure the Dash application."""
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.DARKLY,  # Dark Bootstrap theme
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
        ],
        suppress_callback_exceptions=True,
        title="AltarViewer - Omniboard Launcher",
        assets_folder='assets'
    )
    
    app.layout = build_layout()
    
    # Import callbacks after app is created to register them
    from callbacks import register_callbacks
    register_callbacks(app)
    
    return app


if __name__ == "__main__":
    app = create_dash_app()
    app.run(debug=True, port=8060)
