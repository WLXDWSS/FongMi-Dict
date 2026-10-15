# FongMi 影视 · 配置字典

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Sites](https://img.shields.io/badge/%E7%AB%99%E7%82%B9-1171-brightgreen.svg)
![Live](https://img.shields.io/badge/%E7%9B%B4%E6%92%AD%E6%BA%90-14%20%E8%B7%AF%20%C2%B7%208541%20%E9%A2%91%E9%81%93-orange.svg)
![Lines](https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF%E7%BA%BF%E8%B7%AF-22%20%E6%9D%A1-blue.svg)
[![FongMi](https://img.shields.io/badge/%E5%AE%A2%E6%88%B7%E7%AB%AF-FongMi%20%E8%9C%82%E8%9C%9C%E5%BD%B1%E8%A7%86-important.svg)](https://github.com/FongMi/TV)

一套为安卓手机 / 电视盒子 **FongMi（蜂蜜影视）** 整理的影视配置字典（单仓 / 多仓 / 直播源）。

**所有线路、爬虫包、扩展文件都经过实测校验**：可达性、spider 的 md5 与线上字节一致、站点扩展文件逐个探测、直播源逐路数频道数。
**完全不需要电脑当服务器** —— 文件放手机里直接用，或直接粘贴公网接口地址。

> 最近更新：见 [线路清单.md](docs/线路清单.md)（每次运行 `tools/update.py` 自动刷新实测数据）

---

## 🔖 订阅地址（本仓库 · 免传文件）

直接把下面的地址粘到 FongMi 的 **设置 → 点播 → 请输入配置…** 里，点确定即可，**不用传文件、不用自建服务器**：

```
# ⭐ 多仓总配置（22 条线路，可在软件里随时切换）—— 日常首选
https://ghproxy.net/https://raw.githubusercontent.com/WLXDWSS/FongMi-Dict/main/config/multi.json

# 全能合并单仓（1171 站点 + 134 解析 + 14 路直播）
https://ghproxy.net/https://raw.githubusercontent.com/WLXDWSS/FongMi-Dict/main/config/all-in-one.json

# 多仓增强版（22 条线路 + 5 个公开多仓 + 4 条备用 = 31 条）
https://ghproxy.net/https://raw.githubusercontent.com/WLXDWSS/FongMi-Dict/main/config/multi-plus.json
```

> 上面走 `ghproxy.net` 加速（国内直连 `raw.githubusercontent.com` 常不通）。加速器挂了可换：
> 把 `https://ghproxy.net/https://raw.githubusercontent.com/…` 换成
> `https://gh-proxy.com/https://raw.githubusercontent.com/…`，
> 或用 jsDelivr：`https://fastly.jsdelivr.net/gh/WLXDWSS/FongMi-Dict@main/config/multi.json`
>
> 只想要直播：`live/live-sources.txt` 里的地址填到 **设置 → 直播**。

---

## ⚠️ 免责声明（请先读）

- 本项目**不生产、不存储、不传播任何影视内容**，只是把互联网上**公开分享**的接口地址、爬虫包、直播源做**抓取、校验与整理**。
- 所有资源的版权归各自原作者所有；本项目与 [FongMi](https://github.com/FongMi/TV) 官方**没有任何关系**。
- 仅供个人学习与技术测试使用，**请勿用于商业用途，请于 24 小时内删除**。
- 若原作者不希望被收录，提 Issue 告知，会立即移除。

---

## 🔗 相关项目（上游）

| 项目 | 地址 | 说明 |
|---|---|---|
| **FongMi 影视（源码）** | <https://github.com/FongMi/TV> | 本字典对应的客户端，安卓 TV / 手机播放器 |
| **FongMi 发布页（APK）** | <https://github.com/FongMi/Release> | 官方安装包下载（手机版 / 电视版 / 各架构） |
| **FongMi 爬虫库** | <https://github.com/FongMi/CatVodSpider> | 官方 spider jar 与配置示例 |
| TVBox 系其他客户端 | <https://github.com/o0HalfLife0o/TVBoxOSC> | 影视仓 / OK影视 等同样可用的空壳客户端 |

> 配置格式（`sites` / `lives` / `parses` / `spider` / `urls` 多仓）在 TVBox 系客户端之间通用。

---

## 📁 目录结构

```
.
├── config/
│   ├── multi.json          # ⭐ 多仓总配置：22 条线路，导入一次即可在软件里切换
│   ├── all-in-one.json     # 全能合并单仓：1171 个站点 + 134 个解析 + 14 路直播
│   └── multi-plus.json     # 多仓增强版：22 条线路 + 5 个公开多仓 + 4 条备用（共 31 条）
├── live/
│   └── live-sources.txt    # 14 路直播源地址（约 8541 个频道）
├── docs/
│   ├── 使用说明.md          # 详细中文教程：导入步骤、FAQ、已知限制
│   ├── 在线接口地址.txt      # 全部接口地址纯文本，可直接复制粘贴
│   └── 线路清单.md          # 线路实测数据（站点数、特点、可用性）
├── qrcode/                 # 每个接口一张二维码（用系统相机/微信扫，读出地址免手输）
└── tools/
    ├── update.py           # 一键重新抓取 + 校验 + 生成全部配置
    ├── update.bat          # Windows 双击运行
    └── gen_qr.py           # 重新生成二维码
```

---

## 🚀 快速开始

### 方式一：本地文件导入（推荐，最稳定）

1. 下载本仓库的 `config/multi.json`（点文件 → 右上角 `Raw`/`Download`）传到手机；
2. 打开 **FongMi** → 首页右上角 **设置** → **点播**；
3. 在 `请输入配置…` 输入框**右侧的小图标（选择文件）**里选中刚传进来的 json；
4. 点 **确定** → 返回首页，等待自动加载（首次会下载爬虫包，约 20–30 MB，10～60 秒）。

> 换配置：再点一次「点播」，长按输入框可编辑/清空。

### 方式二：直接粘贴在线地址（不用传文件）

把下面任意一条粘贴到 `请输入配置…` 里，点确定即可：

```
# 高天流云·聚合JS（298 站点，覆盖最广）
https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json

# 老刘备（234 站点，长期维护）
https://ghproxy.net/https://raw.githubusercontent.com/liu673cn/box/main/m.json

# 王二小（99 站点，4K 多）
https://9280.kstore.vip/aiwex.json

# clun（97 站点 + 17 路直播）
https://clun.top/box.json
```

完整清单见 [docs/在线接口地址.txt](docs/在线接口地址.txt)。

> ⚠️ **国内直连 `raw.githubusercontent.com` 不通**，所以本仓库里的 GitHub 类地址统一走 `ghproxy.net` / `gh-proxy.com` 加速。

### 方式三：二维码免手输

用手机**系统相机**或**微信扫一扫**扫 `qrcode/` 里的图片 → 读出地址 → 复制粘贴到 FongMi。

> 注意：FongMi 自带的扫码功能只用于**投屏/同步**（源码里 `ScanActivity` 只被 `CastDialog`/`SyncDialog` 调用），**不能扫码导入配置**。

---

## 📺 线路一览（实测）

| 线路 | 站点数 | 特点 |
|---|---|---|
| ①高天流云·聚合JS | 298 | 覆盖最广，爬虫源 + JS 源，电影/剧集/综艺/动漫/纪录片全覆盖 |
| ②老刘备 | 234 | 长期维护，含磁力/P2P/听书等特殊分类 |
| ③影视仓聚合 | 167 | 聚合肥猫/王二小/4K小盒子等 10 家，含 4K 专区 |
| ④高天流云·PG | 135 | PG 网盘专线，1080P/4K 高码率资源多 |
| ⑤王二小 | 99 | 含大量 4K 频道，秒播体验好 |
| ⑥网络接口 | 98 | 老牌稳定接口 |
| ⑦clun | 97 | 17 条直播线路 + 21 个解析 |
| ⑧高天流云·多线 | 86 | 16 条直播线路 + 11 解析，多线冗余 |
| ⑨PG综合 | 74 | 29 条直播线路，体育/影视兼备 |
| ⑩noimank | 64 | 24 个解析接口，失效自动切换 |
| ⑪~㉒ | 24–63 | 王二小域名版 / 小盒子 / 高天流云 FTY·XYQ / 香雅情 / 半糖仙人 / 菜妮丝 / FongMi专版 / 肥猫 / tushen6 / 高天流云 FM / 俊于 |

**多仓**：小盒子(12仓)、蜗牛(27仓)、游魂(24仓)、tvyuan(27仓)、FanchangWang(8仓)
**备用**：摸鱼儿、tvyuan 全量(1356 站点)、饭太硬、菜妮丝备用域名

> 完整实测数据（含合并后保留数、可用性）见 [docs/线路清单.md](docs/线路清单.md)。

---

## 📡 直播源（14 路 · 约 8541 频道）

| 直播源 | 频道数 | 直播源 | 频道数 |
|---|---|---|---|
| BigBigGrandG-综合 | 1956 | iptv-org-中国 | 508 |
| Guovin-IPTV | 1619 | 芒果TV | 197 |
| 苏香-myIPTV | 1273 | YanG-1989 | 123 |
| huyayqk | 1119 | Kimentanm | 120 |
| ibert-ALL | 723 | YueChan-Live | 96 |
| vbskycn-IPTV4 | 679 | 如意TV / FYTV | 79 / 49 |

地址见 [live/live-sources.txt](live/live-sources.txt)。IPV6 类源需要手机网络支持 IPV6。

---

## 🔄 更新

影视源时效性强（通常几周就变）。重新抓取并校验全部线路：

```bash
python tools/update.py        # 需要 Python 3.8+ 与 curl
# 或 Windows 双击 tools/update.bat
```

脚本会：抓取 22 条线路 → 解析并剥离注释 → 把相对路径绝对化（含内嵌字典字符串）→ 给每个站点绑定其原线路的爬虫包 → 逐个校验爬虫包/扩展文件可达性 → 合并去重 → 生成 `config/*.json`、`live/*.txt`、`docs/线路清单.md`。
**只生成文件，不启动任何常驻服务。**

---

## 🧩 已知限制（如实说明）

- 约 15 个站点的爬虫包托管在第三方镜像（`tv.nxog.top`、`rihou.vip`、`agit.ai` 等），部分网络环境访问不到；打不开不影响其余 1150+ 站点。
- `tvyuan 全量`（1356 站点）与 `饭太硬` 在部分网络无法直连，已放入备用线路。
- 合并单仓中剔除了 74 个上游配置里**指向的文件已不存在**（HTTP 404）的站点——这些站点在原线路里同样打不开。
- 常用 EPG 源在部分网络不通，不影响看电视直播。

---

## 🙏 数据来源

所有接口整理自互联网公开分享，主要来源包括 `gaotianliuyun/gao`、`liu673cn/box`、`Lightconer/tvbox-ysc-config`、`xyq254245/xyqonlinerule`、`tushen6/Tomorrow`、`noimank/tvbox` 等公开仓库与各位不知名的维护者。**感谢所有原作者的付出。**

---

## 📄 License

[MIT](LICENSE) —— 仅适用于本仓库的**脚本与文档**；`config/`、`live/`、`qrcode/` 中的接口地址、爬虫包、直播源版权归各自原作者所有。
