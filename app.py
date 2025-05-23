#!/usr/bin/env python3
"""
DMX Life Application - Main Entry Point
Web interface for controlling DMX lighting scenes via Art-Net
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
