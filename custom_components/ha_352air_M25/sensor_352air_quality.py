"""
352Air Quality Sensor for Home Assistant
"""

import asyncio
import logging
import socket

from homeassistant.components.sensor import (
    DEVICE_CLASS_PM25,
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_TIMEOUT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get_registry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = "352air_M25"

MULTICAST_ADDR = "233.255.255.255"
PORT_352AIR_SENSOR = 11530

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Required(CONF_NAME, default="352Air"): cv.string,
        vol.Optional(CONF_TIMEOUT, default=15): cv.positive_int,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the 352Air Quality sensor platform."""
    entities = []
    try:
        registry = await async_get_registry(hass)

        # Check if already added
        if registry.async_is_registered(config[CONF_MAC]):
            return
        new_entity = PM25Sensor(hass, config)
        entities.append(new_entity)
        registry.async_get_or_create(
            SensorEntity.domain,
            DOMAIN,
            config[CONF_MAC],
            suggested_object_id=config[CONF_NAME],
            device_class=DEVICE_CLASS_PM25,
            config_entry=new_entity.config_entry,
            device={
                (CONF_DEVICE_CLASS, DEVICE_CLASS_PM25),
                (CONF_NAME, config[CONF_NAME])
            },
            capabilities={
                "rotatable": False
            },
            supported_features=0,
        )
    except Exception as ex:
        _LOGGER.error("Exception while setting up 352Air sensor: %s", ex)

    async_add_entities(entities, True)


class PM25Sensor(SensorEntity):
    """Representation of a 352Air Quality sensor."""

    def __init__(self, hass, config):
        self.hass = hass
        self._name = config[CONF_NAME]
        self._mac_addr = config[CONF_MAC].replace(":", "").upper()
        self._state = None
        self._available = False
        self._session = async_get_clientsession(self.hass)
        self.result = {}
        self._timeout = config.get(CONF_TIMEOUT)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return self._mac_addr

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            'identifiers': {(DOMAIN, self._mac_addr)},
            'name': self._name,
            'manufacturer': '352Air',
            'model': 'M25',
            'sw_version': '',
            'entry_type': 'service',
        }

    async def async_update(self):
        """Get the latest data and updates the state."""
        try:
            transport, protocol = await asyncio.wait_for(
                self.hass.loop.create_datagram_endpoint(
                    lambda: _352AirProtocol(self),
                    local_addr=('0.0.0.0', PORT_352AIR_SENSOR),
                    family=socket.AF_INET
                ),
                timeout=self._timeout,
            )

            # Send multicast message to request data from sensors
            msg = bytes.fromhex('A112345678000000000000007B')
            transport.sendto(msg, (MULTICAST_ADDR, PORT_352AIR_SENSOR))

            # Wait for response
            await asyncio.sleep(0.5)

            # Close transport
            transport.close()

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout when attempting to get data from 352Air sensor.")
            self._available = False
            return

    except Exception as ex:
        _LOGGER.error("Exception during communication with 352Air sensor: %s", ex)
        self._available = False
        return

    # Update state
    if self.result:
        pm25 = self.result.get('pm25')
        self._state = pm25
        self._available = True
    else:
        _LOGGER.error("Unable to retrieve data from 352Air sensor.")
        self._available = False
class _352AirProtocol(asyncio.DatagramProtocol):
"""Protocol class for handling UDP responses from 352Air sensors."""

def __init__(self, sensor):
    self.sensor = sensor

def datagram_received(self, data, addr):
    """Receive incoming datagrams and parse them."""
    if len(data) != 33 or data[0] != 0xA1:
        return

    mac_addr = data[2:8].hex().upper()
    if mac_addr != self.sensor._mac_addr:
        return

    pm25 = int.from_bytes(data[19:21], byteorder='big')
    self.sensor.result = {'pm25': pm25}
    
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            try:
                # Validate input
                mac_addr = user_input['mac_addr'].replace(':', '').upper()
                name = user_input['name']

                # Check to see if device already registered in the system
                existing_device = await self.async_set_unique_id(mac_addr)

                if existing_device:
                    self._abort_if_unique_id_configured()
                    return self.async_abort(reason='already_configured')

                # Pass parameters to the next step
                return self.async_create_entry(
                    title=name,
                    data={
                        'name': name,
                        'mac_addr': mac_addr,
                    }
                )
            except Exception as ex:
                _LOGGER.error("Exception occurred in config flow: %s", ex)
                return self.async_abort(reason='exception')
        else:
            return self.async_show_form(
                step_id='user',
                data_schema=vol.Schema(
                    {
                        vol.Required('name', default='352Air'): str,
                        vol.Required('mac_addr'): str,
                    }
                ),
            )

    async def async_step_import(self, import_config):
        """Import a new device from configuration.yaml."""
        mac_addr = import_config[CONF_MAC_ADDR].replace(':', '').upper()
        name = import_config[CONF_NAME]

        # Check to see if device already registered in the system
        existing_device = await self.async_set_unique_id(mac_addr)

        if existing_device:
            self.async_abort(reason='already_configured')
            return

        return self.async_create_entry(
            title=name,
            data={
                'name': name,
                'mac_addr': mac_addr,
            },
        )
      
    """ async_unload_entry"""

"""這個方法會在註冊實體時被調用，用於卸載與該實體相關聯的任何資源"""
    async def async_unload_entry(hass, entry):
    """Unload a config entry."""
        return True

    async_unload_entry(hass, entry)
