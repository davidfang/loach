### loach

![image](https://github.com/daxingshen/imgines/raw/master/3%202.gif)

![image](https://github.com/daxingshen/imgines/raw/master/1.gif)
- loach是一个移动端爬虫，针对现下很火的短视频app—抖音

  1. 支持多个android设备并行自动化
  2. 支持任意android设备的服务端部署到任意机器
  3. 支持使用http方法控制任务

- 示意图

  ![](https://github.com/daxingshen/imgines/raw/master/loach_示意图修正.png)

  1. appium 提供了一组restful[接口用来控制设备](https://github.com/SeleniumHQ/selenium/wiki/JsonWireProtocol#session-1)
  2. scheduler会将从http接收到的command在存在可用设备的时候丢给设备去执行
     1. 对于CRAWLING类型的任务，是长期有效的，即任务没有终结点，设备会被永久占用
     2. 对于FINDING类型的任务，重试三次
  3. 确保android sdk正确配置并adb devices能看到设备

- QAQ

  1. 整个系统有哪些组成？

     loach进程、appium实例若干、android设备若干（数量等于appium实例数量）

  2. 一句话概括loach的逻辑？

     http api控制loach（shceduler），loach控制appium实例，appium实例控制android设备

  3. 部署对网络的要求

     loach进程、appium实例、android设备必须相互知道其它所在的位置。即在同一LAN

  4. loach、appium、android只能在一台机器上运行么？

     不必，正如Q3，互通是唯一网络要求

  5. 补充

     目前我使用i5+8Gwindows部署六台设备很流畅，如果需要大量部署的话。估计两位数就上限了。

     提供两种思路：

     1. 分布式部署，一个loach带十个设备还是很轻松的，若干个loach进程选择一个作为master进程并对外提供http服务(开发中)
     2. 若干个loach并行，并各自对外提供http服务

- 白话部署

     1. 环境

        appium： 1.8.1 实例六个 端口4723-4728

        设备：华为畅享7 SLA-TL10 六台 ip分别是 192.168.1.201-206 端口 5555-5560

        loach：1.2

     2. 启动

        1. adb连接设备

           > adb connect 192.168.1.201:5555
           >
           > adb connect 192.168.1.202:5556
           >
           > adb connect 192.168.1.203:5557
           >
           > adb connect 192.168.1.204:5558
           >
           > adb connect 192.168.1.205:5559
           >
           > adb connect 192.168.1.206:5560

        2. 启动appium

           > appium -p 4723 -bp 6001 -U 192.168.1.201

           > appium -p 4724 -bp 6002 -U 192.168.1.202

           > appium -p 4725 -bp 6003 -U 192.168.1.203

           > appium -p 4726 -bp 6004 -U 192.168.1.204

           > appium -p 4727 -bp 6005 -U 192.168.1.205

           > appium -p 4728 -bp 6006 -U 192.168.1.206

            -bp 并行测试最好指定此参数，否则会引发“the socket ended by other party”异常


        3. 启动loach

           > cd loach/loach/instances
           >
           > python app.py

        4. 添加任务

           >  POST 127.0.0.1:8080/douyin/task/devices/

           参数

           ```
           {
             "1": {
                 "ip": "192.168.1.201",
                 "port": 5555,
                 "sip": "192.168.1.106",
                 "sport":4723
               },
             "2": {
                 "ip": "192.168.1.202",
                 "port": 5556,
                 "sip": "192.168.1.106",
                 "sport":4724
               },
             "3": {
                 "ip": "192.168.1.203",
                 "port": 5557,
                 "sip": "192.168.1.106",
                 "sport":4725
               },
             "4": {
                 "ip": "192.168.1.204",
                 "port": 5558,
                 "sip": "192.168.1.106",
                 "sport":4726
               },
             "5": {
                 "ip": "192.168.1.205",
                 "port": 5559,
                 "sip": "192.168.1.106",
                 "sport":4727
               },
             "6": {
                 "ip": "192.168.1.206",
                 "port": 5560,
                 "sip": "192.168.1.106",
                 "sport":4728
               }
           }
           ```

           > POST 127.0.0.1:8080/douyin/task/crawling/

           ```
           {
             "attrs":["following", "work", "like"]
           }
           ```










## loach http api

- 为什么要提供一组api来启动程序

  1. loach本身设计为任务驱动模型，需要有新的任务才能是loach继续运行。所以使用http来提供新的任务。
  2. 最初是没有这组API的，每次启动loach都需要启动若干appium实例（wifi模式还需要建立adb连接），繁琐的操作另每次重启都苦不堪言。

- HTTP API

  1. 添加设备 POST

     >  <url>/douyin/task/device/

     body

     ```python
     {
       "platform": "7.0",                  android版本
       "device_name": "TRT-AL00",          设备型号：设置-关于手机查看
       "device_type": "huawei-7",
       "ip": "192.168.1.103",              设备ip
       "port": 5555,                       设备port
       "sip": "192.168.1.100",             appium实例的ip
       "sport":4723,                       appium实例的port
       "udid":"36LBB18226509044"           设备序列号
     }
     ```

     **device_name****: 建立appium driver时需要此字段[capability](https://github.com/appium/appium/blob/master/docs/en/writing-running-appium/caps.md)

     **device_type**: 为了支持不同型号的设备，可选值：huawei-7、huawei-7p、nox（模拟器不再使用）

     **ip、port**：使用usb模式时，不需要无用，可以随便填，不重复

     **udid**：设备的序列号，使用adb devices命令可查看。appium实例依靠udid来区分设备，如果使用wifi模式启动，udid等于 ip:port 如192.168.1.103:5555

  2. 批量添加设备

     > <url>/douyin/task/device/

     body

     ```python
     {
     	"1": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7",
     		"ip": "192.168.1.103",
     		"port": 5555,
     		"sip": "192.168.1.100",
     		"sport": 4723,
     		"udid": "36LBB18226509044"
     	},
     	"2": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7",
     		"ip": "192.168.1.103",
     		"port": 5556,
     		"sip": "192.168.1.100",
     		"sport": 4724,
     		"udid": "36LBB18228500328"
     	},
     	"3": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7",
     		"ip": "192.168.1.103",
     		"port": 5557,
     		"sip": "192.168.1.100",
     		"sport": 4725,
     		"udid": "36LBB18228500503"
     	},
     	"4": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7",
     		"ip": "192.168.1.103",
     		"port": 5558,
     		"sip": "192.168.1.100",
     		"sport": 4726,
     		"udid": "36LBB18228500561"
     	},
     	"5": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7",
     		"ip": "192.168.1.100",
     		"port": 5559,
     		"sip": "192.168.1.100",
     		"sport": 4727,
     		"udid": "36LBB18228502964"
     	},
     	"6": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5560,
     		"sip": "192.168.1.100",
     		"sport": 4728,
     		"udid": "4NT7N17409032426"
     	},
     	"7": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5561,
     		"sip": "192.168.1.100",
     		"sport": 4729,
     		"udid": "4NT7N17425000937"
     	},
     	"8": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5562,
     		"sip": "192.168.1.100",
     		"sport": 4730,
     		"udid": "QDY4C17509000567"
     	},
     	"9": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5563,
     		"sip": "192.168.1.100",
     		"sport": 4731,
     		"udid": "QDY4C17509005281"
     	},
     	"10": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5564,
     		"sip": "192.168.1.100",
     		"sport": 4732,
     		"udid": "QDY4C17829010389"
     	},
     	"11": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5565,
     		"sip": "192.168.1.100",
     		"sport": 4733,
     		"udid": "QDY4C17930004703"
     	},
     	"12": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5566,
     		"sip": "192.168.1.100",
     		"sport": 4734,
     		"udid": "QDYNW17517006206"
     	},
     	"13": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5567,
     		"sip": "192.168.1.100",
     		"sport": 4735,
     		"udid": "QDYNW17517006280"
     	},
     	"14": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5568,
     		"sip": "192.168.1.100",
     		"sport": 4736,
     		"udid": "QDYNW17520004097"
     	},
     	"15": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5569,
     		"sip": "192.168.1.100",
     		"sport": 4737,
     		"udid": "QDYNW17C29017111"
     	},
     	"16": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5570,
     		"sip": "192.168.1.100",
     		"sport": 4738,
     		"udid": "4NT7N17401000802"
     	},
     	"17": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5571,
     		"sip": "192.168.1.100",
     		"sport": 4739,
     		"udid": "QDY4C17512006691"
     	},
     	"18": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5572,
     		"sip": "192.168.1.100",
     		"sport": 4740,
     		"udid": "QDYNW17628007515"
     	},
     	"19": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5573,
     		"sip": "192.168.1.100",
     		"sport": 4741,
     		"udid": "4NT4C17703000817"
     	},
     	"20": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5574,
     		"sip": "192.168.1.100",
     		"sport": 4742,
     		"udid": "4NT4C17809000246"
     	},
     	"21": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5575,
     		"sip": "192.168.1.100",
     		"sport": 4743,
     		"udid": "QDYNW17520004212"
     	},
     	"22": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5576,
     		"sip": "192.168.1.100",
     		"sport": 4744,
     		"udid": "QDYNW17518000037"
     	},
     	"23": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5577,
     		"sip": "192.168.1.100",
     		"sport": 4745,
     		"udid": "4NT4C17805011359"
     	},
     	"24": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5578,
     		"sip": "192.168.1.100",
     		"sport": 4746,
     		"udid": "QDY4C17814015503"
     	},
     	"25": {
     		"platform": "7.0",
     		"device_name": "TRT-AL00",
     		"device_type": "huawei-7p",
     		"ip": "192.168.1.103",
     		"port": 5579,
     		"sip": "192.168.1.100",
     		"sport": 4747,
     		"udid": "QDY7N17429001004"
     	}
     }
     ```

  3. 添加任务

     1. crawling任务

        > POST <url>:/douyin/task/crawling/

        body:

        ```python
        {
          "attrs":["comment", "author", "following", "follower", "work", "like"]
        }
        ```

        attrs：指定需要爬去的信息，可选值有以下

        "comment"：评论内容

        "author"：主播首页赞、关注数、粉丝数等主要信息

        "following"：关注列表，如果author没有指定，此字段即使指定也不生效

        "follower"： 粉丝列表，如果author没有指定，此字段即使指定也不生效

         "work"：历史作品，如果author没有指定，此字段即使指定也不生效

         "like"：喜欢作品，如果author没有指定，此字段即使指定也不生效

         “music”：使用的音乐的被使用数等主要信息

         “music_hot”：使用该音乐的最热作品，如果music没有指定，此字段即使指定也不生效

         “music_latest”: 使用该音乐的最新作品，如果music没有指定，此字段即使指定也不生效

     2. finding任务

        > POST <url>:/douyin/task/search/

        body

        ```python
        {
          "short_id":"29353709",
          "attrs":["follower","following","work","like"]
        }
        ```

        short_id: 可在account表中查询

        attrs：类似crawling任务，可选值"follower","following","work","like"

        **如果需要批量添加搜索任务**

        > POST <url>:/douyin/task/searches/

        body

        ```python
        [
            {
        	    "short_id": "29353709",
        	    "attrs": ["follower", "following", "work", "like"]
            },
            {
        	    "short_id": "29353709",
        	    "attrs": ["follower", "following", "work", "like"]
            },
            {
        	    "short_id": "29353709",
        	    "attrs": ["follower", "following", "work", "like"]
            },
            {
        	    "short_id": "29353709",
        	    "attrs": ["follower", "following", "work", "like"]
            }
        ]
        ```

        出错重试五次

     3. 私信任务

        > POST <url>:/douyin/task/kol_letter/?udid=4NT7N17401000802

        udid: 指定某个设备来执行此任务

        body

        ```
        [
          {
          "short_id":"1076686584",
          "words":"dijia"
        },
          {
          "short_id":"1076686584",
          "words":"lucky"
        },
          {
          "short_id":"1076686584",
          "words":"my baby"
        },
          {
          "short_id":"1076686584",
          "words":"you are dog"
        },
          {
          "short_id":"1076686584",
          "words":"fuck yourself"
        }
          ]
        ```

        short_id: 私信的对象

        words：私信的内容

     4. 话题任务

        > POST <url>:/douyin/task/category/?task_num=500

         task_num：添加500次话题任务，每次任务滑动700次。

        **所有任务相关的api，都支持设置timeout**

        如： <url>:/douyin/task/category/?task_num=500&timeout=30

        默认时，任务会一直等待设备就绪

  4. 启动/停止第三方工具

     	> GET <url>:/start/
     	>
     	> 已经启动的程序不会重启

     > GET <url>:/stop/
     >
     > GET <url>:/restart/
     >
     > 已经启动的程序会kill在start

  5. 检查loach运行状态

     > GET <url>:/douyin/task/stat/

     返回信息有所有设备运行状态，任务队列，appium实例

     ```
     {
         "stat": [
             {
                 "ip": "192.168.1.103",
                 "port": 5555,
                 "sip": "192.168.1.100",
                 "sport": 4723,
                 "udid": "36LBB18226509044",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "d70ce834d07849a18a652e5f4defaeb0",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5556,
                 "sip": "192.168.1.100",
                 "sport": 4724,
                 "udid": "36LBB18228500328",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "a5a6c6f96ad940af82f60f1ca3daaeb1",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5557,
                 "sip": "192.168.1.100",
                 "sport": 4725,
                 "udid": "36LBB18228500503",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "721dbc9b32b14c8697eb36079afbf9a5",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5558,
                 "sip": "192.168.1.100",
                 "sport": 4726,
                 "udid": "36LBB18228500561",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "4e1553abda4c49c1ac54e99e9549d081",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.100",
                 "port": 5559,
                 "sip": "192.168.1.100",
                 "sport": 4727,
                 "udid": "36LBB18228502964",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "85c365db62e74bcdb70f867c1fe3ea25",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5560,
                 "sip": "192.168.1.100",
                 "sport": 4728,
                 "udid": "4NT7N17409032426",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "f9e49966e3cc44d3aec2022969a21cb3",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5561,
                 "sip": "192.168.1.100",
                 "sport": 4729,
                 "udid": "4NT7N17425000937",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "1bcc9e2211134a94ae2a86240ced92f1",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5562,
                 "sip": "192.168.1.100",
                 "sport": 4730,
                 "udid": "QDY4C17509000567",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "b5351a61ec794d90abfbc91419b21864",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5563,
                 "sip": "192.168.1.100",
                 "sport": 4731,
                 "udid": "QDY4C17509005281",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "698c94e1f6384c97893d3e71e7d1d852",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5564,
                 "sip": "192.168.1.100",
                 "sport": 4732,
                 "udid": "QDY4C17829010389",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "686fbc44e9bf44ada60a4690495dad27",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5565,
                 "sip": "192.168.1.100",
                 "sport": 4733,
                 "udid": "QDY4C17930004703",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "1810d80c6d3f476eb6b6464fdcbf9c39",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5566,
                 "sip": "192.168.1.100",
                 "sport": 4734,
                 "udid": "QDYNW17517006206",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "17235eee316c4ea2b71baddb9e0c734d",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5567,
                 "sip": "192.168.1.100",
                 "sport": 4735,
                 "udid": "QDYNW17517006280",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "a9a69287d4d0400ca1d94444026a0e32",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5568,
                 "sip": "192.168.1.100",
                 "sport": 4736,
                 "udid": "QDYNW17520004097",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "1a85ecf6dcd34fd383bab4e3f467f993",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5569,
                 "sip": "192.168.1.100",
                 "sport": 4737,
                 "udid": "QDYNW17C29017111",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "e9a2c9f45a78451984f3125e627a4ff7",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5570,
                 "sip": "192.168.1.100",
                 "sport": 4738,
                 "udid": "4NT7N17401000802",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "3ef5ad357e8d4b2cac6996b2720ff599",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5571,
                 "sip": "192.168.1.100",
                 "sport": 4739,
                 "udid": "QDY4C17512006691",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "cab30413ec10451da4e17a7bcba1448d",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5572,
                 "sip": "192.168.1.100",
                 "sport": 4740,
                 "udid": "QDYNW17628007515",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "b5e5aea632be44ef9959382d18314d26",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5573,
                 "sip": "192.168.1.100",
                 "sport": 4741,
                 "udid": "4NT4C17703000817",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "36e1a5dffb7c47b48f123f2920bf2387",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5574,
                 "sip": "192.168.1.100",
                 "sport": 4742,
                 "udid": "4NT4C17809000246",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "014c82cf5e424e59b0ee5717ab1f9079",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5575,
                 "sip": "192.168.1.100",
                 "sport": 4743,
                 "udid": "QDYNW17520004212",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 2,
                     "data": {
                         "attrs": [
                             "comment",
                             "author",
                             "following",
                             "follower",
                             "work",
                             "like"
                         ]
                     },
                     "uuid": "8b891a46d4d54c0b9e66d1a1519e3355",
                     "app_name": "douyin",
                     "timeout": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5576,
                 "sip": "192.168.1.100",
                 "sport": 4744,
                 "udid": "QDYNW17518000037",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 16,
                     "uuid": "f24d958a136b418b84d945e6d82e0922",
                     "app_name": "douyin",
                     "timeout": null,
                     "data": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5577,
                 "sip": "192.168.1.100",
                 "sport": 4745,
                 "udid": "4NT4C17805011359",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 16,
                     "uuid": "f24d958a136b418b84d945e6d82e0922",
                     "app_name": "douyin",
                     "timeout": null,
                     "data": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5578,
                 "sip": "192.168.1.100",
                 "sport": 4746,
                 "udid": "QDY4C17814015503",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 16,
                     "uuid": "f24d958a136b418b84d945e6d82e0922",
                     "app_name": "douyin",
                     "timeout": null,
                     "data": null,
                     "udid": null
                 }
             },
             {
                 "ip": "192.168.1.103",
                 "port": 5579,
                 "sip": "192.168.1.100",
                 "sport": 4747,
                 "udid": "QDY7N17429001004",
                 "platform": "7.0",
                 "device_name": "TRT-AL00",
                 "device_type": "huawei-7p",
                 "app": "DouYinApp_2_1_1",
                 "stat": 2,
                 "task": {
                     "task_type": 16,
                     "uuid": "f24d958a136b418b84d945e6d82e0922",
                     "app_name": "douyin",
                     "timeout": null,
                     "data": null,
                     "udid": null
                 }
             }
         ],
         "waiting_tasks": 1995,
         "appium": [
             "node.exe                      6752 Console                    1    111,088 K\n",
             "node.exe                      6804 Console                    1    107,908 K\n",
             "node.exe                      8160 Console                    1    108,608 K\n",
             "node.exe                      7940 Console                    1    107,612 K\n",
             "node.exe                      8188 Console                    1    107,220 K\n",
             "node.exe                      4036 Console                    1    112,516 K\n",
             "node.exe                      6600 Console                    1    107,896 K\n",
             "node.exe                      6524 Console                    1    110,748 K\n",
             "node.exe                      6456 Console                    1    108,280 K\n",
             "node.exe                      6764 Console                    1    109,412 K\n",
             "node.exe                      1016 Console                    1    109,800 K\n",
             "node.exe                      6024 Console                    1    111,980 K\n",
             "node.exe                      5932 Console                    1    107,936 K\n",
             "node.exe                      4340 Console                    1    108,460 K\n",
             "node.exe                      5916 Console                    1    107,552 K\n",
             "node.exe                      5820 Console                    1    107,344 K\n",
             "node.exe                      5528 Console                    1    107,700 K\n",
             "node.exe                      5560 Console                    1    104,240 K\n",
             "node.exe                      4904 Console                    1    102,164 K\n",
             "node.exe                      5208 Console                    1    103,464 K\n",
             "node.exe                      5224 Console                    1    105,956 K\n",
             "node.exe                      5152 Console                    1    103,884 K\n",
             "node.exe                      5404 Console                    1    103,232 K\n",
             "node.exe                      3488 Console                    1    105,080 K\n",
             "node.exe                      7124 Console                    1    102,836 K\n"
         ]
     }
     ```









