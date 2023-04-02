import json
import logging
import asyncio
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_NAME,
    ATTR_DEVICE_CLASS,
)
from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_PM25,
)
from homeassistant.helpers.entity_registry import async_get_registry

_LOGGER = logging.getLogger(__name__)

MULTICAST_ADDR = '233.255.255.255'
PORT_352AIR_SENSOR = 11530

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the 352Air Quality sensor platform."""
    entities = []
    try:
        registry = await async_get_registry(hass)

        # Check if already added
        if registry.async_is_registered(config['mac_addr']):
            return
        new_entity = PM25Sensor(hass, config)
        entities.append(new_entity)
        registry.async_get_or_create(
            SensorEntity.domain,
            "352air_M25",
            config['mac_addr'],
            suggested_object_id=config['name'],
            device_class=DEVICE_CLASS_PM25,
            config_entry=new_entity.config_entry,
            device={
                (ATTR_DEVICE_CLASS, DEVICE_CLASS_PM25),
                (CONF_NAME, config['name'])
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
        self._name = config['name']
        self._mac_addr = config['mac_addr']
        self._state = None
        self._available = False
        self._session = async_get_clientsession(hass)
        self.result = {}
        self._timeout = 15

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
            _LOGGER.error("Timeout when attempting to get data from sensor.")
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

class _352AirProtocol(asyncio.DatagramProtocol):

    def __init__(self, entity):
        self.entity = entity

    def datagram_received(self, data, addr):
        """Handle incoming UDP packets."""
        buf = bytearray(data)
        if not buf or buf[0] != 0xA1 or len(buf) != 33:
            return

        ip_addr = f"{addr[0]}:{addr[1]}"
        mac_addr = buf[2:8].hex()
        pm25 = int.from_bytes(buf[19:21], byteorder='big')

        self.entity.result = {
            'pm25': pm25
    }
