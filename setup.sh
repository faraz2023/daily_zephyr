#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Create a .env file from the example
cp env.example .env

echo "Setup complete. Remember to update the .env file with your API keys." 