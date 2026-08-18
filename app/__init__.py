"""
DMX Life Application - App Initialization
"""
import os
import sys
import json
import logging
import secrets
import datetime
from flask import Flask
from flask_httpauth import HTTPBasicAuth

# Initialize HTTP Basic Auth
auth = HTTPBasicAuth()

# Addresses treated as "not reachable from the network". Only these are
# considered safe to fall back to development defaults on.
LOOPBACK_HOSTS = {'127.0.0.1', 'localhost', '::1'}

# Development-only fallback credentials. Only ever used when DMXLIFE_HOST
# resolves to loopback (see _resolve_runtime_settings), so a public network
# is never guarded by these. They are intentionally the same values this
# application shipped with historically, kept only for local dev
# convenience now that the venue path requires real credentials.
_DEV_USERNAME = "admin"
_DEV_PASSWORD = "banana123"

# Populated by create_app() -> _resolve_runtime_settings(); read by
# verify_password(). A dict (not module globals) so tests can swap it.
_credentials = {'username': None, 'password': None}


@auth.verify_password
def verify_password(username, password):
    """Verify username and password using a constant-time comparison"""
    valid_username = _credentials['username']
    valid_password = _credentials['password']
    if valid_username is None or valid_password is None:
        return None

    # Compare both fields unconditionally (not short-circuited) so a
    # mismatched username doesn't skip the password comparison and leak
    # timing information about which field was wrong.
    username_ok = secrets.compare_digest(username, valid_username)
    password_ok = secrets.compare_digest(password, valid_password)
    if username_ok and password_ok:
        return username
    return None


def _resolve_runtime_settings():
    """
    Resolve bind host, debug flag and credentials from the environment.

    The bind address determines how strict this is: on loopback, missing
    credentials fall back to development defaults (with a warning) and debug
    mode is allowed, because nothing off this machine can reach either. On
    any other address, both are required outright, refusing to start rather
    than silently running with a public password or an exposed debugger.

    Returns (host, debug, username, password).
    """
    host = os.environ.get('DMXLIFE_HOST', '127.0.0.1')
    debug = os.environ.get('DMXLIFE_DEBUG', '').strip().lower() in ('1', 'true', 'yes', 'on')
    username = os.environ.get('DMXLIFE_USERNAME')
    password = os.environ.get('DMXLIFE_PASSWORD')

    is_loopback = host in LOOPBACK_HOSTS

    if not is_loopback:
        if debug:
            sys.exit(
                f"Refusing to start: DMXLIFE_DEBUG is enabled while DMXLIFE_HOST is "
                f"'{host}' (not loopback). The interactive Werkzeug debugger would be "
                f"reachable by anyone who can reach the server. Unset DMXLIFE_DEBUG, "
                f"or set DMXLIFE_HOST=127.0.0.1 to debug locally."
            )
        if not username or not password:
            sys.exit(
                f"Refusing to start: DMXLIFE_HOST is '{host}' (not loopback), which "
                f"requires DMXLIFE_USERNAME and DMXLIFE_PASSWORD to be set. Example:\n"
                f"  DMXLIFE_USERNAME=admin DMXLIFE_PASSWORD=yourpassword ./start.sh"
            )
        return host, debug, username, password

    # Loopback: nothing off this machine can reach the server, so it is safe
    # to fall back to development defaults when credentials are not set.
    if not username or not password:
        logging.getLogger(__name__).warning(
            "DMXLIFE_USERNAME/DMXLIFE_PASSWORD not set; using development default "
            "credentials. This is only safe because DMXLIFE_HOST is loopback ('%s').",
            host,
        )
        username = username or _DEV_USERNAME
        password = password or _DEV_PASSWORD

    return host, debug, username, password


def create_app(config=None):
    """Initialize and configure the Flask application"""
    app = Flask(__name__)

    host, debug, username, password = _resolve_runtime_settings()
    _credentials['username'] = username
    _credentials['password'] = password

    # Default configuration
    app.config.update(
        SECRET_KEY=os.urandom(24),
        CONFIG_FILE=os.path.join(os.path.dirname(__file__), 'config.json'),
        MAX_SCENES=40,
        DMXLIFE_HOST=host,
        DMXLIFE_DEBUG=debug,
    )

    # Add context processors for templates
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.datetime.now().year}

    # Override with any passed configuration
    if config:
        app.config.update(config)

    # Load configuration from file if it exists
    if os.path.exists(app.config['CONFIG_FILE']):
        try:
            with open(app.config['CONFIG_FILE'], 'r') as f:
                app.config.update(json.load(f))
        except Exception as e:
            app.logger.error(f"Error loading configuration: {e}")

    # Register blueprints
    from app.views.main import main_bp
    from app.views.setup import setup_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(setup_bp, url_prefix='/setup')

    # Initialize DMX controller
    from app.dmx_controller import init_dmx_controller
    init_dmx_controller(app)

    return app
