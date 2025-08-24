#!/usr/bin/env python3
"""
Development server script for Performance Motors Limited Sales Draft Generator
Runs on port 5001 to avoid conflicts with macOS AirPlay on port 5000
"""

from main import app

if __name__ == "__main__":
    print("Starting Performance Motors Limited Sales Draft Generator...")
    print("Server will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, port=5001, host='0.0.0.0')
