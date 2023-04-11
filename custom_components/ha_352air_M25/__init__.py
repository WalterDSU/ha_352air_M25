"""Custom Integration for Air Quality Sensor."""

import logging
import socket


from homeassistant.helpers.discovery import load_platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

DOMAIN = "352air_m25"

def create_server(host, port):
    """Create the UDP server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.setsockopt(socket.IPPROTO_IP,
                     socket.IP_ADD_MEMBERSHIP,
                     socket.inet_aton(MULTICAST_ADDR) +
                     socket.inet_aton(host))

    return server

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Air Quality Sensor platform"""
    hass.data[DOMAIN] = {}

    for platform in ["sensor"]:
        load_platform(hass, platform, DOMAIN, {}, config)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Air Quality Sensor platform from a config entry"""
    # Get config data
    host = entry.data["host"]
    port = entry.data.get("port", DEFAULT_PORT)

    # Create UDP server
    try:
        server = create_server(host, port)
    except Exception as error:
        _LOGGER.error("Error starting UDP server: %s", error)
        raise ConfigEntryNotReady

    # Store server in data dict
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["server"] = server
    
    return True
    
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry"""
    # Shutdown UDP server
    server = hass.data[DOMAIN].get("server")
    if server:
        server.close()

    return True





async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a 352Air PM2.5 sensor config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True
