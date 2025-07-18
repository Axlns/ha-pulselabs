# Pulse Labs Integration for Home Assistant

This custom integration connects your Pulse Labs devices (Pulse One, Pro, Hub, etc.) to Home Assistant via the official cloud API.

## Features

- Supports Pulse One, Pulse Pro, Pulse Zero
- Support for Hubs, Sensors and Controllers is in development.
- Uses `/all-devices` for efficient polling
- Creates dynamic sensors (CO₂, VPD, PPFD, etc.)
- Accurate leaf/air VPD calculation (Buck 1981)
- HACS-compatible

## Installation via HACS

1. Go to **HACS → Integrations → Custom Repositories**
2. Add this repo URL as a **"Integration"**
3. Search for **Pulse Labs**, install
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration**, search **Pulse Labs**

## Manual Installation

Copy the `custom_components/pulselabs/` folder into your Home Assistant `custom_components` directory.

## Configuration

You will be asked to enter your Pulse API key. All devices will be discovered automatically.

---
