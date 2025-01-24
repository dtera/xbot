`xbot`是一个基于企业微信的机器人。

它可以接收用户的命令并触发相应的服务，用于**触发任务、查询信息**，如查看服务器状态、重启服务器、触发脚本等。

**目的就是为了减轻个人的重复工作负担，提高工作效率。**

## 使用方法

这是一个简单的框架，你自己用ChatGPT可能半天也能搞出来。不过如果这些代码可以满足你的需求，你也可以拿去直接用。

用法很简单:

1. fork 本项目
2. 修改 `config.py` 文件，填入企业微信的相关信息
    - 场景模块文件所在目录：``scene_dirs``
    - 特殊对话的前缀以及处理函数：``special_line_prefix``
    - 企业微信相关信息
3. 在 `services` 等 `scene_dirs` 指定的目录下添加你的服务模块代码
4. 修改local.db，添加特殊的权限控制
5. 运行 `PYTHONPATH=.. python -m xbot.wecom_app` 启动服务

以上需要部署到服务器上，然后在企业微信后台配置回调地址，具体的部署和配置方式看这里：
《[企业微信机器人回调服务](https://github.com/easy-wx/wecom-bot-svr?tab=readme-ov-file#%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%9B%9E%E8%B0%83%E6%9C%8D%E5%8A%A1)》

## 设计

本地提供一个HTTP服务，用于接收企业微信(或其他IM工具)的消息推送。

### 通用对话格式

对话遵循以下格式：

``[scene] [cmd] [args]``

其中，`scene` 是场景，`cmd` 是命令，`args` 是参数。

每个 ``scene`` 对应一个 Python 模块；而在模块中，cmd的处理函数命名为 ``cmd_`` + cmd。这样带来了方便：可以动态的添加命令。

为了更清晰地组织代码，你可以将不同的场景放在多个目录中，只要你在 `__init__.py` 文件中，将对应目录追加到 scene_dirs 即可。

框架会按照目录顺序进行搜索，如果有模块名冲突，优先使用排列靠前的模块。
比如，项目的初始创建了 services 和 activities 两个目录，用来存放不同服务和活动级别的场景模块。

有一个特殊的目录——``public``，用来存放不敏感的公用接口。

``common`` 目录则用来存放公共的函数和类。

### 内部对话格式

有些特殊情况，可能不遵循通用对话格式，比如可以将某些对话接入大语言模型，我们可以使用 `@` 开头让服务知道，需要处理这种特殊服务。

```
@介绍一下北京
```

### 对话服务适配与消息处理的分离

设计上，独立消息处理和服务处理：消息处理负责解析消息，服务处理负责处理业务逻辑。

这样，可以快速的构建企业微信之外、别的即时通信工具对话的服务。

## 权限管理

因为企业微信能够获得用户ID，所以通过 scene + cmd + 日期的方式，对用户进行授权。

本地有 ``db.sqlite3``文件进行管理。TODO 提供个通过何种方式同步？

只有授权用户才能进行对话，否则提示错误。

## HELP 指令

- ``help``，列出所有的命令。
- ``help [scene]``，列出该场景下所有命令字。
- ``help [scene] [cmd]``，列出指定命令的详细帮助信息。

## Docker 部署

不使用流水线，直接推送Docker镜像，注意将仓库设置为私有。

构建：

```bash
docker build --network="host" -t jasonzxpan/xbot .
```

如果在当前目录运行，可以直接将目录映射到 /data/xbot：

```bash
docker run -i -v $PWD:/data/xbot -t jasonzxpan/xbot /bin/bash
```

## 真实场景举例