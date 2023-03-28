# ha_352air for M25

352空气检测仪M25
- [352 PM2.5 检测仪](https://www.352group.com.cn/info.php?id=6)


## Installation

```
sudo npm install -g homebridge-352air
```


## Example config

```json
{
  "bridge": {
      "name": "Homebridge",
      "username": "CC:22:3D:E3:CE:30",
      "port": 51826,
      "pin": "031-45-154"
    },
  "description": "This is an example configuration file with one Hygrotermograph accessory. You can use this as a template for creating your own configuration file containing devices you actually own.",
  "accessories": [
      {
            "accessory": "The352AirQuality",
            "name": "PM2.5",
            "timeout": 10
      }
    ]
}
```

## Screenshot

![](https://github.com/mckelvin/homebridge-352air/raw/master/.github/apple-homekit-352air-screenshot.png)
