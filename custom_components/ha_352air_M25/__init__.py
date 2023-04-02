"""The 352Air PM2.5 sensor integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get_registry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the 352Air PM2.5 sensor integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up 352Air PM2.5 sensor from a config entry."""
    mac_addr = entry.data["mac_addr"]
    entity_registry = await async_get_registry(hass)
    if entity_registry.async_is_registered(mac_addr):
        return False

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a 352Air PM2.5 sensor config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True
