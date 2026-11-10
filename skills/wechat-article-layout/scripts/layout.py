#!/usr/bin/env python3
"""林月半子 · Markdown → 公众号排版
用法: python3 layout.py article.md [--banner banner.json] [--out 目录] [--style 风格] [--theme 配色]
产出: <slug>-公众号排版.html（打开 → 选风格和配色 → 填头像 GIF → 一键复制全文）
需要同目录下有 banner.py（来自 wechat-opening-banner skill）才能画开头横幅。
"""
import re, os, sys, json, html as H, argparse

THEMES = {   # 15 套配色：main 主色 / soft 浅底 / tint 色块 / line 线条 / mark 荧光笔。主色统一压暗降饱和，浅底和线条从主色同色相推出来
    "orange":  dict(name="品牌橙", main="#C9643E", soft="#FCF6F2", tint="#F7E3D5", line="#DAB196", mark="#FCE7A6"),
    "blue":    dict(name="科技蓝", main="#2952B6", soft="#F4F8FD", tint="#DDE8FB", line="#A6BBE2", mark="#F9E8A7"),
    "teal":    dict(name="薄荷绿", main="#0C7D6C", soft="#F3F9F7", tint="#D8EDE6", line="#9BC5B9", mark="#F8E8AB"),
    "ink":     dict(name="墨黑", main="#1A1D23", soft="#F9F7F4", tint="#EAE7E1", line="#BFBAB2", mark="#FAE39F"),
    "navy":    dict(name="藏青金", main="#183053", soft="#F5F8FB", tint="#E0E8F3", line="#CAAD71", mark="#F3E0B0"),
    "violet":  dict(name="葡萄紫", main="#5F3F98", soft="#F8F6FD", tint="#E9E4F9", line="#BFB3DD", mark="#F8E8AB"),
    "rose":    dict(name="胭脂红", main="#A6344C", soft="#FDF5F6", tint="#FAE0E3", line="#DEABB2", mark="#FBE6B3"),
    "amber":   dict(name="琥珀", main="#9D6311", soft="#FAF7F2", tint="#F2E5D3", line="#CFB791", mark="#CEE9FD"),
    "morandi": dict(name="莫兰迪", main="#7D6560", soft="#FAF7F5", tint="#ECE6E3", line="#C4B8B2", mark="#F1E4C3"),
    "forest":  dict(name="松柏金", main="#184731", soft="#F5F8F6", tint="#E0EAE2", line="#CAAD71", mark="#F3E0B0"),
    "petrol":  dict(name="孔雀青", main="#0A5765", soft="#F4F8F9", tint="#DAEBEE", line="#A0C2C8", mark="#FBE7AB"),
    "mist":    dict(name="雾霾蓝", main="#4B6D8A", soft="#F5F8FA", tint="#DFE9F0", line="#AABECC", mark="#F9E7B7"),
    "matcha":  dict(name="橄榄绿", main="#596B3A", soft="#F7F8F4", tint="#E6E9DB", line="#B9BEA3", mark="#FDE4BB"),
    "cocoa":   dict(name="可可棕", main="#603F2C", soft="#F9F7F5", tint="#EEE5DF", line="#C8B7A9", mark="#F8E3B0"),
    "dusty":   dict(name="豆沙粉", main="#9D5C61", soft="#FBF6F6", tint="#F5E2E2", line="#D5B0AF", mark="#F9E6BF"),
}
# 10 套风格：不只换颜色，标题、强调、引用、列表、分隔线、图片的结构都不同。r 是卡片圆角
STYLES = {
    "std":  dict(name="标准", r=14, desc="PART 大标题 + 荧光笔 + 圆角卡片"),
    "mag":  dict(name="杂志", r=2,  desc="宋体标题居中、细线、留白多"),
    "min":  dict(name="极简", r=0,  desc="黑白为主、无底色、左对齐"),
    "geek": dict(name="极客", r=6,  desc="等宽字标签、虚线框、终端感"),
    "bold": dict(name="醒目", r=16, desc="大色块标题、粗圆角、强对比"),
    "neo":  dict(name="质感", r=16, desc="巨型数字和大引号做底纹、细线描边、柔和阴影、浅色金句卡"),
    "note": dict(name="手账", r=6,  desc="便签贴纸编号、荧光笔、虚线和纸胶带"),
    "zen":  dict(name="雅致", r=2,  desc="印章编号、宋体标题居中、双线金句"),
    "bento":dict(name="卡片", r=20, desc="大圆角色块、胶囊编号、轻盈扁平"),
    "dark": dict(name="暗夜", r=14, desc="深色底、亮色强调，科技感"),
}
NEW_ST = ("note", "zen", "bento", "dark")
# 正文先用占位色渲染一次，换配色时由页面里的脚本替换，不用每种配色各渲染一遍
TOK = dict(main="#0A0B01", soft="#0A0B02", tint="#0A0B03", line="#0A0B04", mark="#0A0B05")
INK, BODY, GRAY, MUTE, BORDER = "#111827", "#3F3F46", "#6B7280", "#94A3B8", "#E5E7EB"
PROMPT_INK = "#52607A"                # 提示词文字：冷灰蓝，和正文区分开
MONO = "Menlo,Consolas,'SF Mono',monospace"
SERIF = "Georgia,'Songti SC','STSong','Source Han Serif SC','Noto Serif SC',serif"
CN_NUM = "一二三四五六七八九十"
esc = lambda s: H.escape(s, quote=False)
WARN = []                             # 排版过程中发现的问题，最后在自查报告里打印
def warn(x):
    if x not in WARN: WARN.append(x)

# ---------------- inline ----------------
def strong_css(T):
    st = T["st"]
    if st in NEW_ST: return x_strong(T)
    if st == "neo":  return f'font-weight:800;color:{INK};background:linear-gradient(100deg,{T["mark"]},{T["tint"]});padding:2px 6px;border-radius:4px;'
    if st == "mag":  return f'font-weight:700;color:{T["main"]};'
    if st == "min":  return 'font-weight:700;color:#000000;'
    if st == "geek": return f'font-weight:700;color:{T["main"]};background:{T["soft"]};padding:1px 5px;border-radius:3px;'
    if st == "bold": return f'font-weight:700;color:{INK};background:{T["mark"]};padding:2px 4px;border-radius:3px;'
    return f'font-weight:700;color:{INK};background:linear-gradient(transparent 58%,{T["mark"]} 58%);padding:0 2px;'

def inline(s, T, notes):
    keep = []
    def stash(h):
        keep.append(h); return f"\x00{len(keep)-1}\x00"
    # 行内代码、图片、链接先收起来，里面的 * _ = 不会被当成标记
    s = re.sub(r"`([^`]+)`", lambda m: stash(f'<code style="font-family:{MONO};font-size:0.9em;background:{T["soft"]};color:{T["main"]};padding:2px 5px;border-radius:4px;">{esc(m.group(1))}</code>'), s)
    s = re.sub(r'!\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+"[^"]*")?\)', lambda m: stash(f'<img src="{m.group(2)}" style="max-width:100%;vertical-align:middle;"/>'), s)
    def link(m):
        text, url = esc(m.group(1)), m.group(2)
        if "mp.weixin.qq.com" in url:
            return stash(f'<a href="{url}" style="color:{T["main"]};text-decoration:none;border-bottom:1px solid {T["line"]};">{text}</a>')
        notes.append((m.group(1), url))
        return stash(f'<span style="color:{T["main"]};border-bottom:1px solid {T["line"]};">{text}</span><sup style="color:{T["main"]};font-size:11px;">[{len(notes)}]</sup>')
    s = re.sub(r"\[([^\]]+)\]\(<?([^)\s>]+)>?\)", link, s)
    s = esc(s)
    s = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", lambda m: f'<strong style="{strong_css(T)}">{m.group(1)}</strong>', s)
    chip = INK if T["st"] == "min" else T["main"]
    chip_css = x_chip(T) if T["st"] in NEW_ST else f"background:{chip};color:#FFFFFF;font-weight:700;padding:2px 6px;border-radius:3px;"
    s = re.sub(r"==(?=\S)(.+?)(?<=\S)==", lambda m: f'<span style="{chip_css}">{m.group(1)}</span>', s)
    s = re.sub(r"\+\+(?=\S)(.+?)(?<=\S)\+\+|&lt;u&gt;(.+?)&lt;/u&gt;", lambda m: f'<span style="{underline_css(T)}">{m.group(1) or m.group(2)}</span>', s)
    s = re.sub(r"~~(?=\S)(.+?)(?<=\S)~~", r'<span style="text-decoration:line-through;color:#9CA3AF;">\1</span>', s)
    s = re.sub(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])", rf'<em style="font-style:normal;color:{T["main"]};">\1</em>', s)
    plain = re.sub(r"<[^>]+>|\x00\d+\x00", "", s)
    for mk in ("**", "=="):
        if mk in plain: warn(f"有一处 {mk} 没配成对，照原样显示了：「{plain.strip()[:24]}…」。是标记就补齐，本来就是原文符号则不用管")
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)

def p_css(T):
    st = T["st"]
    if st in NEW_ST: return x_p_css(st)
    if st == "mag":  return "margin:0 0 24px;font-size:16px;line-height:2;letter-spacing:1px;color:#333333;text-align:justify;"
    if st == "min":  return "margin:0 0 20px;font-size:15px;line-height:1.85;letter-spacing:0.3px;color:#2B2B2B;text-align:left;"
    if st == "geek": return f"margin:0 0 20px;font-size:15px;line-height:1.9;letter-spacing:0.4px;color:{BODY};text-align:justify;"
    return f"margin:0 0 22px;font-size:16px;line-height:1.9;letter-spacing:0.5px;color:{BODY};text-align:justify;"

# ---------------- blocks ----------------
def h2_part(n, title, sub, T):
    st = T["st"]; M = T["main"]
    if st == "neo": return neo_h2(n, title, sub, T)
    if st in NEW_ST: return x_h2(n, title, sub, T)
    subp = lambda col, extra="": (f'<p style="margin:6px 0 0;font-size:11px;letter-spacing:2px;color:{col};line-height:1.4;{extra}">{esc(sub.upper())}</p>' if sub else "")
    if st == "mag":
        return (f'<section style="margin:54px 0 30px;text-align:center;">'
                f'<p style="margin:0;font-size:34px;line-height:1;color:{M};font-family:{SERIF};font-weight:400;">{n:02d}</p>'
                f'<p style="margin:14px 0 0;font-size:22px;font-weight:700;color:{INK};line-height:1.5;font-family:{SERIF};letter-spacing:1px;">{title}</p>'
                + subp(MUTE) + f'<span style="display:inline-block;width:32px;height:1px;background:{M};margin-top:14px;"></span></section>')
    if st == "min":
        return (f'<section style="margin:48px 0 24px;padding-bottom:10px;border-bottom:2px solid {INK};display:flex;align-items:flex-end;">'
                f'<section style="flex:1;min-width:0;"><p style="margin:0;font-size:20px;font-weight:800;color:{INK};line-height:1.45;">{title}</p>' + subp(MUTE) + '</section>'
                f'<span style="flex-shrink:0;margin-left:12px;font-size:13px;font-weight:700;color:{M};font-family:{MONO};line-height:1.8;">{n:02d}</span></section>')
    if st == "geek":
        return (f'<section style="margin:46px 0 24px;padding-bottom:12px;border-bottom:1.5px dashed {T["line"]};">'
                f'<p style="margin:0 0 8px;font-size:12px;letter-spacing:1px;color:{M};font-family:{MONO};line-height:1.4;">// PART_{n:02d}' + (f' · {esc(sub.upper())}' if sub else "") + '</p>'
                f'<section style="display:flex;align-items:center;"><span style="flex-shrink:0;display:inline-block;background:#0B0B0C;color:#FFFFFF;font-size:14px;font-weight:700;font-family:{MONO};padding:3px 9px;border-radius:5px;margin-right:12px;">{n:02d}</span>'
                f'<span style="font-size:20px;font-weight:800;color:{INK};line-height:1.45;">{title}</span></section></section>')
    if st == "bold":
        return (f'<section style="margin:46px 0 26px;background:{M};border-radius:16px;padding:16px 20px;display:flex;align-items:center;">'
                f'<span style="flex-shrink:0;font-size:42px;line-height:1;font-weight:800;color:#FFFFFF;opacity:0.45;font-family:Helvetica,Arial,sans-serif;margin-right:16px;">{n:02d}</span>'
                f'<section style="flex:1;min-width:0;"><p style="margin:0;font-size:20px;font-weight:800;color:#FFFFFF;line-height:1.45;">{title}</p>' + subp("#FFFFFF", "opacity:0.75;") + '</section></section>')
    return (f'<section style="margin:46px 0 26px;display:flex;align-items:center;">'
            f'<section style="flex-shrink:0;padding-right:18px;margin-right:18px;border-right:1px solid {BORDER};text-align:center;">'
            f'<p style="margin:0;font-size:12px;letter-spacing:2px;font-weight:600;color:{MUTE};line-height:1.4;">PART</p>'
            f'<p style="margin:0;font-size:40px;line-height:1.05;font-weight:800;color:{M};font-family:Helvetica,Arial,sans-serif;">{n:02d}</p></section>'
            f'<section style="flex:1;min-width:0;"><p style="margin:0;font-size:21px;font-weight:800;color:{INK};line-height:1.45;">{title}</p>' + subp(MUTE) + '</section></section>')

def h2_pill(n, title, T):
    title = f"{CN_NUM[n-1] if n <= 10 else n}、{title}"
    return (f'<section style="margin:46px 0 28px;text-align:center;">'
            f'<span style="display:inline-block;background:{T["main"]};color:#FFFFFF;font-size:18px;font-weight:800;line-height:1.5;'
            f'padding:10px 24px;border-radius:10px;box-shadow:0 4px 0 {T["tint"]};">{title}</span></section>')

def h3(title, T):
    st = T["st"]; M = T["main"]
    m = re.match(r"^(第[一二三四五六七八九十\d]+步|Step\s*\d+)\s*[：:、.，,]?\s*(.*)$", title)
    if st == "neo": return neo_h3(m, title, T)
    if st in NEW_ST: return x_h3(m, title, T)
    if m:
        chip = {"mag": f"border:1px solid {M};color:{M};", "geek": f"background:{T['soft']};color:{M};font-family:{MONO};border-radius:5px;",
                "bold": f"background:{M};color:#FFFFFF;"}.get(st, f"background:{INK};color:#FFFFFF;")
        return (f'<section style="margin:30px 0 14px;display:flex;align-items:center;">'
                f'<span style="flex-shrink:0;display:inline-block;font-size:13px;font-weight:700;padding:4px 14px;border-radius:20px;margin-right:12px;{chip}">{m.group(1)}</span>'
                f'<span style="font-size:18px;font-weight:800;color:{INK};line-height:1.5;">{m.group(2)}</span></section>')
    if st == "mag":
        return f'<section style="margin:34px 0 14px;"><span style="font-size:18px;font-weight:700;color:{INK};font-family:{SERIF};padding-bottom:4px;border-bottom:1px solid {M};">{title}</span></section>'
    if st == "min":
        return f'<section style="margin:30px 0 12px;"><span style="font-size:17px;font-weight:800;color:#000000;">{title}</span></section>'
    if st == "geek":
        return f'<section style="margin:30px 0 14px;"><span style="font-size:16px;font-weight:700;color:{M};font-family:{MONO};margin-right:8px;">##</span><span style="font-size:18px;font-weight:800;color:{INK};">{title}</span></section>'
    if st == "bold":
        return f'<section style="margin:32px 0 14px;"><span style="display:inline-block;background:{T["tint"]};color:{M};font-size:17px;font-weight:800;padding:5px 14px;border-radius:10px;">{title}</span></section>'
    return (f'<section style="margin:32px 0 14px;"><span style="display:inline-block;width:4px;height:18px;background:{M};border-radius:2px;vertical-align:-2px;margin-right:10px;"></span>'
            f'<span style="font-size:18px;font-weight:800;color:{INK};">{title}</span></section>')

