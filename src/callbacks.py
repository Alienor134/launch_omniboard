"""Dash callbacks for AltarViewer (Dash web UI).

This module wires the Dash UI to three main concerns:

* MongoDB connection & database discovery
* Database selection UX (highlighting, enabling launch)
* Omniboard lifecycle (launch, clear-all)

The callbacks are thin wrappers around small helper functions so the
behaviour is easier to understand and evolve.
"""
import os
from dash import Output, Input, State, html, no_update, ALL
import dash_bootstrap_components as dbc
from mongodb import MongoDBClient
from omniboard import OmniboardManager


# Initialize managers (shared, module-level singletons)
mongo_client = MongoDBClient()
omniboard_manager = OmniboardManager()


# --- Styling helpers ------------------------------------------------------

DB_ITEM_BASE_STYLE = {
    "padding": "0.4rem 0.6rem",
    "cursor": "pointer",
    "fontSize": "13px",
    "color": "black",
    "borderRadius": "4px",
    "transition": "all 0.15s ease",
}

DB_ITEM_SELECTED_STYLE = dict(
    DB_ITEM_BASE_STYLE,
    **{"backgroundColor": "#4f7cff", "color": "white"},
)


def _friendly_mongo_error_message(error: Exception) -> str:
    """Return a short, user-friendly error message for Mongo failures."""
    error_msg = str(error)

    lower = error_msg.lower()
    if "serverselectiontimeouterror" in error_msg or "timed out" in lower:
        return (
            "Cannot connect to MongoDB server. "
            "Please ensure MongoDB is running and the connection details are correct."
        )
    if "connection refused" in lower:
        return (
            "Connection refused by MongoDB server. "
            "MongoDB may not be running on this port."
        )
    if "authentication failed" in lower:
        return "MongoDB authentication failed. Please check your credentials."

    return f"Connection Error: {error_msg}"


def _build_instances_ui(launched_containers):
    """Build the UI list of launched Omniboard instances.

    All instances are shown as clickable links; Omniboard startup time is
    left to the user (they may need to refresh the page if it is not ready
    yet), so we avoid extra polling complexity.
    """
    if not launched_containers:
        return [
            html.P(
                "No Omniboard instances launched yet",
                className="text-muted text-center mb-0",
            )
        ]

    items = []
    for info in launched_containers:
        db_name = info.get("database", "?")
        url = info.get("url", "")

        content = [
            html.Span(
                f"{db_name}: ",
                style={"fontWeight": "500", "marginRight": "0.5rem"},
            ),
            html.A(
                url,
                href=url,
                target="_blank",
                className="text-decoration-none",
            ),
        ]

        items.append(
            html.Div(
                content,
                style={"padding": "0.3rem 0", "fontSize": "13px"},
            )
        )

    return items


