"""Constants for the Pulse Labs integration."""

DOMAIN = "pulselabs"

BASE_URL = "https://api.pulsegrow.com"
CONF_DEVICES = "devices"
MANUFACTURER = "Pulse Labs, Inc."
DEVICE_TYPE_MAP: dict[int, str] = {
    0: "Pulse One",
    1: "Pulse Pro",
    2: "Pulse Hub",
    3: "Pulse Sensor",
    4: "Pulse Controller",
    5: "Pulse Zero",
}

PLAN_LIMITS = {
    "hobbyist": 4800,
    "enthusiast": 24000,
    "professional": 120000,
}
