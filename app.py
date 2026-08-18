#!/usr/bin/env python3
"""
DMX Life Application - Main Entry Point
Web interface for controlling DMX lighting scenes via Art-Net
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Host and debug are resolved by create_app() from DMXLIFE_HOST /
    # DMXLIFE_DEBUG, with a bind-address-based safety check already applied.
    app.run(host=app.config['DMXLIFE_HOST'], port=5050, debug=app.config['DMXLIFE_DEBUG'])
