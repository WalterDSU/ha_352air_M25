"""Support for 352Air PM2.5 sensors."""

import asyncio
import logging
import socket

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_MAC,
    DEVICE_CLASS_PM25,
    PERCENTAGE,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MULTICAST_ADDR = "233.255.255.255"
PORT_352AIR_SENSOR = 11530


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the 352Air PM2.5 sensor platform."""
    mac_addr = config[CONF_MAC].replace(":", "").upper()
    coordinator = _352AirDataUpdateCoordinator(hass, mac_addr)
    await coordinator.async_refresh()

    async_track_time_interval(
        hass,
        coordinator.async_refresh,
        timedelta(minutes=1),
    )

    async_add_entities([_352AirSensor(coordinator)])


class _352AirDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the 352Air sensor."""

    def __init__(self, hass, mac_addr):
        """Initialize the update coordinator."""
        self._hass = hass
        self._mac_addr = mac_addr
        self.result = {}
        self._available = False
        self._timeout = 15

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from the 352Air sensor."""
        try:
            transport, protocol = await asyncio.wait_for(
                self._hass.loop.create_datagram_endpoint(
                    lambda: _352AirProtocol(self),
                    local_addr=("0.0.0.0", PORT_352AIR_SENSOR),
                    family=socket.AF_INET,
                ),
                timeout=self._timeout,
            )

            # Send multicast message to request data from sensors
            msg = bytes.fromhex("A112345678000000000000007B")
            transport.sendto(msg, (MULTICAST_ADDR, PORT_352AIR_SENSOR))

            # Wait for response
            await asyncio.sleep(0.5)

            # Close transport
            transport.close()

        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout when attempting to get data from 352Air sensor.")

        except Exception as ex:
            raise UpdateFailed(f"Exception during communication with 352Air sensor: {ex}") from ex

        # Update state
        if self.result:
            pm25 = self.result.get("pm25")
            return {"state": pm25, "available": True}

        raise UpdateFailed("Unable to retrieve data from 352Air sensor.")


class _352AirSensor(SensorEntity):
    """Representation of a 352Air PM2.5 sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._unique_id = coordinator._mac_addr
        self._name = f"352Air ({self._unique_id})"
        self._state = None
        self._device_class = DEVICE_CLASS_PM25
        self._unit_of_measurement = PERCENTAGE
        self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        return self._unit_of_measurement

    @property
    def available(self):
        """Return whether the sensor is available."""
        return self._available

    async def async_update(self):
        """Update the state of the sensor."""
        await self._coordinator.async_request_refresh()

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class


class _352AirProtocol(asyncio.DatagramProtocol):
    """Protocol class for handling UDP responses from 352Air sensors."""

    def __init__(self, coordinator):
        self.coordinator = coordinator

    def datagram_received(self, data, addr):
        """Receive incoming datagrams and parse them."""
        if len(data) != 33 or data[0] != 0xA1:
            return
    mac_addr = data[2:8].hex().upper()
    if mac_addr != self.coordinator._mac_addr:
        return

    pm25 = int.from_bytes(data[19:21], byteorder="big")
    self.coordinator.result = {"pm25": pm25}
