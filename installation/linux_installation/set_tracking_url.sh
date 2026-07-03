#!/bin/bash

# Define the tracking URI you want to set
TRACKING_URI="http://192.168.1.147:5000"

# Add the export statement to the .bashrc file if not already set
if ! grep -Fxq "export MLFLOW_TRACKING_URI=$TRACKING_URI" "$HOME/.bashrc"; then
    echo "export MLFLOW_TRACKING_URI=$TRACKING_URI" >> "$HOME/.bashrc"
    echo "MLFLOW_TRACKING_URI has been added to .bashrc"
else
    echo "MLFLOW_TRACKING_URI is already set in .bashrc"
fi

# Reload the .bashrc file to apply changes
source "$HOME/.bashrc"