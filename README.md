# ha_352air for M25
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

352空气检测仪M25
- [352 PM2.5 检测仪](https://www.352group.com.cn/info.php?id=6)
![QQ截图20230413145018](https://user-images.githubusercontent.com/91654066/231677511-bc05d9ca-f086-4fc9-bc2a-cf151f53df47.jpg)

本来打算做一个集成的, 但是能力有限, 没弄好. 后来发现, 原来HA里面, Node Red可以接UDP的信息, 就先用NR来接入了.
有兴趣的朋友,可以先用NR接入, 后面, 再考虑用集成吧. NR比较简单, flow文件在[上面](https://github.com/WalterDSU/ha_352air_M25/blob/main/352air_m25_flows.json).
![QQ截图20230413145302](https://user-images.githubusercontent.com/91654066/231677748-69526b2c-09ac-4971-aa21-6b99d6d80a6c.jpg)