def h4(title, T):
    return f'<p style="margin:24px 0 10px;font-size:16px;font-weight:800;color:{"#FFFFFF" if T["st"] == "dark" else INK};line-height:1.6;">{title}</p>'

def terminal(lines):
    """黑底 terminal：所有风格保持一致"""
    rows = "".join(f'<p style="margin:0;white-space:pre;font-size:14px;line-height:1.9;color:#E5E7EB;font-family:{MONO};">{esc(l) or " "}</p>' for l in lines)
    return (f'<section style="margin:24px 0;background:#0B0B0C;border-radius:10px;padding:14px 18px 16px;">'
            f'<section style="margin-bottom:10px;line-height:0;">' + "".join(f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:{c};margin-right:7px;"></span>' for c in ("#FF5F57", "#FEBC2E", "#28C840")) + '</section>'
            f'<section style="overflow-x:auto;">{rows}</section></section>')

def prompt_box(lines, title, T):
    """长提示词：黑色 PROMPT 标签 + 文件名，正文限高可滑动"""
    body = []
    if T["st"] in NEW_ST:
        for l in lines:
            t = esc(l) or " "; body.append(re.sub(r"(【[^】]+】)", rf'<strong style="color:{T["main"]};">\1</strong>', t))
        return x_prompt(body, title, T)
    for l in lines:
        t = esc(l) or " "
        t = re.sub(r"(【[^】]+】)", rf'<strong style="color:{T["main"]};">\1</strong>', t)
        body.append(f'<p style="margin:0;white-space:pre-wrap;word-break:break-all;font-size:13px;line-height:1.85;color:{PROMPT_INK};font-family:{MONO};">{t}</p>')
    return (f'<section style="margin:26px 0;border:1px solid {BORDER};border-radius:{T["r"]}px;background:#F8FAFC;overflow:hidden;">'
            f'<section style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid {BORDER};background:#FFFFFF;">'
            f'<span style="display:inline-block;background:{INK};color:#FFFFFF;font-size:12px;font-weight:800;letter-spacing:1px;padding:4px 12px;border-radius:20px;font-family:{MONO};">PROMPT</span>'
            f'<span style="font-size:12px;color:{MUTE};">{esc(title or "提示词")} · 上下滑动查看 ↕</span></section>'
            f'<section style="max-height:320px;overflow-y:auto;padding:14px 18px;">{"".join(body)}</section></section>')

def dashed_box(title, icon, inner, T, height=320):
    """虚线滑动卡：长提示词 / 长图"""
    ic = {"list": f'<span style="display:block;width:14px;height:2px;background:{T["main"]};margin:3px auto;"></span>' * 3,
          "image": f'<span style="display:block;width:16px;height:12px;border:2px solid {T["main"]};border-radius:3px;margin:3px auto;"></span>'}[icon]
    return (f'<section style="margin:26px 0;border:1.5px dashed {T["line"]};border-radius:{T["r"]}px;background:#FFFFFF;overflow:hidden;">'
            f'<section style="display:flex;align-items:center;padding:12px 16px;background:{T["soft"]};border-bottom:1.5px dashed {T["line"]};">'
            f'<span style="flex-shrink:0;display:inline-block;width:30px;height:30px;border:1px solid {T["tint"]};background:#FFFFFF;border-radius:8px;padding-top:6px;box-sizing:border-box;margin-right:10px;">{ic}</span>'
            f'<span style="flex:1;font-size:15px;font-weight:700;color:#374151;">{esc(title)}</span>'
            f'<span style="font-size:12px;color:{T["main"]};">↕ 滑动</span></section>'
            f'<section style="max-height:{height}px;overflow-y:auto;padding:16px 18px;">{inner}</section></section>')

def quote(text_html, T):
    st = T["st"]; M = T["main"]
    if st == "neo": return neo_quote(text_html, T)
    if st in NEW_ST: return x_quote(text_html, T)
    if st == "mag":
        return (f'<section style="margin:32px 0;padding:22px 14px 16px;border-top:1px solid {T["line"]};border-bottom:1px solid {T["line"]};text-align:center;">'
                + quote_svg(M, 1, 30, "0 auto 8px") +
                f'<section style="font-size:16px;line-height:2;color:#444444;letter-spacing:1px;font-family:{SERIF};text-align:left;">{text_html}</section></section>')
    if st == "min":
        return f'<section style="margin:26px 0;padding:2px 0 2px 16px;border-left:2px solid #D4D4D8;"><section style="font-size:15px;line-height:1.85;color:{GRAY};">{text_html}</section></section>'
    if st == "geek":
        return (f'<section style="margin:26px 0;padding:12px 16px 10px;background:{T["soft"]};border:1px dashed {T["line"]};border-radius:6px;">'
                f'<p style="margin:0 0 6px;font-size:12px;color:{M};font-family:{MONO};line-height:1.4;">&gt; quote</p>'
                f'<section style="font-size:15px;line-height:1.9;color:#1F2937;">{text_html}</section></section>')
    if st == "bold":
        return (f'<section style="margin:28px 0;padding:18px 20px 14px;background:{T["tint"]};border-radius:16px;border-left:6px solid {M};">'
                f'<section style="font-size:16px;line-height:1.9;color:{INK};font-weight:600;">{text_html}</section></section>')
    return (f'<section style="margin:28px 0;padding:18px 22px 20px;background:{T["soft"]};border-left:4px solid {M};border-radius:4px 12px 12px 4px;">'
            + quote_svg(T["line"], 1, 30, "2px 0 6px") +
            f'<section style="font-size:16px;line-height:1.9;color:#1F2937;letter-spacing:0.5px;">{text_html}</section></section>')

def golden(text_html, T):
    """金句卡"""
    st = T["st"]; M = T["main"]
    if st == "neo": return neo_golden(text_html, T)
    if st in NEW_ST: return x_golden(text_html, T)
    if st == "mag":
        return (f'<section style="margin:40px 0;text-align:center;">' + quote_svg(M, 1, 36, "0 auto") +
                f'<p style="margin:10px 12px 0;font-size:21px;line-height:1.8;font-weight:700;color:{INK};font-family:{SERIF};letter-spacing:1px;">{text_html}</p></section>')
    if st == "min":
        return (f'<section style="margin:34px 0;padding:18px 0;border-top:1px solid {INK};border-bottom:1px solid {INK};">'
                f'<p style="margin:0;font-size:19px;line-height:1.7;font-weight:800;color:#000000;">{text_html}</p></section>')
    if st == "geek":
        return (f'<section style="margin:34px 0;padding:18px 18px;border:1.5px solid {M};border-radius:6px;text-align:center;">'
                f'<p style="margin:0 0 8px;font-size:12px;color:{M};font-family:{MONO};line-height:1.4;">/* key point */</p>'
                f'<p style="margin:0;font-size:19px;line-height:1.7;font-weight:800;color:{INK};">{text_html}</p></section>')
    if st == "bold":
        return (f'<section style="margin:34px 0;padding:24px 20px;background:{T["soft"]};border:2px solid {M};border-radius:16px;text-align:center;">'
                f'<p style="margin:0;font-size:21px;line-height:1.7;font-weight:800;color:{M};">{text_html}</p></section>')
    return (f'<section style="margin:36px 0;text-align:center;">'
            f'<span style="display:inline-block;width:36px;height:3px;background:{M};border-radius:2px;"></span>'
            f'<p style="margin:16px 8px;font-size:20px;line-height:1.7;font-weight:800;color:{INK};">{text_html}</p>'
            f'<span style="display:inline-block;width:36px;height:3px;background:{M};border-radius:2px;"></span></section>')

def callout(kind, text_html, T):
    st = T["st"]
    lab = {"TIP": "小技巧", "NOTE": "说明", "WARN": "注意", "TLDR": "省流版"}.get(kind, kind)
    wn = kind == "WARN"; col = "#D97706" if wn else T["main"]
    body = f'<section style="font-size:15px;line-height:1.85;color:{BODY};">{text_html}</section>'
    if st in NEW_ST: return x_callout(kind, text_html, T)
    if st == "neo":
        return (f'<section style="margin:28px 0;border:1px solid {"#F3DDB4" if wn else T["tint"]};border-radius:16px;background:{"#FFFCF5" if wn else "#FFFFFF"};padding:18px 20px 16px;box-shadow:0 10px 30px rgba(17,24,39,0.06);">'
                f'<p style="margin:0 0 10px;line-height:1;"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{col};vertical-align:middle;margin-right:8px;"></span>'
                f'<span style="font-size:12px;font-weight:800;letter-spacing:3px;color:{col};vertical-align:middle;">{lab}</span></p>{body}</section>')
    if st == "mag":
        return (f'<section style="margin:28px 0;padding:14px 0 4px;border-top:2px solid {col};">'
                f'<p style="margin:0 0 8px;font-size:13px;font-weight:700;letter-spacing:3px;color:{col};">{lab}</p>{body}</section>')
    if st == "min":
        return f'<section style="margin:26px 0;padding:2px 0 2px 16px;border-left:2px solid {col};"><p style="margin:0 0 4px;font-size:13px;font-weight:800;color:{col};">{lab}</p>{body}</section>'
    if st == "geek":
        return (f'<section style="margin:26px 0;border:1px dashed {"#F0B45C" if wn else T["line"]};border-radius:6px;background:{"#FFF7E6" if wn else "#FFFFFF"};padding:12px 16px;">'
                f'<p style="margin:0 0 6px;font-size:12px;font-weight:700;color:{col};font-family:{MONO};">// {lab}</p>{body}</section>')
    if st == "bold":
        return (f'<section style="margin:26px 0;border-radius:16px;background:{"#FFF1D6" if wn else T["tint"]};padding:16px 18px;">'
                f'<span style="display:inline-block;background:{col};color:#FFFFFF;font-size:13px;font-weight:800;padding:4px 12px;border-radius:20px;margin-bottom:10px;">{lab}</span>{body}</section>')
    return (f'<section style="margin:26px 0;border:1px solid {"#FCD9A5" if wn else T["tint"]};border-radius:12px;background:{"#FFF7E6" if wn else "#FFFFFF"};padding:16px 18px;">'
            f'<span style="display:inline-block;background:{col};color:#FFFFFF;font-size:12px;font-weight:700;padding:3px 10px;border-radius:6px;margin-bottom:10px;">{lab}</span>{body}</section>')

def image(src, alt, T):
    fr = {"mag": "border-radius:0;", "min": "border-radius:0;", "geek": f"border-radius:6px;border:1px solid {BORDER};box-sizing:border-box;",
          "bold": "border-radius:14px;box-shadow:0 6px 20px rgba(0,0,0,0.10);"}.get(T["st"], "border-radius:8px;")
    if T["st"] == "neo":
        cap = caption(esc(alt), T, 14, 0) if alt and alt.lower() not in ("image", "img", "图片") else ""
        return (f'<section style="margin:26px 0;text-align:center;"><img src="{src}" style="display:block;width:100%;max-width:100%;border-radius:14px;box-shadow:0 12px 32px rgba(17,24,39,0.10);"/>{cap}</section>')
    cap = caption(esc(alt), T, 8, 0) if alt and alt.lower() not in ("image", "img", "图片") else ""
    return f'<section style="margin:24px 0;text-align:center;"><img src="{src}" style="display:block;width:100%;max-width:100%;margin:0 auto;{fr}"/>{cap}</section>'

def caption(text_html, T, top=-12, bottom=24):
    """图注：灰色小字。跟在图片或视频下面的一行短说明"""
    st = T["st"]
    if st == "neo":
        return (f'<p style="margin:{top + 2}px 0 {bottom}px;text-align:center;line-height:1.6;"><span style="display:inline-block;width:14px;height:1px;background:{T["line"]};vertical-align:middle;margin-right:8px;"></span>'
                f'<span style="color:{MUTE};font-size:12px;letter-spacing:0.5px;vertical-align:middle;">{text_html}</span>'
                f'<span style="display:inline-block;width:14px;height:1px;background:{T["line"]};vertical-align:middle;margin-left:8px;"></span></p>')
    pre = f'<span style="color:{T["main"]};font-family:{MONO};">// </span>' if st == "geek" else (f'<span style="color:{T["main"]};">▲ </span>' if st == "mag" else "")
    return f'<p style="margin:{top}px 0 {bottom}px;font-size:13px;color:{MUTE};text-align:{"left" if st == "min" else "center"};line-height:1.6;">{pre}{text_html}</p>'

def list_block(items, T, notes):
    """items: (层级, 序号或 None, 文字)。序号沿用原文写的数字"""
    st = T["st"]; M = T["main"]; fs = "15px" if st in ("min", "geek") else "16px"; rows = []
    for lv, num, text in items:
        if num is None:
            if st == "neo" and not lv: mk = f'<span style="flex-shrink:0;display:inline-block;width:8px;height:8px;background:{M};border-radius:2px;margin:12px 12px 0 3px;"></span>'
            elif lv:          mk = f'<span style="flex-shrink:0;display:inline-block;width:5px;height:5px;border-radius:50%;border:1px solid {M};margin:12px 11px 0 4px;"></span>'
            elif st == "mag": mk = f'<span style="flex-shrink:0;color:{M};margin-right:10px;line-height:1.9;font-size:{fs};">—</span>'
            elif st == "min": mk = f'<span style="flex-shrink:0;display:inline-block;width:5px;height:5px;background:{INK};margin:12px 12px 0 4px;"></span>'
            elif st == "geek":mk = f'<span style="flex-shrink:0;color:{M};font-family:{MONO};margin-right:10px;line-height:1.9;font-size:13px;">&gt;</span>'
            elif st == "bold":mk = f'<span style="flex-shrink:0;display:inline-block;width:8px;height:8px;border-radius:50%;background:{M};margin:11px 12px 0 2px;"></span>'
            else:             mk = f'<span style="flex-shrink:0;display:inline-block;width:6px;height:6px;border-radius:50%;background:{M};margin:12px 12px 0 4px;"></span>'
        else:
            if st == "neo":   mk = f'<span style="flex-shrink:0;color:{M};font-family:Helvetica,Arial,sans-serif;font-style:italic;font-size:20px;font-weight:900;margin-right:10px;line-height:1.5;min-width:28px;">{num:02d}</span>'
            elif st == "mag": mk = f'<span style="flex-shrink:0;color:{M};font-family:{SERIF};font-size:17px;font-weight:700;margin-right:10px;line-height:1.75;">{num}.</span>'
            elif st == "min": mk = f'<span style="flex-shrink:0;color:#000000;font-size:{fs};font-weight:800;margin-right:8px;line-height:1.9;">{num}.</span>'
            elif st == "geek":mk = f'<span style="flex-shrink:0;color:{M};font-family:{MONO};font-size:13px;font-weight:700;margin-right:10px;line-height:2.1;">{num:02d}</span>'
            elif st == "bold":mk = f'<span style="flex-shrink:0;display:inline-block;min-width:22px;height:22px;line-height:22px;text-align:center;border-radius:50%;background:{M};color:#FFFFFF;font-size:12px;font-weight:800;margin:4px 10px 0 0;">{num}</span>'
            else:             mk = f'<span style="flex-shrink:0;display:inline-block;min-width:22px;height:22px;line-height:22px;text-align:center;border-radius:6px;background:{T["tint"]};color:{M};font-size:12px;font-weight:800;margin:4px 10px 0 0;">{num}</span>'
        rows.append(f'<section style="display:flex;margin:0 0 10px {lv * 22}px;">{mk}<p style="margin:0;flex:1;min-width:0;font-size:{fs};line-height:1.9;color:{BODY};">{inline(text, T, notes)}</p></section>')
    return '<section style="margin:0 0 22px;">' + "".join(rows) + '</section>'

def table(rows, T, notes):
    st = T["st"]; head, body = rows[0], rows[1:]; n = len(head)
    body = [(r + [""] * n)[:n] for r in body]
    if st == "neo":
        th = "".join(f'<th style="padding:12px 14px;font-weight:800;text-align:left;font-size:12px;letter-spacing:1px;background:{T["soft"]};color:{T["main"]};border-bottom:1px solid {T["tint"]};">{inline(c, T, notes)}</th>' for c in head)
        tb = "".join("<tr>" + "".join(f'<td style="padding:12px 14px;color:{INK if j == 0 else BODY};font-weight:{700 if j == 0 else 400};border-top:1px solid #F1F2F4;">{inline(c, T, notes)}</td>' for j, c in enumerate(r)) + "</tr>" for r in body)
        return (f'<section style="margin:28px 0;border:1px solid {T["tint"]};border-radius:14px;overflow:hidden;background:#FFFFFF;box-shadow:0 10px 30px rgba(17,24,39,0.06);"><section style="overflow-x:auto;">'
                f'<table style="width:100%;border-collapse:collapse;font-size:14px;line-height:1.7;"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></section></section>')
    if st == "dark":
        th = "".join(f'<th style="padding:11px 13px;font-weight:800;text-align:left;font-size:13px;background:#1A2029;color:{T["line"]};border-bottom:1px solid #2A313C;">{inline(c, T, notes)}</th>' for c in head)
        tb = "".join("<tr>" + "".join(f'<td style="padding:11px 13px;color:{"#FFFFFF" if j == 0 else "#C5CCD6"};font-weight:{700 if j == 0 else 400};border-top:1px solid #2A313C;">{inline(c, T, notes)}</td>' for j, c in enumerate(r)) + "</tr>" for r in body)
        return (f'<section style="margin:26px 0;border:1px solid #2A313C;border-radius:14px;overflow:hidden;background:#151A21;"><section style="overflow-x:auto;">'
                f'<table style="width:100%;border-collapse:collapse;font-size:14px;line-height:1.7;"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></section></section>')
    if st in ("mag", "min"):
        hs, cs = f"border-bottom:2px solid {INK};color:{INK};", f"border-bottom:1px solid {BORDER};"
    elif st == "geek": hs, cs = f"background:#0B0B0C;color:#FFFFFF;border:1px solid #0B0B0C;font-family:{MONO};", f"border:1px solid {BORDER};"
    elif st == "bold": hs, cs = f"background:{T['main']};color:#FFFFFF;border:1px solid {T['main']};", f"border:1px solid {T['tint']};"
    else:              hs, cs = f"background:{T['soft']};color:{INK};border:1px solid {BORDER};", f"border:1px solid {BORDER};"
    th = "".join(f'<th style="padding:10px 12px;font-weight:700;text-align:left;{hs}">{inline(c, T, notes)}</th>' for c in head)
    tb = "".join("<tr>" + "".join(f'<td style="padding:10px 12px;color:{BODY};{cs}">{inline(c, T, notes)}</td>' for c in r) + "</tr>" for r in body)
    return f'<section style="margin:24px 0;overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:14px;line-height:1.7;"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></section>'

def hr(T):
    st = T["st"]; M = T["main"]; box = '<section style="margin:40px 0;text-align:center;line-height:1;">'
    if st in NEW_ST: return x_hr(T)
    if st == "mag":
        ln = f'<span style="display:inline-block;width:44px;height:1px;background:{T["line"]};vertical-align:middle;"></span>'
        return box + ln + f'<span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:{M};margin:0 10px;vertical-align:middle;"></span>' + ln + '</section>'
    if st == "min":  return box + f'<span style="display:inline-block;width:40px;height:1px;background:{INK};"></span></section>'
    if st == "neo":
        sq = lambda c: f'<span style="display:inline-block;width:8px;height:8px;background:{c};border-radius:2px;margin:0 4px;vertical-align:middle;"></span>'
        ln = lambda a, b: f'<span style="display:inline-block;width:70px;height:3px;border-radius:2px;background:linear-gradient(90deg,{a},{b});vertical-align:middle;"></span>'
        return box + ln("#FFFFFF", M) + sq(T["line"]) + sq(INK) + sq(T["line"]) + ln(M, "#FFFFFF") + '</section>'
    if st == "geek": return box + f'<span style="font-size:13px;letter-spacing:6px;color:{T["line"]};font-family:{MONO};">/ / /</span></section>'
    if st == "bold": return box + f'<span style="display:inline-block;width:56px;height:5px;border-radius:3px;background:{M};"></span></section>'
    return box + "".join(f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{c};margin:0 6px;"></span>' for c in (T["tint"], M, T["tint"])) + '</section>'

def video_slot(name, T):
    return (f'<section style="margin:20px 0;border:1.5px dashed {T["line"]};border-radius:12px;background:{T["soft"]};padding:18px 16px;text-align:center;">'
            f'<p style="margin:0 0 4px;font-size:15px;font-weight:700;color:{T["main"]};">此处放视频：{esc(name)}</p>'
            f'<p style="margin:0;font-size:13px;color:#888888;">在公众号编辑器里插入视频或动图，然后删掉这个方框</p></section>')

def author_card(T, meta):
    if T["st"] in NEW_ST: return x_author(T, meta)
    if T["st"] == "neo":
        return (f'<section style="margin:52px 0 16px;padding:22px;border:1px solid {T["tint"]};border-radius:18px;background:#FFFFFF;box-shadow:0 12px 32px rgba(17,24,39,0.07);display:flex;align-items:center;">'
                f'<section style="flex-shrink:0;width:72px;height:72px;border-radius:50%;background:{T["tint"]};overflow:hidden;margin-right:16px;"><img src="GIF_URL_HERE" style="display:block;width:72px;height:72px;"/></section>'
                f'<section style="flex:1;"><p style="margin:0;font-size:17px;font-weight:900;color:{INK};">{esc(meta.get("author", "林月半子的AI笔记"))}</p>'
                f'<p style="margin:4px 0 0;font-size:13px;line-height:1.7;color:{GRAY};">{esc(meta.get("slogan", "我是林月半子，教你用AI干掉90%的重复劳动"))}</p>'
                f'<p style="margin:10px 0 0;line-height:1;"><span style="display:inline-block;color:{T["main"]};font-size:12px;font-weight:800;letter-spacing:0.5px;padding:5px 12px;border-radius:20px;border:1px solid {T["line"]};">{esc(meta.get("outro_cta", "点个关注，下一篇见 →"))}</span></p></section></section>')
    box = (f'margin:48px 0 12px;padding:20px 0 0;border-top:1px solid {INK};' if T["st"] in ("min", "mag")
           else f'margin:48px 0 12px;padding:20px;border-radius:{max(T["r"], 6) + 2}px;background:{T["soft"]};border:1px solid {T["tint"]};')
    return (f'<section style="{box}display:flex;align-items:center;">'
            f'<section style="flex-shrink:0;width:72px;height:72px;border-radius:50%;background:{T["tint"]};overflow:hidden;margin-right:16px;"><img src="GIF_URL_HERE" style="display:block;width:72px;height:72px;"/></section>'
            f'<section style="flex:1;"><p style="margin:0;font-size:17px;font-weight:800;color:{INK};">{esc(meta.get("author", "林月半子的AI笔记"))}</p>'
            f'<p style="margin:4px 0 0;font-size:13px;line-height:1.7;color:{GRAY};">{esc(meta.get("slogan", "我是林月半子，教你用AI干掉90%的重复劳动"))}</p>'
            f'<p style="margin:8px 0 0;font-size:13px;font-weight:700;color:{T["main"]};">{esc(meta.get("outro_cta", "点个关注，下一篇见 →"))}</p></section></section>')

def notes_block(notes, T):
    if not notes: return ""
    items = "".join(f'<p style="margin:0 0 6px;font-size:12px;line-height:1.7;color:{MUTE};word-break:break-all;">[{i+1}] {esc(t)}：{esc(u)}</p>' for i, (t, u) in enumerate(notes))
    return f'<section style="margin:36px 0 0;padding-top:14px;border-top:1px solid {BORDER};"><p style="margin:0 0 8px;font-size:13px;font-weight:700;color:{GRAY};">参考链接</p>{items}</section>'


# ---------------- 潮酷风格（neo）：巨型数字/引号做底纹，黑描边，错位色块投影 ----------------
def neo_h2(n, title, sub, T):
    M = T["main"]
    return (f'<section style="margin:56px 0 30px;">'
            f'<p style="margin:0 0 0 -3px;line-height:0.82;height:70px;white-space:nowrap;overflow:hidden;">'
            f'<span style="font-size:92px;line-height:0.82;font-weight:900;font-style:italic;letter-spacing:-3px;color:{T["tint"]};font-family:Helvetica,Arial,sans-serif;">{n:02d}</span>'
            f'<span style="font-size:11px;font-weight:800;letter-spacing:3px;color:{M};margin-left:14px;vertical-align:30px;">{esc(sub.upper()) if sub else "PART " + f"{n:02d}"}</span></p>'
            f'<section style="margin:-20px 0 0 10px;">'
            f'<p style="margin:0;font-size:23px;font-weight:900;color:{INK};line-height:1.4;">{title}</p>'
            f'<section style="margin-top:12px;line-height:0;"><span style="display:inline-block;width:72px;height:6px;border-radius:3px;background:linear-gradient(90deg,{M},{T["line"]});"></span>'
            f'<span style="display:inline-block;width:6px;height:6px;border-radius:3px;background:{INK};margin-left:5px;"></span></section></section></section>')

def neo_h3(m, title, T):
    M = T["main"]
    if m:
        return (f'<section style="margin:32px 0 16px;display:flex;align-items:center;">'
                f'<span style="flex-shrink:0;display:inline-block;background:{INK};color:#FFFFFF;font-size:13px;font-weight:800;padding:5px 14px;border-radius:20px;letter-spacing:1px;margin-right:12px;">{m.group(1)}</span>'
                f'<span style="font-size:18px;font-weight:900;color:{INK};line-height:1.5;">{m.group(2)}</span></section>')
    return (f'<section style="margin:34px 0 14px;display:flex;align-items:center;">'
            f'<span style="flex-shrink:0;display:inline-block;width:18px;height:3px;background:{M};border-radius:2px;margin-right:10px;"></span>'
            f'<span style="font-size:18px;font-weight:900;color:{INK};line-height:1.5;">{title}</span></section>')

def neo_quote(text_html, T):
    """大引号压在左上角当底纹，文字叠在上面"""
    return (f'<section style="margin:32px 0;padding:14px 24px 22px;background:{T["soft"]};border:1px solid {T["tint"]};border-radius:18px;overflow:hidden;">'
            + quote_svg(T["line"], 0.55, 58, "18px 0 8px -2px")
            + f'<section style="margin-top:0;font-size:16px;line-height:1.95;color:{INK};letter-spacing:0.5px;">{text_html}</section>'
            f'<section style="margin-top:10px;text-align:right;line-height:0;"><span style="display:inline-block;width:28px;height:4px;border-radius:2px;background:{T["main"]};"></span></section></section>')

def neo_golden(text_html, T):
    """金句卡：浅色扁平。超大引号当底纹（和大标题的巨型编号同一个手法），文字压在引号下半截上，没有阴影和描边"""
    M = T["main"]
    return (f'<section style="margin:40px 0;padding:1px 28px 30px;background:{T["soft"]};border-radius:22px;overflow:hidden;">'
            + quote_svg(T["line"], 0.45, 96, "26px 0 12px -2px")
            + f'<p style="margin:0;font-size:22px;line-height:1.7;font-weight:900;color:{INK};letter-spacing:0.5px;">{text_html}</p>'
            f'<section style="margin-top:18px;line-height:0;"><span style="display:inline-block;width:56px;height:5px;border-radius:3px;background:linear-gradient(90deg,{M},{T["line"]});vertical-align:middle;"></span>'
            f'<span style="display:inline-block;width:5px;height:5px;border-radius:3px;background:{INK};margin-left:5px;vertical-align:middle;"></span></section></section>')
# ================= 4 套新风格：手账 note / 雅致 zen / 卡片 bento / 暗夜 dark =================
# 没写分支的组件（列表、表格、图片、步骤卡等）自动用标准风格的样子；暗夜在最后统一把浅色底上的文字色换成深色底上的
SERIF_CN = "'Songti SC','STSong','Source Han Serif SC','Noto Serif SC','Noto Serif CJK SC',Georgia,serif"
CN_BIG = "壹贰叁肆伍陆柒捌玖拾"
DK_BG, DK_PANEL, DK_BORDER = "#0F1218", "#151A21", "#2A313C"

def quote_svg(color, opacity=1, w=92, margin="0"):
    """大引号画成 SVG 形状：不依赖 Georgia 字体（大多数安卓手机没有，引号会掉下来压字）"""
    h = round(w * 0.72)
    mark = lambda dx: (f'<circle cx="{18+dx}" cy="47" r="15" fill="{color}"/>'
                       f'<path d="M{3+dx} 47C{3+dx} 26 {13+dx} 11 {32+dx} 3L{36+dx} 10C{24+dx} 17 {19+dx} 27 {20+dx} 37Z" fill="{color}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 64" width="{w}" height="{h}" '
            f'style="display:block;margin:{margin};overflow:visible;"><g opacity="{opacity}">{mark(0)}{mark(40)}</g></svg>')

def x_p_css(st):
    return {"note": "margin:0 0 22px;font-size:16px;line-height:1.95;letter-spacing:0.5px;color:#3D3A36;text-align:justify;",
            "zen":  "margin:0 0 24px;font-size:16px;line-height:2.05;letter-spacing:1px;color:#333333;text-align:justify;",
            "bento":"margin:0 0 22px;font-size:16px;line-height:1.85;letter-spacing:0.3px;color:#1D1D1F;text-align:justify;",
            "dark": "margin:0 0 22px;font-size:16px;line-height:1.9;letter-spacing:0.5px;color:#C5CCD6;text-align:justify;"}[st]

def x_strong(T):
    st = T["st"]
    if st == "note":  return f'font-weight:700;color:#1F1F1F;background:{T["mark"]};padding:2px 4px;border-radius:3px;'
    if st == "zen":   return f'font-weight:700;color:#1F1F1F;background:linear-gradient(transparent 66%,{T["tint"]} 66%);padding:0 2px;'
    if st == "bento": return f'font-weight:700;color:#1D1D1F;background:{T["tint"]};padding:2px 7px;border-radius:7px;'
    return 'font-weight:700;color:#FFFFFF;background:#252C37;padding:2px 6px;border-radius:5px;'

def x_chip(T):
    st = T["st"]
    if st == "zen":   return f'font-family:{SERIF_CN};font-weight:700;color:#FFFFFF;background:{T["main"]};padding:3px 9px;letter-spacing:1px;'
    if st == "bento": return f'background:{T["main"]};color:#FFFFFF;font-weight:700;padding:4px 10px;border-radius:9px;'
    if st == "dark":  return f'background:{T["line"]};color:{DK_BG};font-weight:800;padding:2px 8px;border-radius:4px;'
    return f'background:{T["main"]};color:#FFFFFF;font-weight:700;padding:2px 7px;border-radius:3px;'

def underline_css(T):
    """++下划线++：每种风格一种画法，和荧光笔、色块分得开"""
    st = T["st"]; M = T["main"]
    return {"mag": f"border-bottom:1px solid {M};padding-bottom:3px;", "min": f"border-bottom:2px solid {INK};padding-bottom:1px;",
            "geek": f"border-bottom:2px dashed {M};padding-bottom:2px;", "bold": f"border-bottom:3px solid {M};padding-bottom:1px;",
            "neo": f"border-bottom:2px solid {T['line']};padding-bottom:2px;", "note": f"border-bottom:2px dashed {M};padding-bottom:2px;",
            "zen": f"border-bottom:1px solid {M};padding-bottom:3px;", "bento": f"border-bottom:2px solid {M};padding-bottom:1px;",
            "dark": f"color:#E6EAF0;border-bottom:2px solid {T['line']};padding-bottom:1px;"}.get(st, f"border-bottom:2px solid {M};padding-bottom:1px;")

def x_h2(n, title, sub, T):
    st = T["st"]; M, S, TT, L, K = T["main"], T["soft"], T["tint"], T["line"], T["mark"]
    if st == "note":
        return (f'<section style="margin:52px 0 26px;padding-bottom:16px;border-bottom:1.5px dashed {L};">'
                f'<p style="margin:0;line-height:1;"><span style="display:inline-block;background:{K};color:#1F1F1F;font-size:12px;font-weight:800;letter-spacing:2px;line-height:1;padding:6px 14px;transform:rotate(-3deg);font-family:{MONO};">NO.{n:02d}</span></p>'
                f'<p style="margin:14px 0 0;font-size:23px;font-weight:800;color:#1F1F1F;line-height:1.55;"><span style="background:linear-gradient(transparent 62%,{TT} 62%);padding:0 4px;">{title}</span></p>'
                + (f'<p style="margin:8px 0 0 4px;font-size:11px;letter-spacing:3px;color:#A8A29E;line-height:1.4;">— {esc(sub.upper())}</p>' if sub else '') + '</section>')
    if st == "zen":
        ln = f'<span style="display:inline-block;width:28px;height:1px;background:{L};vertical-align:middle;margin:0 10px;"></span>'
        return (f'<section style="margin:60px 0 34px;text-align:center;">'
                f'<p style="margin:0;line-height:1;"><span style="display:inline-block;width:42px;height:42px;line-height:42px;background:{M};color:#FFFFFF;font-size:21px;font-weight:700;border-radius:5px;font-family:{SERIF_CN};">{CN_BIG[n-1] if n <= 10 else n}</span></p>'
                f'<p style="margin:18px 0 0;font-size:23px;font-weight:700;letter-spacing:3px;color:#1F1F1F;line-height:1.6;font-family:{SERIF_CN};">{title}</p>'
                + (f'<p style="margin:12px 0 0;font-size:10px;letter-spacing:4px;color:#A8A29E;line-height:1.4;">{ln}{esc(sub.upper())}{ln}</p>' if sub else '') + '</section>')
    if st == "bento":
        return (f'<section style="margin:52px 0 26px;background:{S};border-radius:22px;padding:22px 22px 24px;">'
                f'<p style="margin:0;line-height:1;"><span style="display:inline-block;background:{M};color:#FFFFFF;font-size:13px;font-weight:800;line-height:1;padding:6px 13px;border-radius:20px;font-family:Helvetica,Arial,sans-serif;">{n:02d}</span>'
                + (f'<span style="margin-left:10px;font-size:11px;font-weight:600;letter-spacing:2px;color:#86868B;">{esc(sub.upper())}</span>' if sub else '') + '</p>'
                f'<p style="margin:14px 0 0;font-size:24px;font-weight:800;color:#1D1D1F;line-height:1.4;">{title}</p></section>')
    return (f'<section style="margin:54px 0 28px;">'
            f'<p style="margin:0 0 0 -2px;font-size:68px;line-height:0.9;height:46px;font-weight:800;color:#1D242E;font-family:Helvetica,Arial,sans-serif;">{n:02d}</p>'
            + (f'<p style="margin:0;font-size:11px;font-weight:700;letter-spacing:3px;color:{L};line-height:1.4;">{esc(sub.upper())}</p>' if sub else '')
            + f'<p style="margin:8px 0 0;font-size:23px;font-weight:800;color:#FFFFFF;line-height:1.45;">{title}</p>'
            f'<p style="margin:16px 0 0;line-height:0;"><span style="display:inline-block;width:48px;height:3px;border-radius:2px;background:{L};"></span></p></section>')

def x_h3(m, title, T):
    st = T["st"]; M = T["main"]; ink = "#FFFFFF" if st == "dark" else "#1F1F1F"
    if m:
        chip = {"note": f"background:{T['mark']};color:#1F1F1F;transform:rotate(-2deg);", "zen": f"border:1px solid {M};color:{M};font-family:{SERIF_CN};",
                "bento": f"background:{M};color:#FFFFFF;", "dark": f"background:{T['line']};color:{DK_BG};"}[st]
        return (f'<section style="margin:30px 0 14px;display:flex;align-items:center;">'
                f'<span style="flex-shrink:0;display:inline-block;font-size:13px;font-weight:700;padding:4px 14px;border-radius:20px;margin-right:12px;{chip}">{m.group(1)}</span>'
                f'<span style="font-size:18px;font-weight:800;color:{ink};line-height:1.5;">{m.group(2)}</span></section>')
    if st == "zen":
        return f'<section style="margin:34px 0 14px;"><span style="font-size:18px;font-weight:700;color:{ink};font-family:{SERIF_CN};letter-spacing:1px;">{title}</span></section>'
    if st == "note":
        return f'<section style="margin:32px 0 14px;"><span style="font-size:18px;font-weight:800;color:{ink};background:linear-gradient(transparent 60%,{T["mark"]} 60%);padding:0 3px;">{title}</span></section>'
    if st == "bento":
        return f'<section style="margin:32px 0 14px;"><span style="display:inline-block;background:{T["soft"]};color:#1D1D1F;font-size:17px;font-weight:800;padding:6px 14px;border-radius:12px;">{title}</span></section>'
    return f'<section style="margin:32px 0 14px;"><span style="font-size:18px;font-weight:800;color:{ink};border-left:3px solid {T["line"]};padding-left:10px;">{title}</span></section>'

def x_quote(text_html, T):
    st = T["st"]; M, S, TT, L, K = T["main"], T["soft"], T["tint"], T["line"], T["mark"]
    if st == "note":
        return (f'<section style="margin:30px 6px;padding:16px 20px;background:#FFFFFF;border:1.5px dashed {L};border-radius:6px;">'
                f'<section style="font-size:16px;line-height:1.95;color:#3D3A36;">{text_html}</section></section>')
    if st == "zen":
        return (f'<section style="margin:32px 0;padding:6px 0 6px 20px;border-left:2px solid {M};">'
                f'<section style="font-size:16px;line-height:2;color:#444444;letter-spacing:1px;font-family:{SERIF_CN};">{text_html}</section></section>')
    if st == "bento":
        return (f'<section style="margin:28px 0;padding:6px 22px 20px;background:{S};border-radius:20px;">' + quote_svg(TT, 1, 40, "14px 0 4px")
                + f'<section style="font-size:16px;line-height:1.9;color:#1D1D1F;">{text_html}</section></section>')
    return (f'<section style="margin:28px 0;padding:6px 20px 18px;background:{DK_PANEL};border:1px solid {DK_BORDER};border-radius:14px;">' + quote_svg(L, 0.55, 36, "14px 0 4px")
            + f'<section style="font-size:16px;line-height:1.9;color:#E6EAF0;">{text_html}</section></section>')

def x_golden(text_html, T):
    st = T["st"]; M, S, TT, L, K = T["main"], T["soft"], T["tint"], T["line"], T["mark"]
    if st == "note":
        return (f'<section style="margin:44px 6px 40px;background:{S};border:1.5px dashed {L};border-radius:6px;padding:0 22px 24px;text-align:center;">'
                f'<p style="margin:-12px 0 16px;line-height:0;"><span style="display:inline-block;width:84px;height:24px;background:{K};opacity:0.9;transform:rotate(-2deg);"></span></p>'
                f'<p style="margin:0;font-size:19px;line-height:1.75;font-weight:800;color:#1F1F1F;">{text_html}</p></section>')
    if st == "zen":
        return (f'<section style="margin:46px 0;padding:28px 10px;border-top:3px double {L};border-bottom:3px double {L};text-align:center;">'
                f'<p style="margin:0;font-size:20px;line-height:1.9;font-weight:700;letter-spacing:2px;color:#1F1F1F;font-family:{SERIF_CN};"><span style="color:{L};">「</span>{text_html}<span style="color:{L};">」</span></p></section>')
    if st == "bento":
        return (f'<section style="margin:40px 0;background:{S};border-radius:26px;padding:10px 26px 30px;overflow:hidden;">' + quote_svg(TT, 1, 74, "22px 0 14px")
                + f'<p style="margin:0;font-size:22px;line-height:1.6;font-weight:800;color:#1D1D1F;">{text_html}</p></section>')
    return (f'<section style="margin:40px 0;background:{DK_PANEL};border:1px solid {DK_BORDER};border-radius:18px;padding:8px 24px 28px;overflow:hidden;">' + quote_svg(L, 0.55, 64, "22px 0 14px")
            + f'<p style="margin:0;font-size:21px;line-height:1.65;font-weight:800;color:#FFFFFF;">{text_html}</p></section>')

def x_callout(kind, text_html, T):
    st = T["st"]; lab = {"TIP": "小技巧", "NOTE": "说明", "WARN": "注意", "TLDR": "省流版"}.get(kind, kind)
    wn = kind == "WARN"; col = "#D97706" if wn else T["main"]
    if st == "note":
        return (f'<section style="margin:30px 6px;border:1.5px dashed {"#F0B45C" if wn else T["line"]};border-radius:6px;background:#FFFFFF;padding:22px 18px 14px;">'
                f'<p style="margin:-34px 0 10px;line-height:1;"><span style="display:inline-block;background:{"#FDE3B0" if wn else T["mark"]};color:#1F1F1F;font-size:12px;font-weight:800;padding:5px 12px;transform:rotate(-2deg);">{lab}</span></p>'
                f'<section style="font-size:15px;line-height:1.85;color:#3D3A36;">{text_html}</section></section>')
    if st == "zen":
        return (f'<section style="margin:30px 0;padding:16px 4px 6px;border-top:1px solid {col};border-bottom:1px solid {T["tint"]};">'
                f'<p style="margin:0 0 8px;font-size:13px;font-weight:700;letter-spacing:4px;color:{col};font-family:{SERIF_CN};">{lab}</p>'
                f'<section style="font-size:15px;line-height:1.95;color:#444444;">{text_html}</section></section>')
    if st == "bento":
        return (f'<section style="margin:26px 0;border-radius:20px;background:{"#FFF4E0" if wn else T["soft"]};padding:18px 20px;">'
                f'<span style="display:inline-block;background:{col};color:#FFFFFF;font-size:12px;font-weight:800;padding:4px 12px;border-radius:20px;margin-bottom:10px;">{lab}</span>'
                f'<section style="font-size:15px;line-height:1.85;color:#1D1D1F;">{text_html}</section></section>')
    return (f'<section style="margin:26px 0;border-radius:14px;background:{DK_PANEL};border:1px solid {"#6B4A1A" if wn else DK_BORDER};padding:16px 18px;">'
            f'<span style="display:inline-block;background:{"#F0B45C" if wn else T["line"]};color:{DK_BG};font-size:12px;font-weight:800;padding:3px 10px;border-radius:6px;margin-bottom:10px;">{lab}</span>'
            f'<section style="font-size:15px;line-height:1.85;color:#C5CCD6;">{text_html}</section></section>')

def x_prompt(body, title, T):
    st = T["st"]; L = T["line"]; lab = f'{esc(title or "提示词")} · 上下滑动查看 ↕'
    p = lambda col, lh: "".join(f'<p style="margin:0;white-space:pre-wrap;word-break:break-all;font-size:13px;line-height:{lh};color:{col};font-family:{MONO};">{b}</p>' for b in body)
    if st == "note":
        return (f'<section style="margin:28px 0;border:1.5px solid {L};border-radius:6px;background:#FFFFFF;">'
                f'<section style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1.5px dashed {L};">'
                f'<span style="display:inline-block;background:{T["mark"]};color:#1F1F1F;font-size:12px;font-weight:800;letter-spacing:1px;padding:4px 12px;transform:rotate(-2deg);font-family:{MONO};">PROMPT</span>'
                f'<span style="font-size:12px;color:#A8A29E;">{lab}</span></section><section style="max-height:320px;overflow-y:auto;padding:14px 18px;">{p("#5B5A57", 1.9)}</section></section>')
    if st == "zen":
        return (f'<section style="margin:30px 0;border:1px solid {L};padding:4px;"><section style="border:1px solid {T["tint"]};background:#FFFFFF;">'
                f'<section style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid {T["tint"]};">'
                f'<span style="font-size:13px;font-weight:700;letter-spacing:4px;color:{T["main"]};font-family:{SERIF_CN};">PROMPT</span><span style="font-size:12px;color:#A8A29E;">{lab}</span></section>'
                f'<section style="max-height:320px;overflow-y:auto;padding:16px 18px;">{p("#5B5A57", 2)}</section></section></section>')
    if st == "bento":
        return (f'<section style="margin:26px 0;border-radius:20px;background:#F5F5F7;overflow:hidden;">'
                f'<section style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px 0;">'
                f'<span style="display:inline-block;background:#1D1D1F;color:#FFFFFF;font-size:12px;font-weight:800;letter-spacing:1px;padding:4px 12px;border-radius:20px;font-family:{MONO};">PROMPT</span>'
                f'<span style="font-size:12px;color:#86868B;">{lab}</span></section><section style="max-height:320px;overflow-y:auto;padding:14px 18px 18px;">{p("#515154", 1.85)}</section></section>')
    return (f'<section style="margin:26px 0;border:1px solid {DK_BORDER};border-radius:14px;background:{DK_PANEL};overflow:hidden;">'
            f'<section style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid {DK_BORDER};background:#1A2029;">'
            f'<span style="display:inline-block;background:{L};color:{DK_BG};font-size:12px;font-weight:800;letter-spacing:1px;padding:4px 12px;border-radius:20px;font-family:{MONO};">PROMPT</span>'
            f'<span style="font-size:12px;color:#6B7685;">{lab}</span></section><section style="max-height:320px;overflow-y:auto;padding:14px 18px;">{p("#9FB0C3", 1.85)}</section></section>')

def x_hr(T):
    st = T["st"]; M, L, K, TT = T["main"], T["line"], T["mark"], T["tint"]
    if st == "note":
        return (f'<section style="margin:40px 0;display:flex;align-items:center;justify-content:center;">'
                f'<span style="display:inline-block;width:70px;border-top:1.5px dashed {L};"></span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{K};border:1.5px solid {L};margin:0 12px;"></span>'
                f'<span style="display:inline-block;width:70px;border-top:1.5px dashed {L};"></span></section>')
    if st == "zen":
        ln = f'<span style="display:inline-block;width:56px;height:1px;background:{L};vertical-align:middle;"></span>'
        return (f'<section style="margin:44px 0;text-align:center;line-height:1;">{ln}'
                f'<span style="display:inline-block;width:7px;height:7px;background:{M};transform:rotate(45deg);vertical-align:middle;margin:0 14px;"></span>{ln}</section>')
    if st == "bento":
        return f'<section style="margin:40px 0;text-align:center;line-height:0;"><span style="display:inline-block;width:44px;height:5px;border-radius:3px;background:{TT};"></span></section>'
    return ('<section style="margin:40px 0;text-align:center;line-height:1;">'
            + "".join(f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{c};margin:0 6px;"></span>' for c in (DK_BORDER, L, DK_BORDER)) + '</section>')

def x_author(T, meta):
    st = T["st"]
    box = {"note": f'border-radius:6px;background:#FFFFFF;border:1.5px dashed {T["line"]};', "zen": f'border-top:1px solid {T["line"]};border-bottom:1px solid {T["line"]};',
           "bento": f'border-radius:24px;background:{T["soft"]};', "dark": f'border-radius:16px;background:{DK_PANEL};border:1px solid {DK_BORDER};'}[st]
    c1, c2, c3, av = (("#FFFFFF", "#8B95A3", T["line"], "#232A35") if st == "dark" else ("#1F1F1F", "#78716C", T["main"], T["tint"]))
    return (f'<section style="margin:48px 0 12px;padding:20px;{box}display:flex;align-items:center;">'
            f'<section style="flex-shrink:0;width:72px;height:72px;border-radius:50%;background:{av};overflow:hidden;margin-right:16px;"><img src="GIF_URL_HERE" style="display:block;width:72px;height:72px;"/></section>'
            f'<section style="flex:1;"><p style="margin:0;font-size:17px;font-weight:800;color:{c1};">{esc(meta.get("author", "林月半子的AI笔记"))}</p>'
            f'<p style="margin:4px 0 0;font-size:13px;line-height:1.7;color:{c2};">{esc(meta.get("slogan", "我是林月半子，教你用AI干掉90%的重复劳动"))}</p>'
            f'<p style="margin:8px 0 0;font-size:13px;font-weight:700;color:{c3};">{esc(meta.get("outro_cta", "点个关注，下一篇见 →"))}</p></section></section>')

def dark_fix(h):
    """暗夜：没写分支的组件（正文列表、表格、图注、小标题等）在深色底上要换成浅色字。SVG 里的颜色不动"""
    parts = re.split(r"(<svg[\s\S]*?</svg>)", h)
    rep = [("color:#111827", "color:#FFFFFF"), ("color:#3F3F46", "color:#C5CCD6"), ("color:#1F2937", "color:#E6EAF0"), ("color:#374151", "color:#E6EAF0"),
           ("color:#6B7280", "color:#8B95A3"), ("color:#94A3B8", "color:#6B7685"), ("background:#FFFFFF", f"background:{DK_PANEL}"),
           ("background:#F8FAFC", f"background:{DK_PANEL}"), ("border:1px solid #E5E7EB", f"border:1px solid {DK_BORDER}"),
           ("border-top:1px solid #F1F2F4", f"border-top:1px solid {DK_BORDER}"), ("border-bottom:1px solid #E5E7EB", f"border-bottom:1px solid {DK_BORDER}"),
           ("color:#52607A", "color:#9FB0C3")]
    for k in range(0, len(parts), 2):
        for a, b in rep: parts[k] = parts[k].replace(a, b)
    return "".join(parts)

# ---------------- 公众号会删掉没有文字的空元素：装饰色块一律画成 SVG ----------------
def _px(v):
    m = re.match(r"(-?[\d.]+)px", v.strip()); return float(m.group(1)) if m else None
def _r(v): return f"{v:.2f}".rstrip("0").rstrip(".")
def _deco_svg(style):
    d = {}
    for part in style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1); d[k.strip()] = v.strip()
    w = _px(d.get("width", "")); h = _px(d.get("height", ""))
    if w is None: return None
    keep = [f"{k}:{d[k]}" for k in ("margin", "margin-left", "margin-right", "margin-top", "margin-bottom", "vertical-align", "flex-shrink") if k in d]
    if "border-top" in d and h is None:
        bw, bs, bc = d["border-top"].split(); t = _px(bw); h = max(2, round(t + 0.5))
        dash = ' stroke-dasharray="4 3"' if bs == "dashed" else ""
        inner = f'<line x1="0" y1="{_r(h/2)}" x2="{_r(w)}" y2="{_r(h/2)}" stroke="{bc}" stroke-width="{_r(t)}"{dash}/>'
    else:
        if h is None: return None
        br = d.get("border-radius", "0"); rx = min(w, h) / 2 if "%" in br else min(_px(br) or 0, min(w, h) / 2)
        bg = d.get("background", ""); stroke = ""; sw = 0
        if "border" in d:
            bw, bs, bc = d["border"].split(); sw = _px(bw); stroke = f' stroke="{bc}" stroke-width="{_r(sw)}"'
        g = re.match(r"linear-gradient\(90deg,\s*(#[0-9A-Fa-f]{6}),\s*(#[0-9A-Fa-f]{6})\)", bg)
        if g:                                   # 渐变：公众号会删 SVG 渐变，用一排细条逐渐变淡拼出来
            c1, c2 = g.groups(); a, b_ = rx, w - rx; n = max(8, int((b_ - a) / 1.5)); sw_ = (b_ - a) / n
            inner = (f'<rect x="0" y="0" width="{_r(w)}" height="{_r(h)}" rx="{_r(rx)}" fill="{c2}"/>'
                     f'<rect x="0" y="0" width="{_r(2*rx)}" height="{_r(h)}" rx="{_r(rx)}" fill="{c1}"/>')
            for i in range(n):
                inner += f'<rect x="{_r(a+i*sw_)}" y="0" width="{_r(sw_)}" height="{_r(h)}" fill="{c1}" fill-opacity="{1-(i+0.5)/n:.3f}" shape-rendering="crispEdges"/>'
        else:
            if (not bg and not stroke) or "(" in bg: return None
            o = sw / 2
            inner = f'<rect x="{_r(o)}" y="{_r(o)}" width="{_r(w-sw)}" height="{_r(h-sw)}" rx="{_r(max(0, rx-o))}" fill="{bg or "none"}"{stroke}/>'
        tr = re.match(r"rotate\((-?[\d.]+)deg\)", d.get("transform", ""))
        if tr: inner = f'<g transform="rotate({tr.group(1)} {_r(w/2)} {_r(h/2)})">{inner}</g>'
        if "opacity" in d: inner = f'<g opacity="{d["opacity"]}">{inner}</g>'
    disp = "display:block" if d.get("display") == "block" else "display:inline-block"
    st = ";".join([disp, "overflow:visible"] + keep)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_r(w)} {_r(h)}" width="{_r(w)}" height="{_r(h)}" style="{st};">{inner}</svg>'

def fix_empty(h):
    return re.sub(r'<span style="([^"]*)"></span>', lambda m: _deco_svg(m.group(1)) or m.group(0), h)

def plain_md(md):
    """「复制 Markdown」用的纯正文：去掉图片、视频、动画卡和 [] 占位，标记符号去掉，方便贴到朱雀做 AI 检测"""
    out, fence, lang, buf = [], False, "", []
    for ln in md.split("\n"):
        s = ln.strip()
        m = re.match(r"^(```+|~~~+)\s*([\w-]*)", s)
        if m and not fence: fence, lang, buf = True, m.group(2).lower(), []; continue
        if fence and (s.startswith("```") or s.startswith("~~~")):
            fence = False
            if lang in ("prompt", "promptbox", "text", ""): out += ["> " + x for x in buf if x.strip()]
            continue
        if fence: buf.append(ln); continue
        if re.match(r"^!\[|^\[[^\]]*\.(mp4|mov|gif)\]$|^\[(截图|可补|可选|视频|GIF)", s) or s.startswith("^"): continue
        s = re.sub(r"\[!(\w+)\]\s*", "", s)
        s = re.sub(r"\*\*|==|\+\+|~~", "", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        s = re.sub(r"[，,]?\[可补[^\]]*\]", "", s)
        out.append(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()

# ================= 动画 SVG 卡（```svg-xxx 代码块）=================
# 规则沿用 wechat-svg-cards：只用 SMIL、无 id/class/渐变/emoji、标题胶囊 t=0 可见、循环播放
SW, SD, S_OUT = 750, 10.0, 9.1          # 宽度、一轮时长、开始淡出的时刻
SFONT = "'PingFang SC','Helvetica Neue','Microsoft YaHei',sans-serif"
sk = lambda t: round(min(max(t / SD, 0), 1), 4)
sR = lambda v: f"{v:.1f}".rstrip('0').rstrip('.')
def scw(c, size): return size if ord(c) > 255 else size * 0.56
def stw(s, size): return sum(scw(c, size) for c in s)

def swrap(s, size, maxw):
    lines, cur, w = [], "", 0
    for c in s:
        cw = scw(c, size)
        if w + cw > maxw and cur:
            lines.append(cur); cur, w = "", 0
            if c == " ": continue
        cur += c; w += cw
    if cur: lines.append(cur)
    return lines or [""]

def sA(attr, vals, ts, spline=None, typ=None):
    kt = ";".join(str(sk(t)) for t in ts); vs = ";".join(str(v) for v in vals); ex = ""
    if spline:
        ex = f' calcMode="spline" keySplines="{";".join([spline] * (len(ts) - 1))}"'
    tag = f'animateTransform attributeName="transform" type="{typ}"' if typ else f'animate attributeName="{attr}"'
    return f'<{tag} values="{vs}" keyTimes="{kt}"{ex} dur="{SD}s" repeatCount="indefinite"/>'

def s_in(t, d=0.35):
    return sA("opacity", [0, 0, 1, 1, 0, 0], [0, t, t + d, S_OUT, S_OUT + 0.4, SD])

def s_fade(inner, t, dx=0, dy=14):
    mv = sA(None, [f"{dx} {dy}", f"{dx} {dy}", "0 0", "0 0"], [0, t, t + 0.45, SD], "0.23 1 0.32 1", "translate") if (dx or dy) else ""
    return f'<g opacity="0">{s_in(t)}<g>{mv}{inner}</g></g>'

def s_grow(attr, a, b, t, d=0.4):
    return sA(attr, [a, a, b, b], [0, t, t + d, SD], "0.42 0 0.58 1")

def s_text(x, y, s, size=22, fill="#333333", w=400, anchor="start"):
    return f'<text x="{sR(x)}" y="{sR(y)}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>'

def s_check(cx, cy, t, col, r=16):
    L = round(r * 2.1)
    return (f'<g opacity="0">{s_in(t, 0.1)}<circle cx="{sR(cx)}" cy="{sR(cy)}" r="{r}" fill="#FFFFFF" stroke="{col}" stroke-width="2.5"/>'
            f'<path d="M{sR(cx-r*0.45)} {sR(cy)}l{sR(r*0.32)} {sR(r*0.32)}l{sR(r*0.6)} {sR(-r*0.62)}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-dasharray="{L}" stroke-dashoffset="{L}">{s_grow("stroke-dashoffset", L, 0, t + 0.05, 0.35)}</path></g>')

def s_frame(title, body, H, T):
    """卡片外框 + 标题（t=0 就可见）。外框跟着风格变，里面的内容各风格通用"""
    st = T.get("st", "std"); M = T["main"]; cap_w = stw(title, 24) + 48; W = SW; Hh = H
    if st == "mag":
        bg = (f'<rect x="1" y="1" width="{SW-2}" height="{sR(H-2)}" rx="4" fill="#FFFFFF" stroke="{T["line"]}" stroke-width="1.5"/>'
              + s_text(40, 64, title, 26, INK, 800) + f'<rect x="40" y="80" width="44" height="3" fill="{M}"/>')
    elif st == "min":
        bg = (f'<rect x="1" y="1" width="{SW-2}" height="{sR(H-2)}" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'
              f'<rect x="1" y="1" width="{SW-2}" height="88" fill="{INK}"/>' + s_text(40, 56, title, 25, "#FFFFFF", 800))
    elif st == "geek":
        bg = (f'<rect x="1" y="1" width="{SW-2}" height="{sR(H-2)}" rx="10" fill="{T["soft"]}" stroke="{T["line"]}" stroke-width="1.5" stroke-dasharray="7 6"/>'
              f'<rect x="36" y="30" width="{sR(cap_w + 26)}" height="48" rx="8" fill="#0B0B0C"/>'
              f'<text x="52" y="62" font-size="22" font-weight="700" fill="{T["line"]}" font-family="Menlo,Consolas,monospace">&gt;</text>'
              + s_text(36 + 26 + cap_w / 2, 62, title, 24, "#FFFFFF", 800, "middle"))
    elif st == "bold":
        bg = (f'<rect x="0" y="0" width="{SW}" height="{sR(H)}" rx="28" fill="{T["tint"]}"/>'
              f'<rect x="36" y="28" width="{sR(cap_w)}" height="52" rx="26" fill="{M}"/>' + s_text(36 + cap_w / 2, 63, title, 25, "#FFFFFF", 800, "middle"))
    elif st == "neo":       # 质感：白卡 + 细线 + 叠三层淡色当柔和阴影（公众号不支持滤镜）
        Hh = H + 18
        bg = ("".join(f'<rect x="{8-k*2}" y="{10+k*3}" width="{SW-16+k*4}" height="{sR(H-6)}" rx="26" fill="#0F172A" opacity="0.028"/>' for k in range(3))
              + f'<rect x="6" y="1" width="{SW-12}" height="{sR(H)}" rx="24" fill="#FFFFFF" stroke="{T["tint"]}" stroke-width="1.5"/>'
              f'<rect x="40" y="38" width="5" height="34" rx="2.5" fill="{M}"/>' + s_text(58, 65, title, 27, INK, 800))
    elif st == "dark":
        bg = (f'<rect x="0" y="0" width="{SW}" height="{sR(H)}" rx="24" fill="#151A21" stroke="#2A313C" stroke-width="2"/>'
              f'<rect x="40" y="38" width="5" height="34" rx="2.5" fill="{T["line"]}"/>' + s_text(58, 65, title, 27, "#FFFFFF", 800))
    else:
        bg = (f'<rect x="0" y="0" width="{SW}" height="{sR(H)}" rx="24" fill="{T["soft"]}"/>'
              f'<rect x="36" y="30" width="{sR(cap_w)}" height="48" rx="24" fill="{M}"/>' + s_text(36 + cap_w / 2, 62, title, 24, "#FFFFFF", 800, "middle"))
    return (f'<section style="margin:28px 0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {sR(Hh)}" width="100%" '
            f'style="display:block;max-width:100%;height:auto;margin:0 auto;font-family:{SFONT}">' + bg + body + '</svg></section>')

def s_footer(quote, y, t, T):
    if not quote: return "", y
    w = min(stw(quote, 24), 640); x0 = (SW - w) / 2
    return (s_fade(s_text(SW / 2, y + 30, quote, 24, INK, 800, "middle"), t, 0, 10)
            + f'<g opacity="0">{s_in(t + 0.3, 0.05)}<line x1="{sR(x0)}" y1="{sR(y+44)}" x2="{sR(x0)}" y2="{sR(y+44)}" stroke="{T["main"]}" stroke-width="5" stroke-linecap="round">{s_grow("x2", sR(x0), sR(x0+w), t + 0.3, 0.5)}</line></g>'), y + 80

def s_split(lines):
    rows, quote = [], ""
    for l in lines:
        s = l.strip()
        if not s: continue
        if s.startswith(">"): quote = s[1:].strip(); continue
        if re.match(r"^\|?\s*:?-{2,}", s) and set(s) <= set("|-: "): continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        hl = any("★" in c for c in cells)
        rows.append(([c.replace("★", "").strip() for c in cells], hl))
    return rows, quote

def svg_table(title, lines, T):
    rows, quote = s_split(lines)
    head, body = rows[0][0], rows[1:]
    n = len(head); X0, WID = 40, SW - 80
    need = [max([stw(head[c], 20)] + [stw(r[0][c] if c < len(r[0]) else "", 22) for r in body]) + 32 for c in range(n)]
    tot = sum(need); cw = [max(100, WID * w / tot) for w in need]; s_ = sum(cw); cw = [c * WID / s_ for c in cw]
    xs = [X0 + sum(cw[:i]) for i in range(n)]
    o = [f'<rect x="{X0}" y="104" width="{WID}" height="50" rx="12" fill="{T["tint"]}"/>']
    o += [s_text(xs[c] + 18, 136, head[c], 20, T["main"], 800) for c in range(n)]
    y = 166; t = 0.5
    for i, (cells, hl) in enumerate(body):
        wl = [swrap(cells[c] if c < len(cells) else "", 22, cw[c] - 30) for c in range(n)]
        h = max(len(w) for w in wl) * 32 + 30
        inner = (f'<rect x="{X0}" y="{sR(y)}" width="{WID}" height="{sR(h)}" rx="12" fill="#FFFFFF" stroke="{T["main"] if hl else T["tint"]}" stroke-width="{2.5 if hl else 1.5}"/>'
                 + (f'<rect x="{X0}" y="{sR(y)}" width="6" height="{sR(h)}" rx="3" fill="{T["main"]}"/>' if hl else ""))
        for c in range(n):
            for j, ln in enumerate(wl[c]):
                inner += s_text(xs[c] + 18, y + 36 + j * 32, ln, 22, T["main"] if (hl and c == 0) else (INK if c == 0 else BODY), 700 if c == 0 else 400)
        o.append(s_fade(inner, t, -24, 0)); y += h + 10; t += 0.35
    if any(hl for _, hl in body):
        o.append(f'<g opacity="0">{s_in(t + 0.1, 0.1)}' + s_text(SW - 52, 136, "★ 重点", 18, T["main"], 800, "end") + '</g>')
    f, y = s_footer(quote, y + 6, t + 0.4, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_bars(title, lines, T):
    rows, quote = s_split(lines)
    vals = [float(re.sub(r"[^\d.]", "", r[0][1]) or 0) for r in rows]; vmax = max(vals) or 1
    hls = [hl for _, hl in rows]
    if not any(hls): hls = [v == vmax for v in vals]
    lw = min(220, max(stw(r[0][0], 24) for r in rows) + 24); bx = 40 + lw; bwmax = SW - 40 - bx - 110
    o = []; y = 116; t = 0.5
    for i, ((cells, _), v) in enumerate(zip(rows, vals)):
        col = T["main"] if hls[i] else T["line"]; w = max(8, bwmax * v / vmax); cy = y + 22
        txt = cells[2] if len(cells) > 2 and cells[2] else cells[1]
        o.append(s_fade(s_text(40, cy + 9, cells[0], 24, INK, 700 if hls[i] else 500), t, -16, 0))
        o.append(f'<g opacity="0">{s_in(t, 0.1)}<rect x="{sR(bx)}" y="{sR(cy-16)}" width="{sR(bwmax)}" height="32" rx="16" fill="#FFFFFF"/>'
                 f'<rect x="{sR(bx)}" y="{sR(cy-16)}" width="0" height="32" rx="16" fill="{col}">{s_grow("width", 0, sR(w), t + 0.1, 0.6)}</rect></g>')
        o.append(f'<g opacity="0">{s_in(t + 0.6, 0.2)}' + s_text(bx + w + 14, cy + 9, txt, 24, T["main"] if hls[i] else GRAY, 800) + '</g>')
        y += 64; t += 0.45
    f, y = s_footer(quote, y + 4, t + 0.4, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_steps(title, lines, T):
    rows, quote = s_split(lines)
    o = []; y = 108; t = 0.5; X0, WID = 40, SW - 80
    for i, (cells, hl) in enumerate(rows):
        tl = swrap(cells[0], 24, WID - 170); sl = swrap(cells[1], 19, WID - 170) if len(cells) > 1 and cells[1] else []
        h = 36 + len(tl) * 32 + len(sl) * 28 + (6 if sl else 0)
        inner = (f'<rect x="{X0}" y="{sR(y)}" width="{WID}" height="{sR(h)}" rx="18" fill="#FFFFFF" stroke="{T["tint"]}" stroke-width="1.5"/>'
                 f'<circle cx="{X0+46}" cy="{sR(y+h/2)}" r="24" fill="{T["main"]}"/>' + s_text(X0 + 46, y + h / 2 + 9, str(i + 1), 24, "#FFFFFF", 800, "middle"))
        ty = y + 18 + 26
        for ln in tl: inner += s_text(X0 + 92, ty, ln, 24, INK, 800); ty += 32
        ty += 4
        for ln in sl: inner += s_text(X0 + 92, ty, ln, 19, GRAY); ty += 28
        o.append(s_fade(inner, t, -28, 0)); o.append(s_check(X0 + WID - 44, y + h / 2, t + 0.45, T["main"]))
        y += h + 14; t += 0.6
    f, y = s_footer(quote, y + 4, t + 0.3, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_timeline(title, lines, T):
    rows, quote = s_split(lines); n = len(rows[:6]); rows = rows[:6]
    xa, xb = 90, SW - 90; xs = [xa + (xb - xa) * i / max(n - 1, 1) for i in range(n)]
    span = (xb - xa) / max(n - 1, 1); ly = 196; t0, dur = 0.5, 0.45 * n
    o = [f'<g opacity="0">{s_in(t0, 0.05)}<line x1="{xa}" y1="{ly}" x2="{xa}" y2="{ly}" stroke="{T["line"]}" stroke-width="4" stroke-linecap="round">{s_grow("x2", xa, xb, t0, dur)}</line></g>']
    maxl = 1
    for i, (cells, hl) in enumerate(rows):
        ti = t0 + dur * (xs[i] - xa) / max(xb - xa, 1)
        tl = swrap(cells[1] if len(cells) > 1 else "", 19, min(span - 14, 220)); maxl = max(maxl, len(tl))
        inner = (s_text(xs[i], ly - 30, cells[0], 22, T["main"], 800, "middle")
                 + f'<circle cx="{sR(xs[i])}" cy="{ly}" r="{12 if hl else 10}" fill="{T["main"]}" stroke="#FFFFFF" stroke-width="4"/>'
                 + "".join(s_text(xs[i], ly + 46 + j * 28, ln, 19, INK if hl else BODY, 700 if hl else 400, "middle") for j, ln in enumerate(tl)))
        o.append(s_fade(inner, ti, 0, 12))
    y = ly + 46 + maxl * 28
    f, y = s_footer(quote, y, t0 + dur + 0.4, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_breakdown(title, lines, T):
    rows, quote = s_split(lines)
    lw = max(stw(r[0][0], 20) for r in rows) + 30; tx = 40 + lw + 18; tmax = SW - 40 - tx
    o = []; y = 112; t = 0.5
    for cells, hl in rows:
        tl = swrap(cells[1] if len(cells) > 1 else "", 22, tmax); h = len(tl) * 36
        o.append(s_fade(f'<rect x="40" y="{sR(y-2)}" width="{sR(lw)}" height="36" rx="18" fill="{T["main"] if hl else T["tint"]}"/>'
                        + s_text(40 + lw / 2, y + 23, cells[0], 20, "#FFFFFF" if hl else T["main"], 800, "middle"), t, 0, 0))
        for j, ln in enumerate(tl):
            ly = y + j * 36; w = stw(ln, 22) + 12; ts = t + 0.35 + j * 0.25
            o.append(f'<g opacity="0">{s_in(t + 0.15, 0.2)}'
                     f'<rect x="{sR(tx-6)}" y="{sR(ly+1)}" width="0" height="32" rx="6" fill="{T["main"] if hl else T["tint"]}">{s_grow("width", 0, sR(w), ts, 0.35)}</rect>'
                     f'<text x="{sR(tx)}" y="{sR(ly+25)}" font-size="22" font-weight="{700 if hl else 400}" fill="#9CA3AF">{sA("fill", ["#9CA3AF", "#9CA3AF", "#FFFFFF" if hl else INK, "#FFFFFF" if hl else INK], [0, ts + 0.2, ts + 0.35, SD])}{esc(ln)}</text></g>')
        y += max(h, 36) + 20; t += 0.35 + len(tl) * 0.25 + 0.15
    f, y = s_footer(quote, y, t + 0.2, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_compare(title, lines, T):
    rows, quote = s_split(lines)
    (lt, rt), items = rows[0][0][:2], rows[1:]
    cw = 300; lx, rx = 40, SW - 40 - cw; tw_ = cw - 74
    wl = [(swrap(c[0], 21, tw_), swrap(c[1] if len(c) > 1 else "", 21, tw_)) for c, _ in items]
    hs = [max(len(a), len(b)) * 30 + 26 for a, b in wl]
    top = 112; H_ = 64 + sum(hs) + 10 * (len(hs) - 1) + 20
    o = [s_fade(f'<rect x="{lx}" y="{top}" width="{cw}" height="{H_}" rx="18" fill="#FFFFFF" stroke="{BORDER}" stroke-width="1.5"/>' + s_text(lx + cw / 2, top + 42, lt, 22, GRAY, 800, "middle"), 0.3, 0, 10),
         s_fade(f'<rect x="{rx}" y="{top}" width="{cw}" height="{H_}" rx="18" fill="#FFFFFF" stroke="{T["main"]}" stroke-width="2.5"/>'
                f'<rect x="{rx}" y="{top}" width="{cw}" height="60" rx="18" fill="{T["main"]}"/><rect x="{rx}" y="{top+40}" width="{cw}" height="20" fill="{T["main"]}"/>'
                + s_text(rx + cw / 2, top + 42, rt, 22, "#FFFFFF", 800, "middle"), 0.5, 0, 10),
         f'<g opacity="0">{s_in(0.7)}<path d="M{SW/2-14} {top+H_/2-14}L{SW/2+10} {top+H_/2}L{SW/2-14} {top+H_/2+14}" fill="none" stroke="{T["main"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>']
    y = top + 74; t = 0.9
    for (a, b), h in zip(wl, hs):
        cy = y + 18
        o.append(s_fade(f'<circle cx="{lx+28}" cy="{sR(cy)}" r="11" fill="#E5E7EB"/><path d="M{lx+24} {sR(cy-4)}l8 8M{lx+32} {sR(cy-4)}l-8 8" stroke="#9CA3AF" stroke-width="2.4" stroke-linecap="round"/>'
                        + "".join(s_text(lx + 50, y + 25 + j * 30, ln, 21, "#9CA3AF") for j, ln in enumerate(a)), t, -14, 0))
        o.append(s_fade(f'<circle cx="{rx+28}" cy="{sR(cy)}" r="11" fill="{T["main"]}"/><path d="M{rx+23} {sR(cy)}l4 4l7 -8" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
                        + "".join(s_text(rx + 50, y + 25 + j * 30, ln, 21, INK, 700) for j, ln in enumerate(b)), t + 0.3, 14, 0))
        y += h + 10; t += 0.6
    f, y2 = s_footer(quote, top + H_ + 16, t + 0.2, T); o.append(f)
    return s_frame(title, "".join(o), (y2 if quote else top + H_) + 24, T)

def svg_concept(title, lines, T):
    """概念对比时间线：灰色虚线是「以前」，主题色实线一段段画出来是「现在」，沿途节点点亮"""
    rows, quote = s_split([l for l in lines if not l.strip().startswith("!")])
    notes = [l.strip()[1:].strip() for l in lines if l.strip().startswith("!")]
    lead = [r[0][0] for r in rows if len(r[0]) == 1]; tracks = [r for r in rows if len(r[0]) > 1][:2]
    old, new = (tracks + [None])[:2] if len(tracks) == 2 else (None, tracks[0])
    M = T["main"]; o = []; y = 104; t = 0.4
    for ld in lead[:1]:
        for ln in swrap(ld, 26, SW - 80):
            y += 36; o.append(s_fade(s_text(40, y, ln, 26, INK, 800), t, 0, 10))
        y += 14; t += 0.4
    lw = min(230, max(stw(tr[0][0], 21) for tr in (old, new) if tr) + 34); xa, xb = 40 + lw + 34, SW - 70
    def track(tr, y, t, live):
        cells = tr[0]; nodes = cells[1:5]; n = len(nodes); col = M if live else "#B6BCC6"
        xs = [xa + (xb - xa) * (i + 0.5) / n for i in range(n)]; span = (xb - xa) / n; dur = 0.5 * n if live else 0.3
        out = [s_fade(f'<rect x="40" y="{sR(y-19)}" width="{sR(lw)}" height="38" rx="19" fill="{M if live else "#E5E7EB"}"/>'
                      + s_text(40 + lw / 2, y + 7, cells[0], 21, "#FFFFFF" if live else GRAY, 800, "middle"), t, -12, 0)]
        dash = "" if live else ' stroke-dasharray="3 9"'
        out.append(f'<g opacity="0">{s_in(t + 0.15, 0.05)}<line x1="{sR(xa)}" y1="{sR(y)}" x2="{sR(xa)}" y2="{sR(y)}" stroke="{col}" stroke-width="{5 if live else 4}" stroke-linecap="round"{dash}>{s_grow("x2", sR(xa), sR(xb), t + 0.15, dur)}</line></g>')
        maxl = 1
        for i, nd in enumerate(nodes):
            ti = t + 0.15 + dur * (xs[i] - xa) / (xb - xa); tl = swrap(nd, 19, span - 12); maxl = max(maxl, len(tl))
            out.append(s_fade(f'<circle cx="{sR(xs[i])}" cy="{sR(y)}" r="{11 if live else 8}" fill="{col if live else "#FFFFFF"}" stroke="{"#FFFFFF" if live else col}" stroke-width="{4 if live else 3}"/>'
                              + "".join(s_text(xs[i], y + 40 + j * 26, ln, 19, INK if live else "#9CA3AF", 700 if live else 400, "middle") for j, ln in enumerate(tl)), ti, 0, 8))
        return out, y + 40 + maxl * 26, t + 0.15 + dur + 0.3
    if old: a, y2, t = track(old, y + 34, t, False); o += a; y = y2 + 6
    a, y2, t = track(new, y + 34, t, True); o += a; y = y2 + 4
    for nt in notes[:1]:
        tl = swrap(nt, 21, SW - 140); h = len(tl) * 32 + 28
        o.append(s_fade(f'<rect x="40" y="{sR(y)}" width="{SW-80}" height="{sR(h)}" rx="14" fill="#FFFFFF" stroke="{T["line"]}" stroke-width="2" stroke-dasharray="8 6"/>'
                        + "".join(s_text(SW / 2, y + 38 + j * 32, ln, 21, M, 700, "middle") for j, ln in enumerate(tl)), t, 0, 10))
        y += h + 14; t += 0.5
    f, y = s_footer(quote, y + 4, t + 0.2, T); o.append(f)
    return s_frame(title, "".join(o), y + 24, T)

def svg_phone(title, lines, T):
    """手机演示卡：左边手机里一幕一幕轮播，右边功能列表的高亮跟着走。是示意，不是真实截图"""
    rows, _ = s_split(lines)
    subs = [r[0][0] for r in rows if len(r[0]) == 1]; sc = [r[0] for r in rows if len(r[0]) > 1][:5]
    sub = subs[0] if subs else "示意演示，非真实截图"
    M = T["main"]; n = len(sc); S = 2.8; D_ = n * S; kk = lambda t: round(min(max(t / D_, 0), 1), 4)
    def A(attr, vals, ts, disc=False):
        return (f'<animate attributeName="{attr}" values="{";".join(str(v) for v in vals)}" keyTimes="{";".join(str(kk(t)) for t in ts)}"'
                + (' calcMode="discrete"' if disc else "") + f' dur="{sR(D_)}s" repeatCount="indefinite"/>')
    def win(i, a=0.0, f=0.25):     # 第 i 幕里，从 a 秒开始显示到这一幕结束
        t0, t1 = i * S + a, (i + 1) * S
        if i == 0 and a == 0: return A("opacity", [1, 1, 0, 0], [0, t1 - 0.25, t1, D_])
        return A("opacity", [0, 0, 1, 1, 0, 0], [0, t0, t0 + f, t1 - 0.25, t1, D_])
    px, py, pw, ph = 44, 132, 262, 520; sx, sy, sw_, sh = px + 12, py + 12, pw - 24, ph - 24
    o = [s_text(40, 112, sub, 19, GRAY),
         f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="42" fill="{INK}"/>',
         f'<rect x="{sx}" y="{sy}" width="{sw_}" height="{sh}" rx="31" fill="#F3F4F6"/>',
         f'<rect x="{px + pw / 2 - 36}" y="{sy + 10}" width="72" height="18" rx="9" fill="{INK}"/>']
    for i, c in enumerate(sc):
        name, who, text = c[0], (c[1] if len(c) > 2 else ""), c[-1]
        me = who in ("我", "me", "Me", "用户")
        tl = swrap(text, 19, sw_ - 74); bw = max(stw(l, 19) for l in tl) + 30; bh = len(tl) * 28 + 22
        bx = sx + sw_ - 16 - bw if me else sx + 16; by = sy + 132
        g = [f'<g opacity="{1 if i == 0 else 0}">{win(i)}'
             + s_text(px + pw / 2, sy + 66, name, 20, INK, 800, "middle")
             + f'<rect x="{sx + 20}" y="{sy + 82}" width="{sw_ - 40}" height="1.5" fill="#E5E7EB"/>'
             + (s_text(px + pw / 2, sy + 112, who, 15, "#9CA3AF", 400, "middle") if who and not me else "") + '</g>',
             f'<g opacity="0">{win(i, 0.5)}<rect x="{sR(bx)}" y="{by}" width="{sR(bw)}" height="{bh}" rx="16" fill="{M if me else "#FFFFFF"}"/>'
             + "".join(s_text(bx + 15, by + 31 + j * 28, l, 19, "#FFFFFF" if me else INK) for j, l in enumerate(tl)) + '</g>',
             f'<g opacity="0">{win(i, 1.3)}<circle cx="{px + pw / 2}" cy="{by + bh + 62}" r="24" fill="#FFFFFF" stroke="{M}" stroke-width="3"/>'
             f'<path d="M{px + pw / 2 - 11} {by + bh + 62}l8 8l14 -15" fill="none" stroke="{M}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>']
        o += g
        dx = px + pw / 2 - (n - 1) * 9 + i * 18                       # 分页小圆点
        o.append(f'<circle cx="{sR(dx)}" cy="{sy + sh - 22}" r="4" fill="#D1D5DB">' + A("fill", ["#D1D5DB", M, "#D1D5DB"] if i else [M, "#D1D5DB", "#D1D5DB"], [0, i * S, (i + 1) * S] if i else [0, S, D_], True) + '</circle>')
    lx = px + pw + 40; lwid = SW - 40 - lx; rh = min(92, (ph - 12 * (n - 1)) / n); ly = py + (ph - (n * rh + (n - 1) * 12)) / 2
    for i, c in enumerate(sc):
        yy = ly + i * (rh + 12); on = [0, i * S, (i + 1) * S] if i else [0, S, D_]
        hi = (lambda a, b: A(a[0], [b, a[1], b] if i else [a[1], b, b], on, True))
        o.append(f'<rect x="{lx}" y="{sR(yy)}" width="{lwid}" height="{sR(rh)}" rx="16" fill="#FFFFFF" stroke="{T["tint"]}" stroke-width="2">' + hi(("fill", M), "#FFFFFF") + '</rect>'
                 f'<circle cx="{lx + 40}" cy="{sR(yy + rh / 2)}" r="18" fill="{T["tint"]}">' + hi(("fill", "#FFFFFF"), T["tint"]) + '</circle>'
                 f'<text x="{lx + 40}" y="{sR(yy + rh / 2 + 7)}" font-size="19" font-weight="800" fill="{M}" text-anchor="middle">{i + 1}</text>'
                 f'<text x="{lx + 74}" y="{sR(yy + rh / 2 + 8)}" font-size="23" font-weight="800" fill="{INK}">' + hi(("fill", "#FFFFFF"), INK) + esc(swrap(c[0], 23, lwid - 96)[0]) + '</text>')
    return s_frame(title, "".join(o), py + ph + 30, T)

SVG_KINDS = {"svg-table": svg_table, "svg-bars": svg_bars, "svg-steps": svg_steps, "svg-timeline": svg_timeline,
             "svg-breakdown": svg_breakdown, "svg-compare": svg_compare, "svg-concept": svg_concept, "svg-phone": svg_phone}



def svg_card(lang, title, body, T):
    """动画卡写错格式时不让整篇崩掉：退回成普通代码框，并在自查报告里提示"""
    title = title or {"svg-table": "一张表看懂", "svg-bars": "数据对比", "svg-steps": "照着做", "svg-timeline": "时间线", "svg-breakdown": "拆开看", "svg-compare": "对比", "svg-concept": "一张图看懂", "svg-phone": "演示"}[lang]
    try:
        return SVG_KINDS[lang](title, body, T)
    except Exception as e:
        warn(f"{lang}「{title}」的内容格式不对（{type(e).__name__}），没画成动画卡，先按普通代码框显示。对照写法表检查每行的 | 分隔")
        return terminal(body)

# ---------------- 飞书导出清理 + 自查 ----------------
ESC_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!>~=|])")
VIDEO_RE = re.compile(r"^\[([^\]]+\.(?:mp4|mov|m4v|webm|avi|gif))\]$", re.I)
TEMP_IMG = re.compile(r"authcode|feishu\.cn|larksuite\.com|larkoffice\.com|feishucdn|/space/api/box", re.I)
CJK = r"[⺀-鿿＀-￯　-〿]"

def clean_md(md):
    """去 BOM、统一换行；去掉飞书导出的转义反斜杠（代码块和行内代码里不动）"""
    md = md.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    out, fence = [], False
    for ln in md.split("\n"):
        if ln.strip().startswith("```"): fence = not fence; out.append(ln); continue
        if fence: out.append(ln); continue
        out.append("".join(seg if k % 2 else ESC_RE.sub(r"\1", seg) for k, seg in enumerate(re.split(r"(`[^`]*`)", ln))))
    return "\n".join(out)

def join_lines(parts):
    """段内换行合并：中文之间不加空格，英文之间加空格"""
    s = parts[0]
    for p in parts[1:]:
        s += ("" if re.search(CJK + r"$", s) or re.match(CJK, p) else " ") + p
    return s

def check(md, html_body, banner, stat):
    """生成后自动跑的文字自查，代替截图。返回问题列表"""
    issues = []
    imgs = re.findall(r'!\[[^\]]*\]\(<?([^)\s>]+)', md)
    stat["图片"] = len(imgs)
    temp = [u for u in imgs if TEMP_IMG.search(u)]
    local = [u for u in imgs if not u.startswith("http") and u not in temp]
    other = [u for u in imgs if u.startswith("http") and "mmbiz.qpic.cn" not in u and u not in temp]
    if temp: issues.append(f"{len(temp)} 张图是飞书临时链接，粘进公众号会丢，发布前换成公众号图库地址")
    if local: issues.append(f"{len(local)} 张图是本地路径或 base64，粘进公众号会丢：{local[0][:60]}…")
    if other: issues.append(f"{len(other)} 张图在外部图床，公众号会尝试转存，失败的要手动重传")
    if stat.get("视频占位"): issues.append(f"{stat['视频占位']} 处视频占位，需要在公众号里手动插视频或删掉")
    svgs = re.findall(r"<svg[\s\S]*?</svg>", html_body + (banner or ""))
    bad = [x for x in svgs if re.search(r'\s(id|class)="', x) or "<style" in x or "<script" in x or "Gradient" in x]
    if bad: issues.append(f"{len(bad)} 个 SVG 含 id/class/style/script/渐变，公众号会吞掉，需要修")
    if stat.get("动画卡", 0) > 3: issues.append(f"动画卡有 {stat['动画卡']} 张，超过 3 张会显得花，建议删到 3 张以内")
    return issues + WARN

# ---------------- parser ----------------
def front_matter(text):
    meta = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end > 0:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1); meta[k.strip().lower()] = v.strip().strip('"').strip("'")
            text = text[end+4:].lstrip("\n")
    return meta, text

LI_RE = re.compile(r"^(\s*)(?:([-*+])|(\d+)[.)、])\s+(.*)$")
CAP_END = "。！？!?：:；;，,、…"

def render(md, T, meta, stat=None):
    lines = md.split("\n"); i = 0; out = []; notes = []; h2n = 0
    stat = stat if stat is not None else {}
    pill = meta.get("h2", "part") == "pill" and T["st"] == "std"
    autocap = meta.get("caption", "auto").lower() not in ("off", "false", "no")
    para = []; st8 = {"media": False}
    def emit(h, media=False):
        out.append(h); st8["media"] = media
    def flush():
        if not para: return
        text = join_lines(para); n = len(para); para.clear()
        if text.startswith("^"):                      # 手动图注：^ 开头
            stat["图注"] = stat.get("图注", 0) + 1; emit(caption(inline(text[1:].strip(), T, notes), T)); return
        if (autocap and st8["media"] and n == 1 and len(text) <= 46 and text[-1] not in CAP_END
                and not re.search(r"\*\*|==|\+\+|^[「“\"]", text)):   # 自动图注：紧跟图片/视频的一行短句，结尾没有标点
            stat["图注"] = stat.get("图注", 0) + 1; emit(caption(inline(text, T, notes), T)); return
        emit(f'<p style="{p_css(T)}">{inline(text, T, notes)}</p>')
    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if not s: flush(); i += 1; continue
        m = re.match(r"^(```+|~~~+)\s*([\w][\w-]*)?\s*(.*)$", s)
        if m:
            flush(); fence = m.group(1)[:3]; lang = (m.group(2) or "").lower(); arg = m.group(3).strip(); body = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                body.append(lines[i]); i += 1
            if i >= len(lines): warn(f"有一个代码块没有结束的 ```（开头是「{(body[0] if body else '')[:20]}」），后面的内容全被当成了代码")
            i += 1
            while body and not body[-1].strip(): body.pop()
            while body and not body[0].strip(): body.pop(0)
            if lang in SVG_KINDS: stat["动画卡"] = stat.get("动画卡", 0) + 1; emit(svg_card(lang, arg, body, T))
            elif lang == "prompt": stat["滑动卡"] = stat.get("滑动卡", 0) + 1; emit(prompt_box(body, arg, T))
            elif lang == "promptbox":
                inner = "".join(f'<p style="margin:0;white-space:pre-wrap;word-break:break-all;font-size:13px;line-height:1.85;color:{PROMPT_INK};font-family:{MONO};">{esc(b) or " "}</p>' for b in body)
                stat["滑动卡"] = stat.get("滑动卡", 0) + 1; emit(dashed_box(arg or "滑动查看完整提示词", "list", inner, T))
            elif lang == "longimage":
                src = next((b.strip() for b in body if b.strip()), "")
                stat["滑动卡"] = stat.get("滑动卡", 0) + 1; emit(dashed_box(arg or "滑动查看长图", "image", f'<img src="{src}" style="display:block;width:100%;"/>', T, 420), True)
            else: emit(terminal(body))
            continue
        mh = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", s)
        if mh:
            flush(); lv = len(mh.group(1)); t = mh.group(2).strip()
            if lv == 1: meta.setdefault("title", t)
            elif lv == 2:
                h2n += 1; sub = ""
                if "|" in t: t, sub = [x.strip() for x in t.split("|", 1)]
                t = re.sub(r"^(?:[一二三四五六七八九十]+[、.．]|\d+[、.．]\s*|PART\s*\d+\s*[:：]?\s*)", "", t).strip() or t   # 原文自带的「一、」去掉，编号由版式加
                emit(h2_pill(h2n, inline(t, T, notes), T) if pill else h2_part(h2n, inline(t, T, notes), sub, T))
            elif lv == 3: emit(h3(inline(t, T, notes), T))
            else: emit(h4(inline(t, T, notes), T))
            i += 1; continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s): flush(); emit(hr(T)); i += 1; continue
        if s.startswith(">"):
            flush(); q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip()); i += 1
            kind = None
            mm = re.match(r"^\[!(\w+)\]\s*(.*)$", q[0]) if q else None
            if mm: kind = mm.group(1).upper(); q[0] = mm.group(2)
            paras = [join_lines(x.split("\n")) for x in "\n".join(q).split("\n\n") if x.strip()]
            body = "".join(f'<p style="margin:0 0 6px;">{inline(x, T, notes)}</p>' for x in paras)
            if kind == "QUOTE": emit(golden(inline(join_lines([x for x in q if x]) if any(q) else "", T, notes), T))
            elif kind: emit(callout(kind, body, T))
            else: emit(quote(body, T))
            continue
        mv = VIDEO_RE.match(s)
        if mv: flush(); stat["视频占位"] = stat.get("视频占位", 0) + 1; emit(video_slot(mv.group(1), T), True); i += 1; continue
        mi = re.match(r'^!\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+"([^"]*)")?\)$', s)
        if mi:
            flush()
            if (mi.group(3) or "").lower() == "long":
                stat["滑动卡"] = stat.get("滑动卡", 0) + 1
                emit(dashed_box(mi.group(1) if mi.group(1) and mi.group(1).lower() != "image" else "滑动查看长图", "image", f'<img src="{mi.group(2)}" style="display:block;width:100%;"/>', T, 420), True)
            else: emit(image(mi.group(2), mi.group(1), T), True)
            i += 1; continue
        ml = LI_RE.match(ln)
        if ml:
            flush(); items = []; base = len(ml.group(1).expandtabs(4)); ordered = ml.group(3) is not None
            while i < len(lines):
                x = LI_RE.match(lines[i])
                if x:
                    lv = min(2, max(0, (len(x.group(1).expandtabs(4)) - base) // 2))
                    if lv == 0 and (x.group(3) is not None) != ordered: break      # 换了列表类型，另起一个
                    items.append([lv, int(x.group(3)) if x.group(3) else None, x.group(4)]); i += 1; continue
                if lines[i].strip() and lines[i][:1] in " \t" and items:           # 缩进的续行并进上一条
                    items[-1][2] = join_lines([items[-1][2], lines[i].strip()]); i += 1; continue
                j = i
                while j < len(lines) and not lines[j].strip(): j += 1               # 飞书导出的列表每条之间有空行，跳过去接着算同一个列表
                if j > i and j < len(lines) and LI_RE.match(lines[j]) and (len(LI_RE.match(lines[j]).group(1)) > 0 or (LI_RE.match(lines[j]).group(3) is not None) == ordered):
                    i = j; continue
                break
            emit(list_block(items, T, notes)); continue
        if "|" in s and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$", lines[i+1].strip()) and "|" in lines[i+1]:
            flush(); rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                r = [c.strip() for c in re.sub(r"^\||\|$", "", lines[i].strip()).split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in r): rows.append(r)
                i += 1
            emit(table(rows, T, notes)); continue
        para.append(s); i += 1
    flush()
    if meta.get("outro", "true").lower() != "false": out.append(author_card(T, meta))
    out.append(notes_block(notes, T))
    wrap = "padding:26px 18px 30px;background:#0F1218;border-radius:18px;" if T["st"] == "dark" else "padding:0 4px;"
    return (f'<section style="font-family:-apple-system,BlinkMacSystemFont,\'PingFang SC\',\'Helvetica Neue\',sans-serif;{wrap}">'
            + "".join(out) + '</section>')

# ---------------- page ----------------
PAGE = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>__TITLE__ · 公众号排版</title>
<style>
body{margin:0;background:#EDEDED;font-family:'PingFang SC',sans-serif;color:#222}
.bar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #e5e5e5;padding:10px 20px;display:flex;gap:8px 10px;flex-wrap:wrap;align-items:center}
.bar b{font-size:15px;width:100%} .bar input[type=text]{width:340px;padding:8px 10px;border:1.5px solid #ccc;border-radius:8px;font-size:13px}
.bar label{font-size:13px;color:#555} .row{width:100%;display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center}
.sw{border:2px solid transparent;border-radius:20px;padding:4px 12px 4px 8px;font-size:13px;cursor:pointer;background:#f3f3f3;display:inline-flex;align-items:center;gap:6px}.sw i{width:12px;height:12px;border-radius:50%;display:inline-block}
.sw.st{padding:4px 14px}.sw.on{border-color:#222;background:#fff;font-weight:700}
button.go{border:0;background:#C9643E;color:#fff;padding:9px 16px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:700}
button.ghost{border:1.5px solid #C9643E;background:#fff;color:#C9643E;padding:8px 14px;border-radius:8px;font-size:13px;cursor:pointer}
#m{font-size:13px;width:100%} .ok{color:#2F9E5A} .err{color:#C9643E;font-weight:700}
.phone{max-width:640px;margin:24px auto 80px;background:#fff;border-radius:14px;box-shadow:0 6px 30px rgba(0,0,0,.08);padding:28px 22px}
.phone h1{font-size:22px;line-height:1.4;margin:0 0 18px;color:#111}
#manual{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;z-index:9}
#manual>div{background:#fff;border-radius:12px;padding:18px;width:min(720px,90vw)} #manual textarea{width:100%;height:220px;font-size:12px;box-sizing:border-box}
</style></head><body>
<div class="bar"><b>__TITLE__</b>
<div class="row"><label>风格</label><span id="sts" class="row" style="width:auto"></span></div>
<div class="row"><label>配色</label><span id="sws" class="row" style="width:auto"></span></div>
<label>头像 GIF</label><input type="text" id="gif" placeholder="https://mmbiz.qpic.cn/mmbiz_gif/…">
<label>本地预览</label><input type="file" id="local" accept="image/*">
<button class="go" onclick="copyAll(this)">复制全文到公众号</button>
<button class="ghost" onclick="copyPart(this,'banner')">只复制横幅</button>
<button class="ghost" onclick="copyPart(this,'body')">只复制正文</button>
<button class="ghost" onclick="copyMd(this)" title="纯正文，去掉了图片、视频、动画卡和占位，方便贴到朱雀做 AI 检测">复制 Markdown</button>
<div id="m"></div></div>
<div class="phone"><h1>__TITLE__</h1><div id="pv"></div></div>
<div id="manual"><div><b>浏览器没让我写剪贴板，请手动复制</b><p style="font-size:13px;color:#666">已全选，按 ⌘C / Ctrl+C。</p><textarea readonly></textarea><p style="text-align:right"><button class="ghost" onclick="document.getElementById('manual').style.display='none'">关闭</button></p></div></div>
<script>
const D=__DATA__;
const G=document.getElementById('gif'),L=document.getElementById('local');
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
G.value=ls('lq_banner_gif')||''; let local=ls('lq_banner_gif_local')||'';
let theme=D.fixed_theme?D.default_theme:(ls('lq_layout_theme')||D.default_theme); if(!D.palette[theme])theme=D.default_theme;
let style=D.fixed_style?D.default_style:(ls('lq_layout_style')||D.default_style); if(!D.styles[style])style=D.default_style;
function esc(u){return u.replace(/&/g,'&amp;').replace(/"/g,'&quot;')}
function paint(h){for(const k in D.tokens)h=h.split(D.tokens[k]).join(D.palette[theme][k]);return h}
function parts(u){const BN=(style=='neo'&&D.banner_neo)?D.banner_neo:D.banner;const b=BN?(BN[theme]||BN._):'';return {banner:b.split('GIF_URL_HERE').join(u),body:paint(D.styles[style]).split('GIF_URL_HERE').join(u)}}
function render(){const p=parts(esc(local||G.value.trim()||''));document.getElementById('pv').innerHTML=(p.banner?'<section style="margin:0 0 24px">'+p.banner+'</section>':'')+p.body;
  document.getElementById('sts').innerHTML=Object.keys(D.styles).map(k=>'<span class="sw st'+(k==style?' on':'')+'" title="'+D.style_desc[k]+'" onclick="pickS(\''+k+'\')">'+D.style_names[k]+'</span>').join('');
  document.getElementById('sws').innerHTML=Object.keys(D.palette).map(k=>'<span class="sw'+(k==theme?' on':'')+'" onclick="pick(\''+k+'\')"><i style="background:'+D.palette[k].main+'"></i>'+D.names[k]+'</span>').join('')}
function pick(k){theme=k;ls('lq_layout_theme',k);render()}
function pickS(k){style=k;ls('lq_layout_style',k);render()}
G.addEventListener('input',()=>{ls('lq_banner_gif',G.value.trim());render()});
L.addEventListener('change',()=>{const f=L.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{local=r.result;ls('lq_banner_gif_local',local);render()};r.readAsDataURL(f)});
render();
function msg(t,ok){const m=document.getElementById('m');m.textContent=t;m.className=ok?'ok':'err'}
function flash(b,t){const o=b.dataset.l||b.textContent;b.dataset.l=o;b.textContent=t;setTimeout(()=>b.textContent=o,1800)}
function need(){const u=G.value.trim();const raw=parts('GIF_URL_HERE');if((raw.banner+raw.body).indexOf('GIF_URL_HERE')<0)return parts('');
  if(!u){msg('先在顶部填头像 GIF 的公众号图片地址（横幅和文末作者卡都会用到）',false);G.focus();return null}
  if(!/^https:\/\/mmbiz\.qpic\.cn\//.test(u)){msg('头像地址要以 https://mmbiz.qpic.cn/ 开头（公众号图库里的图）',false);G.focus();return null}
  return parts(esc(u))}
function legacy(h,p){let d=false;const f=e=>{e.clipboardData.setData('text/html',h);e.clipboardData.setData('text/plain',p);e.preventDefault();d=true};
  document.addEventListener('copy',f);let ok=false;try{ok=document.execCommand('copy')}catch(e){}document.removeEventListener('copy',f);return ok&&d}
async function put(h){const t=h.replace(/<[^>]+>/g,'');if(legacy(h,t))return true;
  try{if(navigator.clipboard&&window.ClipboardItem){await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([h],{type:'text/html'}),'text/plain':new Blob([t],{type:'text/plain'})})]);return true}}catch(e){}return false}
function manual(p){const d=document.getElementById('manual');const t=d.querySelector('textarea');t.value=p;d.style.display='flex';t.focus();t.select()}
async function send(b,h,what){if(await put(h)){flash(b,'已复制 ✓');msg('已复制'+what+'（'+D.style_names[style]+' · '+D.names[theme]+'），去公众号编辑器正文里粘贴',true)}else{msg('这个窗口不允许写剪贴板：请用 Chrome 直接打开本文件',false);manual(h)}}
async function copyAll(b){const p=need();if(!p)return;send(b,(p.banner?'<section style="margin:0 0 24px">'+p.banner+'</section>':'')+p.body,'全文')}
async function copyMd(b){const t=D.md||'';let ok=false;
  try{await navigator.clipboard.writeText(t);ok=true}catch(e){}
  if(!ok){const f=e=>{e.clipboardData.setData('text/plain',t);e.preventDefault();ok=true};document.addEventListener('copy',f);try{document.execCommand('copy')}catch(e){}document.removeEventListener('copy',f)}
  if(ok){flash(b,'已复制 ✓');msg('已复制 Markdown（'+t.length+' 字），可以贴到朱雀做检测',true)}else{msg('浏览器没让写剪贴板，请手动复制',false);manual(t)}}
async function copyPart(b,k){const p=need();if(!p)return;if(!p[k]){msg('这篇没有横幅',false);return}send(b,p[k],k=='banner'?'横幅':'正文')}
</script></body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md"); ap.add_argument("--banner"); ap.add_argument("--out", default="out")
    ap.add_argument("--style", choices=list(STYLES)); ap.add_argument("--theme", choices=list(THEMES))
    a = ap.parse_args()
    meta, md = front_matter(clean_md(open(a.md, encoding="utf-8").read()))
    m = re.search(r"^#\s+(.+)$", md, re.M)
    title = meta.get("title") or (m.group(1).strip() if m else os.path.splitext(os.path.basename(a.md))[0])
    slug = meta.get("slug") or re.sub(r"[^\w一-鿿-]+", "-", title)[:30].strip("-") or "article"
    style = a.style or meta.get("style", "std"); theme = a.theme or meta.get("theme", "orange")
    if style not in STYLES: warn(f"没有「{style}」这个风格，用了标准。可选：{'、'.join(STYLES)}"); style = "std"
    if theme not in THEMES: warn(f"没有「{theme}」这个配色，用了品牌橙。可选：{'、'.join(THEMES)}"); theme = "orange"
    stat = {}; styles = {}
    for k in [style] + [x for x in STYLES if x != style]:       # 默认风格先渲染，统计和提示只记这一遍
        n = len(WARN); styles[k] = fix_empty(render(md, dict(TOK, st=k, r=STYLES[k]["r"]), dict(meta), stat if k == style else {}))
        if k == "dark": styles[k] = dark_fix(styles[k])
        if k != style: del WARN[n:]
    styles = {k: styles[k] for k in STYLES}
    banner = None; banner_neo = None
    if a.banner:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import banner as B
        spec = json.load(open(a.banner, encoding="utf-8"))
        key = "card" if spec.get("style") == "card" else "poster"
        if spec.get("style") in ("card", "poster", "neo") and spec.get(key, {}).get("theme", "all") == "all":
            for k, T in THEMES.items():   # 标题卡 / 大字海报 / 潮酷横幅跟着配色换色
                B.THEMES[k] = dict(main=T["main"], light=T["tint"], line=T["line"], border=T["tint"], bg=T["soft"])
            def per_theme(st):
                r = {}
                for k in THEMES:
                    sp = json.loads(json.dumps(spec)); sp["style"] = st; sp[key]["theme"] = k; r[k] = B.build(sp)
                return r
            banner = per_theme(spec["style"])
            if spec["style"] == "poster": banner_neo = per_theme("neo")     # 正文切到潮酷风格时，横幅自动换成潮酷版
        else:
            banner = {"_": B.build(spec)}
        for x in B.check_spec(spec, list(banner.values())): warn("横幅：" + x)
    data = {"styles": styles, "style_names": {k: v["name"] for k, v in STYLES.items()}, "style_desc": {k: v["desc"] for k, v in STYLES.items()},
            "palette": {k: {c: v[c] for c in TOK} for k, v in THEMES.items()}, "names": {k: v["name"] for k, v in THEMES.items()}, "tokens": TOK,
            "banner": banner, "banner_neo": banner_neo, "default_theme": theme, "default_style": style,
            "fixed_theme": bool(a.theme or meta.get("theme")), "fixed_style": bool(a.style or meta.get("style")), "md": plain_md(md)}
    os.makedirs(a.out, exist_ok=True)
    page = PAGE.replace("__TITLE__", esc(title)).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    path = os.path.join(a.out, f"{slug}-公众号排版.html")
    open(path, "w", encoding="utf-8").write(page)
    issues = check(md, styles[style], "".join((banner or {}).values()), stat)
    print(f"ok  {path}  （{os.path.getsize(path) // 1024} KB，默认：{STYLES[style]['name']} · {THEMES[theme]['name']}）")
    order = ["图片", "图注", "视频占位", "动画卡", "滑动卡"]
    print("统计：" + "，".join(f"{k} {stat.get(k, 0)}" for k in order))
    if issues:
        print("发布前要处理：")
        for x in issues: print("  - " + x)
    else:
        print("自查通过：没有发现会在公众号里出问题的地方")

if __name__ == "__main__":
    main()
