# 利用AWS IoT Greengrass在边缘DIY自动浇花

build a IoT application to water flower by leveraging AWS IoT Greengrass
利用AWS IoT Greengrass的边缘计算能力，实现在本地基于温度、湿度和亮度传感器数据控制水泵进行自动浇花，同时在网络可用时将传感器数据和继电器数据上传到云端，进行远程监控和可视化分析。该方法不受网络因素影响，即使网络不可用，依然可以自主控制浇花行为。

## 自动浇花思路
* 通过树莓派和AWS IoT Core建立连接
* 利用光传感器、温度传感器和土壤湿度传感器检测环境亮度、温度及花盆中湿度，通过树莓派汇总后上传
* 利用LCD屏在本地显示传感器数据信息，并以不同颜色醒目提示土壤湿度状况
* 利用继电器控制小水泵进行浇水
* 在树莓派上运行自动控制逻辑，根据亮度、温度和湿度确定继电器状态
* 通过topic来设置湿度阈值，这样可以很方便地实现通过手机App或Web应用进行参数设置
* 将传感器数据和继电器状态通过AWS IoT的规则引擎发送到Amazon Elasticsearch，建立监控仪表板，这样可以很方便地通过手机或浏览器进行可视化监控

## 所需材料
* 树莓派一个，MicroSD卡一张
* GrovePi+ 树莓派扩展板一个
* 三个Grove传感器配件：温度传感器，土壤湿度传感器，亮度传感器
* Grove 1602 LCD RGB背光显示屏一个
* 一个继电器配件（Grove Ralay）
* 微型水泵一个（3V/5V/6V），水泵水管一条

完整的方案介绍和搭建步骤请参见博客：[利用 AWS IoT Greengrass 在边缘 DIY 自动浇花 | 手把手玩转物联网](https://aws.amazon.com/cn/blogs/china/diy-auto-watering-at-the-edge-with-aws-iot-greengrass-hand-to-hand-internet-of-things/)


