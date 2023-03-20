import socket
import json

from homeassistant.helpers.entity import Entity

MULTICAST_ADDR = "233.255.255.255"
PORT_352AIR_SENSOR = 11530

class The352AirQuality(Entity):
    def __init__(self, config):
        self._name = config.get('name', 'The 352Air Quality')
        self._state = None
        self._pm25 = None
        self._mac_addr = None
        self._ip_addr = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', PORT_352AIR_SENSOR)))
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_ADDR) + socket.inet_aton('0.0.0.0'))

    def update(self):
        data, _ = self._socket.recvfrom(1024)
        buf = bytearray(data)
        if len(buf) != 33 or buf[0] != 0xA1:
            return
        self._ip_addr = f"{str(_[0])}:{str(_[1])}"
        self._mac_addr = buf[2:8].hex()
        self._pm25 = buf[19:21].hex()
        self._state = self.calculate_air_quality()

    def calculate_air_quality(self):
        if self._pm25 is None:
            return None
        density = int(self._pm25, 16)
        if density <= 11:
            # 0 ~ 11
            return 'excellent'
        elif density <= 35:
            # 12 ~ 35
            return 'good'
        elif density <= 55:
            # 36 ~ 55
            return 'fair'
        elif density <= 150:
            # 56 ~ 150
            return 'inferior'
        else:
            # 151 ~ 500
            return 'poor'

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return 'air quality index'

    @property
    def device_state_attributes(self):
        return {
            'pm25': self._pm25,
            'ip_address': self._ip_addr,
            'mac_address': self._mac_addr,
        }

    @property
    def icon(self):
        return 'mdi:blur-radial'

    def get_air_quality_index(self):
        return self._state

    def get_pm25_density(self):
        if self._pm25 is not None:
            return int(self._pm25, 16)

    def get_device_state_attributes(self):
        attrs = {}
        attrs['pm25'] = self._pm25
        attrs['ip_address'] = self._ip_addr
        attrs['mac_address'] = self._mac_addr
        return attrs

    def update_air_quality_sensor(self):
        self.update()
        self.schedule_update_ha_state()

    def update_air_quality_callback(self, event_time):
        self.update_air_quality_sensor()
        self.hass.helpers.event.async_call_later(120, self.update_air_quality_callback, None)

    def setup_platform(hass, config, add_entities, discovery_info=None):
        add_entities([The352AirQuality(config)], True)