def register_callbacks(app):
    """Register all callbacks with the app instance."""
    
    @app.callback(
        [Output("port-input-container", "style"),
         Output("url-input-container", "style")],
        Input("connection-mode", "value")
    )
    def toggle_connection_mode(mode):
        """Toggle between port and URL input modes."""
        if mode == "port":
            return {"display": "block", "marginBottom": "1rem"}, {"display": "none"}
        else:
            return {"display": "none"}, {"display": "block", "marginBottom": "1rem"}


    @app.callback(
        [Output("connection-store", "data"),
         Output("databases-store", "data"),
         Output("connection-status", "children"),
         Output("database-list-container", "children")],
        Input("connect-btn", "n_clicks"),
        [State("connection-mode", "value"),
         State("port-input", "value"),
         State("url-input", "value")],
        prevent_initial_call=True
    )
    def connect_to_mongodb(n_clicks, mode, port, url):
        """Connect to MongoDB and retrieve database list."""
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        
        try:
            # Connect based on mode
            if mode == "port":
                port_value = port or "27017"
                databases = mongo_client.connect_by_port(port_value)
                connection_info = {"mode": "port", "port": port_value}
            else:
                # If URL is empty, fall back to the configured default URL
                default_url = os.environ.get("MONGO_DEFAULT_URL", "mongodb://localhost:27017/")
                url_value = (url or "").strip() or default_url
                databases = mongo_client.connect_by_url(url_value)
                connection_info = {"mode": "url", "url": url_value}
            
            # Create database list UI
            if not databases:
                db_list_ui = html.P(
                    "No databases found",
                    className="text-muted",
                    style={"padding": "1rem 0", "fontSize": "13px"}
                )
            else:
                db_list_ui = [
                    html.Div(
                        db,
                        id={"type": "db-button", "index": db},
                        className="db-item",
                        style=DB_ITEM_BASE_STYLE,
                    )
                    for db in databases
                ]
            
            success_msg = dbc.Alert(
                f"Successfully connected! Found {len(databases)} database(s).",
                color="success",
                dismissable=True,
                duration=4000,
            )
            
            return connection_info, databases, success_msg, db_list_ui
            
        except Exception as e:
            error_alert = dbc.Alert(
                _friendly_mongo_error_message(e),
                color="danger",
                dismissable=True,
            )
            
            return no_update, no_update, error_alert, no_update


    @app.callback(
        [Output("selected-db-store", "data"),
         Output("selected-database", "children"),
         Output("launch-btn", "disabled"),
         Output({"type": "db-button", "index": ALL}, "style")],
        Input({"type": "db-button", "index": ALL}, "n_clicks"),
        State({"type": "db-button", "index": ALL}, "id"),
        prevent_initial_call=True
    )
    def select_database(n_clicks_list, button_ids):
        """Handle database selection and visually highlight the chosen database."""
        from dash import callback_context

        # No trigger information: nothing to do
        if not callback_context.triggered:
            return no_update, no_update, no_update, no_update

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        import json
        try:
            button_id = json.loads(triggered_id)
            db_name = button_id["index"]
        except Exception:
            return no_update, no_update, no_update, no_update

        # Compute styles for all db buttons, highlighting the selected one
        styles = []
        for btn_id in button_ids:
            if isinstance(btn_id, dict) and btn_id.get("index") == db_name:
                styles.append(DB_ITEM_SELECTED_STYLE)
            else:
                styles.append(DB_ITEM_BASE_STYLE)

        # We now rely on visual highlight, so we no longer need the "Selected: ..." text
        return db_name, "", False, styles
    @app.callback(
        [Output("launched-containers-store", "data", allow_duplicate=True),
         Output("launched-instances", "children", allow_duplicate=True)],
        Input("launch-btn", "n_clicks"),
        [State("selected-db-store", "data"),
         State("launched-containers-store", "data"),
         State("connection-store", "data")],
        prevent_initial_call=True
    )
    def launch_omniboard(n_clicks, selected_db, launched_containers, connection_info):
        """Launch Omniboard container for selected database.
        """
        if not n_clicks or not selected_db:
            return no_update, no_update

        try:
            # Get MongoDB connection details
            mongo_host, mongo_port, _ = mongo_client.parse_connection_url()

            # For URL-based connections (e.g. Atlas / remote VM with
            # authentication), reuse the full connection URI so that
            # Omniboard can authenticate and honour any options. For the
            # simple port-based mode we keep using host/port only so
            # localhost mappings continue to work as before.
            mongo_uri = None
            if isinstance(connection_info, dict) and connection_info.get("mode") == "url":
                mongo_uri = mongo_client.get_connection_uri()

            # Launch Omniboard (non-blocking, container starts in background)
            container_name, host_port = omniboard_manager.launch(
                db_name=selected_db,
                mongo_host=mongo_host,
                mongo_port=mongo_port,
                mongo_uri=mongo_uri,
            )

            # Add to launched containers list
            if launched_containers is None:
                launched_containers = []

            container_info = {
                "database": selected_db,
                "port": host_port,
                "container": container_name,
                "url": f"http://localhost:{host_port}",
            }
            launched_containers.append(container_info)

            # Build UI for launched instances
            instances_ui = _build_instances_ui(launched_containers)

            return launched_containers, instances_ui

        except Exception as e:
            error_card = dbc.Alert(
                f"Failed to launch Omniboard: {str(e)}",
                color="danger",
                dismissable=True,
            )
            return no_update, error_card


    @app.callback(
        [Output("launched-containers-store", "data", allow_duplicate=True),
         Output("launched-instances", "children", allow_duplicate=True)],
        Input("clear-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_containers(n_clicks):
        """Clear all Omniboard containers."""
        if not n_clicks:
            return no_update, no_update
        
        try:
            # Best-effort clear; ignore the count as we don't currently
            # surface an extra alert, just reset the store/UI.
            omniboard_manager.clear_all_containers()

            return [], _build_instances_ui([])
            
        except Exception as e:
            error = dbc.Alert(
                f"Error clearing containers: {str(e)}",
                color="danger",
                dismissable=True,
            )
            return no_update, error
