# ha_352air for M25
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

352空气检测仪M25
- [352 PM2.5 检测仪](https://www.352group.com.cn/info.php?id=6)

本来打算做一个集成的, 但是能力有限, 没弄好. 后来发现, 原来HA里面, Node Red可以接UDP的信息, 就只是用NR来接入了.
有兴趣的朋友,可以先用NR接入, 后面, 再考虑用集成吧. NR比较简单, flow文件在上面.
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
