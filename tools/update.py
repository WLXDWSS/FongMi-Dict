#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FongMi 字典 一键更新工具
功能：抓取全部公开线路 → 校验爬虫包/扩展文件可达性 → 重新生成字典文件
用法：双击 更新字典.bat  或  python 更新字典.py
说明：只做「抓取 + 校验 + 生成文件」，不启动任何常驻服务，不需要电脑当服务器。
"""
import json, os, re, sys, time, hashlib, subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlsplit
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # 仓库根目录
OUT = os.path.join(ROOT, "config")           # 生成的配置（多仓/单仓）
DOCS = os.path.join(ROOT, "docs")            # 说明与清单
LIVE = os.path.join(ROOT, "live")            # 直播源地址
UA = "okhttp/3.12.13"
PROXY = "http://127.0.0.1:7892"
GH = "https://ghproxy.net/"

# 已实测公网可达的线路：(显示名, 最终URL, body文件, 备注)
SOURCES = [
    ("①高天流云·聚合JS", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json", "高天流云_聚合JS", "298站点，覆盖最广"),
    ("②老刘备", "https://ghproxy.net/https://raw.githubusercontent.com/liu673cn/box/main/m.json", "老刘备-ghproxy", "234站点，长期维护"),
    ("③影视仓聚合", "https://ghproxy.net/https://raw.githubusercontent.com/Lightconer/tvbox-ysc-config/main/output/%E5%8D%95%E4%BB%93%E8%81%9A%E5%90%88.json", "影视仓聚合", "167站点，聚合肥猫/王二小等10家"),
    ("④高天流云·PG", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0825.json", "高天流云_PG", "135站点，网盘高码率"),
    ("⑤王二小", "https://9280.kstore.vip/aiwex.json", "王二小-aiwex", "99站点，4K多"),
    ("⑥网络接口", "https://8815.kstore.vip/tvbox/wmz", "网络接口-wmz", "98站点，老牌稳定"),
    ("⑦clun", "https://clun.top/box.json", "clun", "97站点，直播17路"),
    ("⑧高天流云·多线", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0821.json", "高天流云_多线", "86站点，多线冗余"),
    ("⑨PG综合", "https://www.252035.xyz/p/jsm.json", "PG综合252035", "74站点，直播29路"),
    ("⑩noimank", "https://gitlab.com/noimank/tvbox/-/raw/main/tvbox1.json", "noimank", "64站点，解析24个"),
    ("⑪王二小·域名版", "http://tvbox.王二小放牛娃.top", "王二小-域名", "63站点"),
    ("⑫小盒子", "http://xhztv.top/xhz", "小盒子-xhz", "54站点"),
    ("⑬高天流云·FTY", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0826.json", "高天流云_FTY", "51站点，饭太硬同源"),
    ("⑭高天流云·XYQ", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/XYQ.json", "高天流云_XYQ", "49站点，香雅情同源"),
    ("⑮香雅情", "https://gh-proxy.com/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json", "香雅情", "48站点，老片多"),
    ("⑯半糖仙人", "https://raw.giteeusercontent.com/ph7368/ok/raw/master/%E5%8D%8A%E7%B3%96%E4%BB%99%E4%BA%BA.json", "半糖仙人", "46站点，直播18路"),
    ("⑰菜妮丝", "https://tv.xn--yhqu5zs87a.top", "菜妮丝", "46站点"),
    ("⑱FongMi专版", "https://www.252035.xyz/z/FongMi.json", "FongMi专版", "43站点，专为FongMi适配"),
    ("⑲肥猫", "http://肥猫.net/", "肥猫-net", "39站点"),
    ("⑳tushen6", "https://ghproxy.net/https://raw.githubusercontent.com/tushen6/Tomorrow/master/tvbox.json", "tushen6", "33站点，OK影视同源"),
    ("㉑高天流云·FM", "https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json", "高天流云_FM", "33站点，FongMi官方jar"),
    ("㉒俊于", "http://home.jundie.top:81/top98.json", "俊于", "24站点，冷门老片"),
]

# 已实测可达的多仓/子仓库
DEPOTS = [
    ("小盒子多仓(12仓)", "http://xhztv.top/DC.txt"),
    ("蜗牛多仓(27仓)", "https://tv.%E8%9C%97%E7%89%9B.top/DS"),
    ("游魂多仓(24仓)", "https://www.iyouhun.com/tv/dc"),
    ("tvyuan多仓(27仓)", "https://gitee.com/onm-hundred-and-eleven/tvyuan/raw/main/tvbox_multi.json"),
    ("FanchangWang多仓(8仓)", "https://gh-proxy.com/https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/dist/tvbox.json"),
]

# 备用线路（本机网络不可直连，手机运营商网络下大概率可用）
BACKUP_LINES = [
    ("备用·摸鱼儿", "http://我不是.摸鱼儿.top", "100站点，更新极快"),
    ("备用·tvyuan全量", "https://tv.cc0cd.cc.cd", "1356站点/129直播，最全但需网络可达"),
    ("备用·饭太硬", "http://www.饭太硬.net/tv", "老牌接口"),
    ("备用·菜妮丝旧域", "https://tv.菜妮丝.top", "菜妮丝备用域名"),
]

PATH_EXT = re.compile(r"^(\.\./|\./)?[\w\u4e00-\u9fa5\-./]+\.(js|json|txt|py|m3u|m3u8)$", re.I)


def curl(url, extra=None, timeout=25):
    cmd = ["curl", "-sSL", "-m", str(timeout), "--compressed", "-A", UA]
    if extra:
        cmd += extra
    cmd += ["-o", "-", "-w", "\n@@@%{http_code}|%{size_download}", url]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        return "TO", b""
    out = p.stdout
    m = out.rfind(b"\n@@@")
    body = out[:m] if m >= 0 else out
    meta = out[m + 4:].decode("utf-8", "replace").split("|") if m >= 0 else ["?", "0"]
    return meta[0], body


def doh_ip(host):
    for ep in ("https://dns.alidns.com/resolve?name=%s&type=A", "https://doh.pub/dns-query?name=%s&type=A"):
        try:
            st, b = curl(ep % host, extra=["-H", "accept: application/dns-json"], timeout=10)
            d = json.loads(b.decode("utf-8", "replace"))
            ips = [a["data"] for a in d.get("Answer", []) if a.get("type") == 1]
            if ips:
                return ips[0]
        except Exception:
            continue
    return None


_CACHE = {}


def fetch_public(url, timeout=30):
    """公网可达性：直连 → DoH解析重试 → 本机代理兜底。返回 (how, bytes)"""
    if url in _CACHE:
        return _CACHE[url]
    st, b = curl(url, timeout=timeout)
    if st == "200" and len(b) > 0:
        _CACHE[url] = ("direct", b)
        return _CACHE[url]
    host = urlsplit(url).hostname
    if host:
        ip = doh_ip(host)
        if ip:
            port = urlsplit(url).port or (443 if url.startswith("https") else 80)
            st2, b2 = curl(url, extra=["--resolve", "%s:%s:%s" % (host, port, ip)], timeout=timeout)
            if st2 == "200" and len(b2) > 0:
                _CACHE[url] = ("doh", b2)
                return _CACHE[url]
    st3, b3 = curl(url, extra=["-x", PROXY], timeout=timeout)
    if st3 == "200" and len(b3) > 0:
        _CACHE[url] = ("proxy", b3)
        return _CACHE[url]
    _CACHE[url] = ("fail", b"")
    return _CACHE[url]


def strip_json(txt):
    txt = txt.lstrip("\ufeff")
    txt = re.sub(r"(?m)^\s*//.*$", "", txt)
    txt = re.sub(r"(?m)^\s*#.*$", "", txt)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r",(\s*[}\]])", r"\1", txt)
    return txt.strip()


def load_body(fn):
    """fn 为 URL：实时抓取并解析线路配置"""
    how, data = fetch_cached(fn)
    if not data:
        raise IOError("抓取失败: %s" % fn)
    raw = data.decode("utf-8", "replace")
    s = strip_json(raw)
    i = min([p for p in (s.find("{"), s.find("[")) if p >= 0] or [-1])
    try:
        return json.loads(s[i:])
    except Exception as e:
        print("  !! %s 解析失败 %s" % (fn, e))
        return None


def join_abs(base, rel):
    """把相对路径拼到 base 上，保留 base 中的 'https://' 双斜杠（urljoin 会吃掉它）"""
    r = rel.strip()
    if not r or "://" in r:
        return r
    d = base if base.endswith("/") else base.rsplit("/", 1)[0] + "/"
    while r.startswith("./"):
        r = r[2:]
    while r.startswith("../"):
        r = r[3:]
        d = d.rstrip("/").rsplit("/", 1)[0] + "/"
    return d + r


EMBED = re.compile(r"(?:\.\./|\./)[\w一-龥\-./]+\.(?:js|json|txt|py|jar|m3u|m3u8)", re.I)


def resolve_abs(base, val, force=False):
    """把相对路径解析为公网绝对地址；返回 (新值, 需要校验的URL列表)
    支持三种形态：
      1) 纯相对路径      ./lib/x.json
      2) $$$ 分隔的多段   ./a.json$$$null$$$proxy$$$1
      3) 内嵌于字典字符串 {'token': './lib/token.json', 'json': './json/x.json'}
    force=True 用于 jar 字段（扩展名可能是 .png/.jpg 等）"""
    if not isinstance(val, str):
        return val, []
    v = val.strip()
    if not v:
        return val, []
    parts, check = [], []
    for p in v.split("$$$"):
        ps = p.strip()
        if not ps:
            parts.append(p)
            continue
        if ps.startswith(("http://", "https://", "assets", "file")):
            parts.append(p)
            continue
        if force:
            key = ps.split(";md5;")[0].strip()
            if key and "://" not in key:
                u = join_abs(base, key)
                parts.append(u + ps[len(key):])
                check.append(u)
                continue
            parts.append(p)
            continue
        if PATH_EXT.match(ps):
            u = join_abs(base, ps)
            parts.append(u)
            check.append(u)
            continue

        def _rep(m, base=base):
            u = join_abs(base, m.group(0))
            check.append(u)
            return u

        parts.append(EMBED.sub(_rep, p) if EMBED.search(p) else p)
    return "$$$".join(parts), check


def fetch_no_proxy(url, timeout=30):
    """只走公网（直连 → DoH），不依赖本机代理"""
    st, b = curl(url, timeout=timeout)
    if st == "200" and len(b) > 0:
        return "direct", b
    host = urlsplit(url).hostname
    if host:
        ip = doh_ip(host)
        if ip:
            port = urlsplit(url).port or (443 if url.startswith("https") else 80)
            st2, b2 = curl(url, extra=["--resolve", "%s:%s:%s" % (host, port, ip)], timeout=timeout)
            if st2 == "200" and len(b2) > 0:
                return "doh", b2
    return "fail", b""


CACHE_DIR = os.path.join(HERE, "httpcache")


def _ck(url):
    return os.path.join(CACHE_DIR, hashlib.md5(url.encode("utf-8")).hexdigest())


def fetch_cached(url, timeout=30, proxy_ok=True):
    """带磁盘缓存的公网抓取：命中缓存直接返回，避免重跑时重复请求"""
    k = _ck(url)
    meta = k + ".json"
    if os.path.exists(meta):
        try:
            d = json.load(open(meta, encoding="utf-8"))
            if d.get("how") != "fail":
                return d["how"], open(k, "rb").read()
            return "fail", b""
        except Exception:
            pass
    how, data = fetch_no_proxy(url, timeout)
    if how == "fail" and proxy_ok:
        st, b = curl(url, extra=["-x", PROXY], timeout=25)
        if st == "200" and len(b) > 0:
            how, data = "proxy-only", b
    if how == "fail" or not data:
        return "fail", b""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(meta, "w", encoding="utf-8") as f:
        json.dump({"how": how, "url": url, "size": len(data)}, f, ensure_ascii=False)
    with open(k, "wb") as f:
        f.write(data)
    return how, data


def verify_url(url, tries=2):
    for i in range(tries):
        how, data = fetch_cached(url)
        if how != "fail":
            return how, len(data)
        if i + 1 < tries:
            time.sleep(1.0)
    return "fail", 0


ACC_ALTS = [("https://ghproxy.net/https://", "https://gh-proxy.com/https://"),
            ("https://gh-proxy.com/https://", "https://ghproxy.net/https://")]


def alt_accel(url):
    for a, b in ACC_ALTS:
        if url.startswith(a):
            return b + url[len(a):]
    return None


def probe_file(url, timeout=25, tries=3):
    """稳健探测文件是否存在且可下载
    返回 (status, data, 可用URL)；status: ok / notfound / fail
    要点：
      · 404/410 才算「文件不存在」→ 剔除
      · 403(限流)、5xx、超时、200+空内容 → 重试，并换备用加速器
      · ghproxy 类加速器会限流并间歇性返回空内容，绝不可据此判死
    """
    def once(u, t):
        st, b = curl(u, timeout=t)
        if st == "200" and len(b) > 0:
            return "ok", b
        if st in ("404", "410"):
            return "notfound", b""
        host = urlsplit(u).hostname
        if host:
            ip = doh_ip(host)
            if ip:
                port = urlsplit(u).port or (443 if u.startswith("https") else 80)
                st2, b2 = curl(u, extra=["--resolve", "%s:%s:%s" % (host, port, ip)], timeout=t)
                if st2 == "200" and len(b2) > 0:
                    return "ok", b2
                if st2 in ("404", "410"):
                    return "notfound", b""
        return "retry", b""

    alt = alt_accel(url)
    for i in range(tries):
        r, b = once(url, timeout)
        if r == "ok":
            return "ok", b, url
        if r == "notfound":
            break
        time.sleep(1.5 * (i + 1))
    if alt:
        for i in range(tries):
            r, b = once(alt, timeout)
            if r == "ok":
                return "ok", b, alt
            if r == "notfound":
                break
            time.sleep(1.5 * (i + 1))
    # 兜底：本机代理确认（说明路径存在，只是本机直连受限）
    st, b = curl(url, extra=["-x", PROXY], timeout=timeout)
    if st == "200" and len(b) > 0:
        return "ok", b, url
    return "fail", b"", url


_PROBE = {}


def check_url(url):
    """返回 (ok?, 可用URL)；成功结果写入磁盘缓存以加速重跑"""
    if url in _PROBE:
        return _PROBE[url]
    k, meta = _ck(url), _ck(url) + ".json"
    if os.path.exists(meta):
        try:
            d = json.load(open(meta, encoding="utf-8"))
            if d.get("how") != "fail":
                _PROBE[url] = (True, d.get("final") or url)
                return _PROBE[url]
        except Exception:
            pass
    st, data, w = probe_file(url)
    if st == "ok":
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(meta, "w", encoding="utf-8") as f:
                json.dump({"how": "ok", "url": url, "size": len(data), "final": w}, f, ensure_ascii=False)
            with open(k, "wb") as f:
                f.write(data)
        except Exception:
            pass
        _PROBE[url] = (True, w)
        return _PROBE[url]
    if st != "ok":
        r = repair_ext(url)
        if r:
            _PROBE[url] = (True, r)
            return _PROBE[url]
        _PROBE[url] = (False, url)
        return _PROBE[url]
    _PROBE[url] = (True, w)
    return _PROBE[url]


REPAIR_DIRS = ("libs/js/", "libs/", "js/", "lib/", "json/", "libs/jar/")


def repair_ext(url):
    """相对路径写错/目录改名时的补救：换常见目录再试"""
    if "/" not in url:
        return None
    head, _, name = url.rpartition("/")
    base, _, _ = head.rpartition("/")
    if not name:
        return None
    for d in REPAIR_DIRS:
        cand = "%s/%s%s" % (base, d, name)
        if cand == url:
            continue
        st, data, _w = probe_file(cand, timeout=15, tries=1)
        if st == "ok":
            return cand
    return None


def main():
    for d in (OUT, DOCS, LIVE):
        os.makedirs(d, exist_ok=True)
    all_sites, seen_key, seen_name = [], set(), set()
    all_parses, seen_parse = [], set()
    flags, ads, hosts, doh = [], [], [], []
    rules = []
    per_line = []
    dropped = []
    risk_sites = []

    for name, url, _bodyfn, note in SOURCES:
        j = load_body(url)
        if not j or "sites" not in j:
            print("  !! %-18s 无 sites" % name)
            continue
        sites = [s for s in (j.get("sites") or []) if isinstance(s, dict)]
        spider = str(j.get("spider") or "").strip()
        # 本线路的全局 spider → 绝对地址 + 正确 md5（站点继承用）
        line_spider = ""
        if spider:
            real = spider.partition(";md5;")[0].strip()
            jurl = real if real.startswith("http") else join_abs(url, real)
            how, data = fetch_cached(jurl)
            if data:
                line_spider = "%s;md5;%s" % (jurl, hashlib.md5(data).hexdigest())
        # 站点级 jar / ext / api 绝对化
        resolved, pending = [], []
        for s in sites:
            s = dict(s)
            for fld in ("jar", "ext", "api"):
                v = s.get(fld)
                if not isinstance(v, str) or not v.strip():
                    continue
                if fld == "jar":
                    nv, ch = resolve_abs(url, v, force=True)
                    if ch:
                        s[fld] = nv
                        pending += [x.split(";md5;")[0] for x in ch]
                elif fld == "ext":
                    nv, ch = resolve_abs(url, v)
                    if ch:
                        s[fld] = nv
                        pending += ch
                else:  # api：只有形如路径的才处理
                    if PATH_EXT.match(v.strip()):
                        nv = join_abs(url, v.strip())
                        s[fld] = nv
                        pending.append(nv)
            resolved.append(s)
        # 校验可达性：多加速器容错 + 空响应重试 + 目录补救
        fix, still_bad = {}, set()
        if pending:
            uniq = sorted(set(pending))
            with ThreadPoolExecutor(max_workers=3) as ex:
                for u, (okk, w) in zip(uniq, ex.map(check_url, uniq)):
                    if not okk:
                        still_bad.add(u)
                    elif w != u:
                        fix[u] = w
        kept = []
        for s in resolved:
            fail = False
            for fld in ("jar", "ext", "api"):
                v = s.get(fld)
                if not isinstance(v, str) or not v.strip():
                    continue
                parts = v.split("$$$")
                new = []
                for p in parts:
                    key = p.split(";md5;")[0].strip()
                    if key in fix:
                        new.append(fix[key] + (";md5;" + p.split(";md5;", 1)[1] if ";md5;" in p else ""))
                    elif key in still_bad:
                        fail = True
                        new.append(p)
                    elif EMBED.search(p):
                        # 内嵌相对路径：可达则换成绝对地址，不可达则保留原文（不因此剔除站点）
                        def _rep(m, fix=fix, still_bad=still_bad):
                            u = join_abs(url, m.group(0))
                            if u in fix:
                                return fix[u]
                            if u in still_bad:
                                return m.group(0)
                            return u
                        new.append(EMBED.sub(_rep, p))
                    else:
                        new.append(p)
                s[fld] = "$$$".join(new)
            if fail:
                dropped.append((name, s.get("name"), str(s.get("ext") or s.get("api"))[:70]))
                continue
            # 站点继承本线路的爬虫包（合并后全局 spider 不再通用）
            if not str(s.get("jar") or "").strip() and line_spider:
                s["jar"] = line_spider
            k = s.get("key") or ""
            nm = s.get("name") or ""
            if k and k in seen_key:
                continue
            if nm and nm in seen_name:
                continue
            if k:
                seen_key.add(k)
            if nm:
                seen_name.add(nm)
            kept.append(s)
        all_sites.extend(kept)
        # parses
        pn = 0
        for p in (j.get("parses") or []):
            if not isinstance(p, dict):
                continue
            sig = (p.get("name"), p.get("url"))
            if sig in seen_parse:
                continue
            seen_parse.add(sig)
            all_parses.append(p)
            pn += 1
        flags += [f for f in (j.get("flags") or []) if isinstance(f, str)]
        ads += [a for a in (j.get("ads") or []) if isinstance(a, str)]
        hosts += [h for h in (j.get("hosts") or []) if isinstance(h, str)]
        doh += [d for d in (j.get("doh") or []) if isinstance(d, dict)]
        for r in (j.get("rules") or []):
            if isinstance(r, dict):
                blob = json.dumps(r, ensure_ascii=False)
                if "./" in blob or "../" in blob:
                    continue
                rules.append(r)
        per_line.append({"name": name, "url": url, "note": note,
                         "sites_raw": len(sites), "sites_kept": len(kept), "parses": pn})

    # ---- 去重辅助列表 ----
    def uniq(seq):
        out, seen = [], set()
        for x in seq:
            k = json.dumps(x, ensure_ascii=False, sort_keys=True) if not isinstance(x, str) else x
            if k not in seen:
                seen.add(k)
                out.append(x)
        return out

    flags, ads, hosts = uniq(flags), uniq(ads), uniq(hosts)
    rules = uniq(rules)
    doh = uniq(doh)

    # ---- 直播源（全部实测可达）----
    LIVES = [
        ("BigBigGrandG-综合", "https://ghproxy.net/https://raw.githubusercontent.com/BigBigGrandG/IPTV-URL/release/Gather.m3u", 1956),
        ("Guovin-IPTV", "https://ghproxy.net/https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u", 1619),
        ("苏香-myIPTV", "https://ghproxy.net/https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u", 1273),
        ("huyayqk", "https://sub.ottiptv.cc/huyayqk.m3u", 1119),
        ("ibert-ALL", "https://m3u.ibert.me/all.m3u", 723),
        ("vbskycn-IPTV4", "https://ghproxy.net/https://raw.githubusercontent.com/vbskycn/iptv/master/tv/iptv4.txt", 679),
        ("iptv-org-中国", "https://ghproxy.net/https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u", 508),
        ("芒果TV", "https://mgtv.ottiptv.cc/mglist.m3u", 197),
        ("YanG-1989", "https://ghproxy.net/https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u", 123),
        ("Kimentanm", "https://ghproxy.net/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u", 120),
        ("YueChan-Live", "https://ghproxy.net/https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u", 96),
        ("如意TV", "http://iptv.ruyitv.cc/m3u/tv.txt", 79),
        ("FYTV", "http://iptv.4666888.xyz/FYTV.m3u", 49),
        ("范明明-综合(需外网)", "https://live.fanmingming.com/tv/m3u/index.m3u", 0),
    ]
    live_group = {
        "name": "直播",
        "type": 0,
        "url": LIVES[0][1],
        "playerType": 1,
        "channels": [{"name": n, "url": u} for n, u, _ in LIVES],
    }

    # ---- spider：取主线路的 jar（绝对地址 + 正确 md5）----
    try:
        primary = load_body(SOURCES[0][1])
    except Exception:
        primary = {}
    spider = ""
    sp_raw = str(primary.get("spider") or "").strip()
    if sp_raw:
        real = sp_raw.partition(";md5;")[0].strip()
        jurl = real if real.startswith("http") else join_abs(SOURCES[0][1], real)
        how, data = fetch_cached(jurl)
        if data:
            spider = "%s;md5;%s" % (jurl, hashlib.md5(data).hexdigest())

    # ---- 全能合并单仓 ----
    merged = {
        "wallpaper": primary.get("wallpaper") or "",
        "logo": primary.get("logo") or "",
        "spider": spider,
        "sites": all_sites,
        "lives": [live_group],
        "parses": all_parses,
        "flags": flags,
        "ads": ads,
        "hosts": hosts,
        "doh": doh,
        "rules": rules,
    }
    merged = {k: v for k, v in merged.items() if v not in ("", [], None)}
    with open(os.path.join(OUT, "all-in-one.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)

    # ---- 多仓（推荐）----
    urls = [{"name": n, "url": u} for n, u, _, _ in SOURCES]
    with open(os.path.join(OUT, "multi.json"), "w", encoding="utf-8") as f:
        json.dump({"urls": urls}, f, ensure_ascii=False, indent=2)

    # ---- 多仓（含子仓库 + 备用线路）----
    urls2 = list(urls)
    urls2 += [{"name": n, "url": u} for n, u in DEPOTS]
    urls2 += [{"name": n, "url": u} for n, u, _ in BACKUP_LINES]
    with open(os.path.join(OUT, "multi-plus.json"), "w", encoding="utf-8") as f:
        json.dump({"urls": urls2}, f, ensure_ascii=False, indent=2)

    # ---- 纯文本清单（可直接粘贴/扫码）----
    with open(os.path.join(DOCS, "在线接口地址.txt"), "w", encoding="utf-8") as f:
        f.write("FongMi 在线接口地址清单（直接粘贴到「设置-点播-配置地址」即可，无需电脑做服务器）\n")
        f.write("=" * 72 + "\n\n【单仓线路｜实测公网可达】\n")
        for n, u, _b, note in SOURCES:
            f.write("%s\n    %s\n    (%s)\n\n" % (n, u, note))
        f.write("【多仓/子仓库】\n")
        for n, u in DEPOTS:
            f.write("%s\n    %s\n\n" % (n, u))
        f.write("【备用线路｜手机运营商网络下可用】\n")
        for n, u, note in BACKUP_LINES:
            f.write("%s\n    %s\n    (%s)\n\n" % (n, u, note))
    with open(os.path.join(LIVE, "live-sources.txt"), "w", encoding="utf-8") as f:
        f.write("FongMi 直播源地址清单（m3u/txt，可直接填到「设置-直播」）\n")
        f.write("=" * 72 + "\n\n")
        for n, u, ch in LIVES:
            f.write("%-24s %s\n    %s\n\n" % (n, ("%d 频道" % ch) if ch else "频道数未知", u))

    # ---- 线路清单.md（自动刷新实测数据）----
    t = ["# 线路清单（实测数据）", "",
         "> 由 `tools/update.py` 自动生成，数字为**本机实测**结果。", "",
         "## 单仓线路", "", "| 线路 | 站点数（原始） | 合并后保留 | 特点 |", "|---|---|---|---|"]
    for p_ in per_line:
        t.append("| %s | %d | %d | %s |" % (p_["name"], p_["sites_raw"], p_["sites_kept"], p_["note"]))
    t += ["", "## 多仓 / 子仓库", "", "| 名称 | 地址 |", "|---|---|"]
    for n, u in DEPOTS:
        t.append("| %s | `%s` |" % (n, u))
    t += ["", "## 备用线路（本机网络不可直连验证）", "", "| 名称 | 地址 | 说明 |", "|---|---|---|"]
    for n, u, note in BACKUP_LINES:
        t.append("| %s | `%s` | %s |" % (n, u, note))
    t += ["", "## 合并统计", "",
          "- 合并后站点：**%d**" % len(all_sites),
          "- 解析接口：**%d**" % len(all_parses),
          "- 直播源：**%d 路**（约 %d 频道）" % (len(LIVES), sum(x[2] for x in LIVES)),
          "- 剔除站点（上游文件已不存在）：**%d**" % len(dropped), ""]
    with open(os.path.join(DOCS, "线路清单.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(t))

    # ---- 报告 ----
    with open(os.path.join(HERE, "build_report.json"), "w", encoding="utf-8") as f:
        json.dump({"per_line": per_line, "dropped": dropped, "risk_sites": risk_sites,
                   "totals": {"sites": len(all_sites), "parses": len(all_parses),
                              "flags": len(flags), "rules": len(rules),
                              "lives": len(LIVES), "live_channels": sum(x[2] for x in LIVES)}},
                  f, ensure_ascii=False, indent=1)
    print("线路  %-4s %-8s %-8s" % ("", "原始", "保留"))
    for p in per_line:
        print("  %-20s %-8d %-8d %s" % (p["name"], p["sites_raw"], p["sites_kept"], p["note"]))
    print("\n合并站点 %d  解析 %d  flags %d  rules %d  直播源 %d路/%d频道"
          % (len(all_sites), len(all_parses), len(flags), len(rules), len(LIVES), sum(x[2] for x in LIVES)))
    print("剔除站点(ext/jar不可达) %d 个" % len(dropped))
    for d in dropped[:15]:
        print("    - %s / %s -> %s" % d)
    print("spider = %s" % spider[:130])


if __name__ == "__main__":
    main()
