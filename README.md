# ha_352air for M25
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

352空气检测仪M25
- [352 PM2.5 检测仪](https://www.352group.com.cn/info.php?id=6)
![QQ截图20230413145018](https://user-images.githubusercontent.com/91654066/231677511-bc05d9ca-f086-4fc9-bc2a-cf151f53df47.jpg)

本来打算做一个集成的, 但是能力有限, 没弄好. 后来发现, 原来HA里面, Node Red可以接UDP的信息, 就先用NR来接入了.
有兴趣的朋友,可以先用NR接入, 后面, 再考虑用集成吧. NR比较简单, flow文件在[上面](https://github.com/WalterDSU/ha_352air_M25/blob/main/352air_m25_flows.json).
![QQ截图20230418132118](https://user-images.githubusercontent.com/91654066/232678522-6df352a2-b01c-4333-9853-4e7021d37084.jpg)


