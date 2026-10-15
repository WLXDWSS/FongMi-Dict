# 工具说明

## update.py — 一键更新字典

抓取全部公开线路 → 校验 → 重新生成 `config/*.json`、`live/live-sources.txt`、`docs/线路清单.md`。

```bash
python tools/update.py
```

Windows 可直接双击 `update.bat`。

### 依赖

- Python 3.8+
- 系统 `curl`（Windows 10/11 自带；Linux/macOS 一般也有）

无需 pip 安装任何包（只用标准库 + curl）。

### 它会做什么

1. 拉取 22 条线路的配置，剥离 `//` 注释后解析；
2. 把**相对路径**全部转成绝对地址（支持三种写法：`./lib/x.json`、`a.json$$$b.json`、`{'token':'./lib/token.json'}` 这类内嵌字典字符串）；
3. 给每个站点**绑定它原线路的爬虫包（jar）**——合并后全局 `spider` 不再通用，这一步不做站点会全废；
4. 逐个校验爬虫包 / 扩展文件是否真的能下载：
   - `404 / 410` 才算「文件不存在」→ 剔除该站点
   - `403 / 超时 / 200+空内容` 视为限流或网络问题 → 重试并切换加速器（`ghproxy.net` ⇄ `gh-proxy.com`）
   - 目录改名导致的失效路径，会尝试 `libs/js/`、`libs/`、`js/`、`lib/`、`json/` 补救
5. 合并去重（先按 `key` 再按 `name`，站点多的线路优先）；
6. 写入配置，并在 `docs/线路清单.md` 里输出本次实测数据。

### 输出

| 文件 | 内容 |
|---|---|
| `config/multi.json` | 多仓总配置（22 条线路） |
| `config/all-in-one.json` | 全能合并单仓（全部站点 + 直播） |
| `config/multi-plus.json` | 含子仓库与备用线路（31 条） |
| `live/live-sources.txt` | 直播源地址清单 |
| `docs/线路清单.md` | 本次实测数据（站点数、可用性） |

**不启动任何常驻服务**，只生成文件。

### 缓存

`tools/httpcache/` 会缓存抓取成功的文件，重复运行会快很多。已加入 `.gitignore`，可随时删除。

### 中国大陆网络提示

- `raw.githubusercontent.com` 直连不通，脚本默认走 `ghproxy.net` / `gh-proxy.com` 加速。
- 若本机有代理，脚本会用 `127.0.0.1:7892` 兜底（见 `update.py` 顶部的 `PROXY` 常量，可自行修改或删除）。
- DNS 被污染时脚本会用 DoH（`dns.alidns.com` / `doh.pub`）解析真实 IP 重试。

## gen_qr.py — 重新生成二维码

```bash
pip install qrcode pillow
python tools/gen_qr.py
```

生成到 `qrcode/`。二维码内容必须是 `http` 开头的地址（FongMi 扫码导入的限制）。
