#!/usr/bin/env python3
"""林月半子 · 公众号开头横幅生成器
用法: python3 banner.py spec.json [输出目录]
产出: <slug>.svg（含 GIF_URL_HERE 占位）和 <slug>-复制到公众号.html
"""
import json, sys, os, re, random, html as H

D = 7.0                     # 一轮时长（秒）
W, HH = 1246, 220
OR, GR, INK, BODY, MUT = "#C9643E", "#2F9E5A", "#1F1F1F", "#333333", "#9A9A9A"
EASE = "0.23 1 0.32 1"
SLOGAN = json.loads(r"""[["我",16,"04400e50784808480840fffe084008440a440c48183068220852088a2b061002"],["是",16,"1ff0101010101ff0101010101ff00000fffe0100110011f811002900450083fe"],["林",16,"1020102010201020fdfe10203070387054a850a8912412221420102010201020"],["月",16,"07fc040404040404040407fc04040404040407fc040404040804080410142008"],["半",16,"0100210811080910092001003ff8010001000100fffe01000100010001000100"],["子",16,"00007ff800100020004001800100fffe01000100010001000100010005000200"],["，",16,"00000000000000000000000000000000000000000c000c000400040008000000"],["教",16,"082008207ea0093e0a44ff4408447ea4242848288f1078100828084828841102"],["你",16,"08800880088011fe110232043420502091281124122412221422102010a01040"],["用",16,"00003ff82108210821083ff82108210821083ff8210821082108410841288010"],["A",8,"0000000018242442427e424242420000"],["I",8,"000000003e08080808080808083e0000"],["干",16,"00003ff801000100010001000100fffe01000100010001000100010001000100"],["掉",16,"10201020103e1020fdfc110415fc190431fcd124102013fe1020102050202020"],["9",8,"000000003c4242423e02020204380000"],["0",8,"00000000182442464a52624224180000"],["%",8,"00000000314a4a340808162929460000"],["的",16,"1040104020407e7c42844284430442447e2442244204420442047e0442280010"],["重",16,"001000f83f000100fffe01001ff011101ff011101ff001003ff80100fffe0000"],["复",16,"100010001ffc20005ff090101ff010101ff004000ff01820644003801c70e00e"],["劳",16,"08200820fffe082000007ffe420282043ff00210021004100410081010a02040"],["动",16,"004000407c40004001fc0044fe4420442044208448844484fd04450402280410"]]""")   # 固定口号点阵（Unifont 16px）：我是林月半子，教你用AI干掉90%的重复劳动
SLOGAN_COLORS = [MUT]*7 + [BODY]*7 + [OR]*8   # 我是林月半子， / 教你用AI干掉 / 90%的重复劳动

k = lambda t: round(min(max(t / D, 0), 1), 4)
R = lambda v: f"{v:.1f}".rstrip('0').rstrip('.')
esc = lambda s: H.escape(str(s), quote=True)

def A(attr, vals, ts, spline=None, typ=None):
    kt = ";".join(str(k(t)) for t in ts); vs = ";".join(str(v) for v in vals); ex = ""
    if spline:
        sp = spline if isinstance(spline, list) else [spline] * (len(ts) - 1)
        ex = f' calcMode="spline" keySplines="{";".join(sp)}"'
    if typ:
        return f'<animateTransform attributeName="transform" type="{typ}" values="{vs}" keyTimes="{kt}"{ex} dur="{D}s" repeatCount="indefinite"/>'
    return f'<animate attributeName="{attr}" values="{vs}" keyTimes="{kt}"{ex} dur="{D}s" repeatCount="indefinite"/>'

def show(t, f=0.15):
    return A("opacity", [0, 0, 1, 1], [0, t, t + f, D])

def pop(cx, cy, t, inner, amp=1.12):
    return (f'<g transform="translate({R(cx)} {R(cy)})"><g>{A(None,[".5",".5",amp,1,1],[0,t,t+0.12,t+0.22,D],EASE,"scale")}'
            f'<g transform="translate({R(-cx)} {R(-cy)})">{inner}</g></g></g>')

def grow(attr, a, b, t, d=0.3, spline="0.42 0 0.58 1"):
    return A(attr, [a, a, b, b], [0, t, t + d, D], ["0 0 1 1", spline, "0 0 1 1"])

def tw(s, size):   # 估算文字宽度
    return sum(size if ord(c) > 255 else size * 0.58 for c in s)

# ---------------- fixed part: avatar + slogan ----------------
def head():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HH}" width="100%" style="display:block;width:100%;height:auto;max-width:{W}px;margin:0 auto;background:transparent;font-family:\'PingFang SC\',sans-serif">',
         '<image x="4" y="18" width="216" height="190" preserveAspectRatio="xMidYMax meet" href="GIF_URL_HERE"/>']
    random.seed(3); ps, tx, ty, dot = 3.0, 236, 86, 2.5; x = tx
    for i, (ch, w, hexrows) in enumerate(SLOGAN):
        n = w // 4; runs = []
        for y in range(16):
            v = int(hexrows[y*n:(y+1)*n], 16); bits = [(v >> (w-1-b)) & 1 for b in range(w)]; b = 0
            while b < w:
                if bits[b]:
                    e = b
                    while e < w and bits[e]: e += 1
                    runs.append(f"M{R(x+b*ps)} {R(ty+y*ps+dot/2)}h{R((e-b)*ps)}"); b = e
                else: b += 1
        cw = w * ps
        if runs:
            ta, td = 0.1 + i*0.045, 1.9 + i*0.025
            dx, dy = random.uniform(-26, 26), random.uniform(-38, 38); mx, my = x + cw/2, ty + 24
            p = f'<path d="{"".join(runs)}" fill="none" stroke="{SLOGAN_COLORS[i]}" stroke-width="{dot}" stroke-dasharray="{dot} {R(ps-dot)}"/>'
            o.append(f'<g opacity="0">{A("opacity",[0,0,1,1,0,0],[0,ta,ta+0.12,td,td+0.35,D])}'
                     f'<g>{A(None,["0 0","0 0",f"{R(dx)} {R(dy)}",f"{R(dx)} {R(dy)}"],[0,td,td+0.4,D],EASE,"translate")}'
                     f'<g transform="translate({R(mx)} {R(my)})"><g>{A(None,[".6",".6","1.08",1,1,".25",".25"],[0,ta,ta+0.1,ta+0.18,td,td+0.4,D],EASE,"scale")}'
                     f'<g transform="translate({R(-mx)} {R(-my)})">{p}</g></g></g></g></g>')
        x += cw
    return o


# ================= v2: illustrated scenes =================
import math
TEAL, TEAL_L, NAVY, GOLD, BLUE, LINE, SHADOW = "#12A37F", "#D5F2E8", "#2B3A55", "#F2B33D", "#5B7FB8", "#D9DEE5", "#E7EAEF"
T0, T_END = 2.4, 6.0          # scene window

def bounce(cx, cy, t, inner, big=1.15):
    """从 0 蹦出来：0 → big → 0.95 → 1"""
    return (f'<g opacity="0">{show(t,0.05)}<g transform="translate({R(cx)} {R(cy)})"><g>'
            f'{A(None,[0,0,big,0.95,1,1],[0,t,t+0.16,t+0.26,t+0.34,D],["0 0 1 1","0.3 0 0.6 1","0.4 0 0.6 1","0.4 0 0.6 1","0 0 1 1"],"scale")}'
            f'<g transform="translate({R(-cx)} {R(-cy)})">{inner}</g></g></g></g>')

def check_badge(cx, cy, t, r=10):
    return bounce(cx, cy, t, f'<circle cx="{R(cx)}" cy="{R(cy)}" r="{r}" fill="{TEAL}" stroke="#FFFFFF" stroke-width="2.5"/>'
                  f'<path d="M{R(cx-r*0.45)} {R(cy)}l{R(r*0.32)} {R(r*0.32)}l{R(r*0.55)} {R(-r*0.6)}" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>', 1.3)

def label(x, y, s, t, anchor="middle", size=13, col=None):
    if not s: return ""
    return f'<g opacity="0">{show(t,0.2)}<text x="{R(x)}" y="{R(y)}" font-size="{size}" fill="{col or MUT}" text-anchor="{anchor}">{esc(s)}</text></g>'

# ---------- icons (drawn around 0,0, ~28px) ----------
def _icon(name, bg="#FFFFFF"):
    I = {
     "sun": f'<circle r="7" fill="{GOLD}"/>' + "".join(f'<line x1="{R(10*math.cos(a))}" y1="{R(10*math.sin(a))}" x2="{R(14*math.cos(a))}" y2="{R(14*math.sin(a))}" stroke="{GOLD}" stroke-width="2.5" stroke-linecap="round"/>' for a in [i*math.pi/4 for i in range(8)]),
     "moon": f'<circle r="11" fill="#E8C766"/><circle cx="5" cy="-4" r="9.5" fill="{bg}"/>',
     "paw": f'<ellipse cy="5" rx="7" ry="6" fill="{TEAL}"/><circle cx="-8" cy="-3" r="3" fill="{TEAL}"/><circle cx="-3" cy="-9" r="3" fill="{TEAL}"/><circle cx="3" cy="-9" r="3" fill="{TEAL}"/><circle cx="8" cy="-3" r="3" fill="{TEAL}"/>',
     "pin": f'<path d="M0 13C-7 4-10-1-10-4A10 10 0 1 1 10-4C10-1 7 4 0 13Z" fill="{TEAL}"/><circle cy="-4" r="4" fill="{bg}"/>',
     "pill": f'<g transform="rotate(-35)"><rect x="-13" y="-6" width="26" height="12" rx="6" fill="#FFFFFF" stroke="#C9CED6" stroke-width="1.5"/><path d="M0 -6H-7A6 6 0 0 0 -7 6H0Z" fill="{OR}"/></g>',
     "bell": f'<path d="M-9 6V-1A9 9 0 0 1 9-1V6L11 9H-11Z" fill="{GOLD}"/><circle cy="12" r="2.6" fill="{GOLD}"/>',
     "wallet": f'<rect x="-13" y="-9" width="26" height="18" rx="3" fill="{BLUE}"/><rect x="-13" y="-4" width="26" height="4" fill="{NAVY}"/><rect x="4" y="3" width="6" height="3" rx="1" fill="#FFFFFF"/>',
     "calendar": f'<rect x="-11" y="-10" width="22" height="21" rx="3" fill="#FFFFFF" stroke="{NAVY}" stroke-width="2"/><rect x="-11" y="-10" width="22" height="6" rx="2" fill="{OR}"/>' + "".join(f'<rect x="{-7+c*5}" y="{0+r*5}" width="3" height="3" fill="{NAVY}"/>' for r in range(2) for c in range(3)),
     "train": f'<rect x="-10" y="-13" width="20" height="21" rx="5" fill="{BLUE}"/><rect x="-7" y="-9" width="14" height="6" rx="1.5" fill="#FFFFFF"/><circle cx="-5" cy="4" r="1.6" fill="{GOLD}"/><circle cx="5" cy="4" r="1.6" fill="{GOLD}"/><path d="M-7 9L-10 13M7 9L10 13" stroke="{NAVY}" stroke-width="2" stroke-linecap="round"/>',
     "doc": f'<rect x="-10" y="-13" width="20" height="26" rx="2.5" fill="#FFFFFF" stroke="#9AA3AF" stroke-width="1.5"/><rect x="-6" y="-7" width="12" height="2.5" rx="1" fill="{TEAL}"/><rect x="-6" y="-1" width="12" height="2.5" rx="1" fill="#C9CED6"/><rect x="-6" y="5" width="8" height="2.5" rx="1" fill="#C9CED6"/>',
     "scissors": f'<circle cx="-5" cy="8" r="4" fill="none" stroke="{OR}" stroke-width="2.5"/><circle cx="5" cy="8" r="4" fill="none" stroke="{OR}" stroke-width="2.5"/><path d="M-3 5L6-12M3 5L-6-12" stroke="{NAVY}" stroke-width="2.5" stroke-linecap="round"/>',
     "music": f'<rect x="3" y="-12" width="2.6" height="18" fill="{TEAL}"/><path d="M5.6-12C10-10 11-6 9-3C9-6 7-8 5.6-8Z" fill="{TEAL}"/><ellipse cx="0" cy="7" rx="5" ry="4" fill="{TEAL}"/>',
     "text": f'<rect x="-10" y="-11" width="20" height="4.5" rx="1" fill="{NAVY}"/><rect x="-2.3" y="-11" width="4.6" height="22" rx="1" fill="{NAVY}"/>',
     "play": f'<rect x="-13" y="-10" width="26" height="20" rx="5" fill="{OR}"/><path d="M-3-5L5 0L-3 5Z" fill="#FFFFFF"/>',
     "chart": f'<rect x="-11" y="2" width="5" height="9" rx="1" fill="{TEAL}"/><rect x="-3" y="-4" width="5" height="15" rx="1" fill="{TEAL}"/><rect x="5" y="-11" width="5" height="22" rx="1" fill="{OR}"/>',
     "person": f'<path d="M-11 13Q-11 2 0 2Q11 2 11 13Z" fill="{NAVY}"/><circle cy="-5" r="6.5" fill="#F2B98A"/><path d="M-6.5-6Q-6-13 0-12Q6-13 6.5-6L4-9L0-7L-4-9Z" fill="{INK}"/>',
     "photo": f'<rect x="-13" y="-10" width="26" height="20" rx="3" fill="#DDE7F3"/><path d="M-13 10L-4-1L3 6L7 2L13 8V10Z" fill="{TEAL}"/><circle cx="6" cy="-4" r="3" fill="{GOLD}"/>',
     "cup": f'<path d="M-8-7H8L6 12H-6Z" fill="#EDE3D2" stroke="{NAVY}" stroke-width="1.5"/><rect x="-10" y="-11" width="20" height="4" rx="2" fill="{NAVY}"/><rect x="-7.2" y="0" width="14.4" height="5" fill="{BLUE}"/>',
     "chat": f'<path d="M-12-10H12A3 3 0 0 1 15-7V4A3 3 0 0 1 12 7H-2L-8 12V7H-12A3 3 0 0 1-15 4V-7A3 3 0 0 1-12-10Z" fill="{TEAL}"/><circle cx="-6" cy="-1.5" r="1.8" fill="#FFFFFF"/><circle cy="-1.5" r="1.8" fill="#FFFFFF"/><circle cx="6" cy="-1.5" r="1.8" fill="#FFFFFF"/>',
     "mic": f'<rect x="-4.5" y="-13" width="9" height="16" rx="4.5" fill="{NAVY}"/><path d="M-8-1A8 8 0 0 0 8-1M0 7V12M-5 12H5" fill="none" stroke="{NAVY}" stroke-width="2.2" stroke-linecap="round"/>',
     "mail": f'<rect x="-13" y="-9" width="26" height="18" rx="2.5" fill="#FFFFFF" stroke="{NAVY}" stroke-width="2"/><path d="M-12-7L0 2L12-7" fill="none" stroke="{OR}" stroke-width="2"/>',
     "spark": f'<path d="M0-14Q2-2 14 0Q2 2 0 14Q-2 2-14 0Q-2-2 0-14Z" fill="{GOLD}"/>',
     "code": f'<path d="M-6-8L-13 0L-6 8M6-8L13 0L6 8M3-11L-3 11" fill="none" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
     "image": None,
    }
    I["image"] = I["photo"]
    return I.get(name) or I["spark"]

def icon(name, cx, cy, s=1.0, bg="#FFFFFF"):
    return f'<g transform="translate({R(cx)} {R(cy)}) scale({s})">{_icon(name,bg)}</g>'

# ---------- props (big objects) ----------
def prop_chat(x, cy, t):
    w, h = 150, 116; y = cy - h/2
    o = [bounce(x+w/2, cy, t, f'<rect x="{x}" y="{R(y+6)}" width="{w}" height="{h}" rx="14" fill="{SHADOW}"/>'
         f'<rect x="{x}" y="{R(y)}" width="{w}" height="{h}" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
         + "".join(f'<circle cx="{x+16+i*11}" cy="{R(y+16)}" r="3.2" fill="#C9CED6"/>' for i in range(3)))]
    rows = [(x+16, 70, "#D5D9E0"), (x+w-16-62, 62, TEAL), (x+16, 52, "#D5D9E0"), (x+w-16-70, 70, TEAL)]
    for i, (bx, bw, col) in enumerate(rows):
        by = y + 32 + i*20
        o.append(bounce(bx+bw/2, by+6, t+0.3+i*0.18, f'<rect x="{R(bx)}" y="{R(by)}" width="{bw}" height="12" rx="6" fill="{col}"/>'))
    return o, (x+w, cy), w

def prop_clapper(x, cy, t, work):
    w, h = 120, 92; y = cy - h/2 + 10
    stripes = "".join(f'<path d="M{x+6+i*22} {R(y-22)}L{x+20+i*22} {R(y-22)}L{x+12+i*22} {R(y-6)}L{x-2+i*22} {R(y-6)}Z" fill="#FFFFFF"/>' for i in range(5))
    arm = (f'<g><rect x="{x}" y="{R(y-24)}" width="{w}" height="20" rx="4" fill="{INK}"/>{stripes}'
           f'{A(None,[f"0 {x} {R(y-4)}",f"0 {x} {R(y-4)}",f"-14 {x} {R(y-4)}",f"0 {x} {R(y-4)}",f"-14 {x} {R(y-4)}",f"0 {x} {R(y-4)}",f"0 {x} {R(y-4)}"],[0,work,work+0.12,work+0.24,work+0.36,work+0.48,D],None,"rotate")}</g>')
    body = (f'<rect x="{x}" y="{R(y+4)}" width="{w}" height="{h-8}" rx="8" fill="{SHADOW}"/>'
            f'<rect x="{x}" y="{R(y-2)}" width="{w}" height="{h-8}" rx="8" fill="#3B4252"/>'
            f'<circle cx="{x+w/2}" cy="{R(y+h/2-6)}" r="16" fill="{TEAL}"/><path d="M{x+w/2-5} {R(y+h/2-14)}L{x+w/2+8} {R(y+h/2-6)}L{x+w/2-5} {R(y+h/2+2)}Z" fill="#FFFFFF"/>'
            f'<rect x="{x+12}" y="{R(y+8)}" width="18" height="4" rx="2" fill="#7B8496"/><rect x="{x+w-38}" y="{R(y+h-24)}" width="26" height="4" rx="2" fill="#7B8496"/>')
    return [bounce(x+w/2, cy, t, body+arm)], (x, cy), (x+w, cy), w

def prop_robot(x, cy, t, work):
    w = 150; hx, hy = x+20, cy-78
    eyes = (f'<g><path d="M{hx+38} {hy+42}l9 -9l9 9l-9 9Z" fill="#5BD6A8"/><path d="M{hx+72} {hy+42}l9 -9l9 9l-9 9Z" fill="#5BD6A8"/>'
            f'{A(None,[f"1 1",f"1 1",f"1 0.1",f"1 1",f"1 1",f"1 0.1",f"1 1",f"1 1"],[0,t+0.6,t+0.66,t+0.72,work+0.9,work+0.96,work+1.02,D],None,"scale")}</g>')
    body = (f'<ellipse cx="{x+w/2}" cy="{cy+78}" rx="56" ry="7" fill="{SHADOW}"/>'
            f'<path d="M{hx} {hy+6}L{hx+110} {hy}L{hx+118} {hy+70}L{hx+6} {hy+76}Z" fill="#E9EAE6"/><path d="M{hx+110} {hy}L{hx+120} {hy+6}L{hx+126} {hy+74}L{hx+118} {hy+70}Z" fill="#C9CBC4"/>'
            f'<rect x="{hx+20}" y="{hy+18}" width="80" height="46" rx="5" fill="#1C2026"/>'
            f'<rect x="{hx+28}" y="{hy+26}" width="18" height="3" rx="1.5" fill="#5BD6A8" opacity=".7"/>'
            f'<path d="M{hx+14} {hy+80}H{hx+104}L{hx+100} {hy+132}H{hx+20}Z" fill="#E9EAE6"/>'
            f'<g><path d="M{hx+34} {hy+92}L{hx+122} {hy+84}L{hx+130} {hy+126}L{hx+40} {hy+134}Z" fill="#2E4A3E"/>'
            f'<path d="M{hx+20} {hy+122}L{hx+110} {hy+116}L{hx+130} {hy+126}L{hx+40} {hy+134}Z" fill="#3E6252"/>'
            f'<rect x="{hx+70}" y="{hy+100}" width="12" height="10" rx="2" fill="{GOLD}"/></g>')
    mark = bounce(hx+64, hy-14, work+1.0, f'<rect x="{hx+48}" y="{hy-26}" width="32" height="22" rx="4" fill="{TEAL_L}"/><path d="M{hx+56} {hy-15}l5 5l9 -9" fill="none" stroke="{TEAL}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    return [bounce(x+w/2, cy, t, body + eyes), mark], (x, cy), (x+w, cy), w

def prop_computer(x, cy, t, work):
    w = 250; mx, my = x, cy-62
    keys = "".join(f'<rect x="{mx+176+c*9}" y="{my+104+r*7}" width="7" height="5" rx="1" fill="#FFFFFF" stroke="#CFC4AE" stroke-width=".6"/>' for r in range(3) for c in range(7))
    scr = (mx+14, my+12, 132, 82)
    body = (f'<rect x="{mx+18}" y="{my+130}" width="120" height="8" rx="4" fill="#E3D9C4"/>'
            f'<path d="M{mx+150} {my+90}Q{mx+190} {my+92} {mx+200} {my+100}" fill="none" stroke="#B9AE97" stroke-width="1.5"/>'
            f'<rect x="{mx}" y="{my}" width="160" height="126" rx="14" fill="#EFE6D2" stroke="#CFC4AE" stroke-width="2"/>'
            f'<rect x="{scr[0]}" y="{scr[1]}" width="{scr[2]}" height="{scr[3]}" rx="8" fill="#1F242C"/>'
            f'<path d="M{mx+40} {my+86}L{mx+62} {my+20}H{mx+78}L{mx+56} {my+86}Z" fill="#FFFFFF" opacity=".06"/>'
            f'<rect x="{mx+108}" y="{my+108}" width="36" height="4" rx="2" fill="#B9AE97"/><circle cx="{mx+20}" cy="{my+110}" r="2.5" fill="#B9AE97"/>'
            f'<rect x="{mx+170}" y="{my+100}" width="74" height="28" rx="4" fill="#E3D9C4" stroke="#CFC4AE"/>{keys}')
    glow = (f'<rect x="{scr[0]}" y="{scr[1]}" width="{scr[2]}" height="{scr[3]}" rx="8" fill="#2B3A55" opacity="0">'
            f'{A("opacity",[0,0,1,0.85,1,1],[0,work,work+0.08,work+0.14,work+0.2,D])}</rect>')
    return [bounce(x+80, cy, t, body + glow)], (x, cy), (x+w, cy), w, scr

def prop_phone(x, cy, t, work):
    w, h = 92, 176; y = cy - h/2
    scr = (x+7, y+10, 78, 156)
    body = (f'<rect x="{x}" y="{R(y)}" width="{w}" height="{h}" rx="16" fill="{INK}"/>'
            f'<rect x="{scr[0]}" y="{R(scr[1])}" width="{scr[2]}" height="{scr[3]}" rx="10" fill="#2B3A55"/>')
    return [bounce(x+w/2, cy, t, body)], (x, cy), (x+w, cy), w, scr

def prop_start(x, cy, t, ic):
    r = 34
    return [bounce(x+r, cy, t, f'<circle cx="{x+r}" cy="{cy+4}" r="{r}" fill="{SHADOW}"/><circle cx="{x+r}" cy="{cy}" r="{r}" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>' + icon(ic, x+r, cy, 1.5))], (x+2*r, cy), 2*r

PROPS = {"robot": prop_robot, "clapper": prop_clapper, "computer": prop_computer, "phone": prop_phone}

# ---------- tiles ----------
def tile_card(x, cy, t, it, w=110):
    h = 108; y = cy - h/2
    inner = (f'<rect x="{x}" y="{R(y+5)}" width="{w}" height="{h}" rx="10" fill="{SHADOW}"/>'
             f'<rect x="{x}" y="{R(y)}" width="{w}" height="{h}" rx="10" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
             + "".join(f'<circle cx="{x+12+i*8}" cy="{R(y+12)}" r="2.4" fill="#C9CED6"/>' for i in range(3))
             + f'<rect x="{x+12}" y="{R(y+24)}" width="{w-24}" height="7" rx="3.5" fill="{TEAL}"/>'
             + icon(it.get("icon","doc"), x+30, y+56, 0.95)
             + f'<rect x="{x+50}" y="{R(y+48)}" width="{w-64}" height="5" rx="2.5" fill="#1F7A5C"/><rect x="{x+50}" y="{R(y+60)}" width="{w-76}" height="5" rx="2.5" fill="#6CCDAA"/>'
             + f'<rect x="{x+12}" y="{R(y+86)}" width="{w-24}" height="7" rx="3.5" fill="{TEAL}"/>')
    return bounce(x+w/2, cy, t, inner), (x+w-6, y+4), (x+w/2, y+h+18)

def tile_film(x, cy, t, it, w=160):
    h = 104; y = cy - h/2
    holes = "".join(f'<rect x="{R(x+10+i*(w-20)/7)}" y="{R(y+5)}" width="9" height="5" rx="1" fill="#FFFFFF"/><rect x="{R(x+10+i*(w-20)/7)}" y="{R(y+h-10)}" width="9" height="5" rx="1" fill="#FFFFFF"/>' for i in range(8))
    sbg = it.get("bg") or ["#F5E9D3", "#DDE7F3", "#E3F1EA", "#F6E1D6"][it.get("_i", 0) % 4]
    inner = (f'<rect x="{x}" y="{R(y)}" width="{w}" height="{h}" rx="6" fill="#3B4252"/>{holes}'
             f'<rect x="{x+8}" y="{R(y+15)}" width="{w-16}" height="{h-30}" rx="3" fill="{sbg}"/>'
             + icon(it.get("icon","play"), x+w/2, cy, 1.5, sbg))
    return bounce(x+w/2, cy, t, inner), (x+w-6, y+4), (x+w/2, y+h+18)

TILES = {"card": (tile_card, 110), "film": (tile_film, 156)}

def connector(x1, x2, y, t, d=0.25):
    return (f'<g opacity="0">{show(t,0.05)}<circle cx="{R(x1)}" cy="{y}" r="4" fill="#8E97A6"/>'
            f'<line x1="{R(x1)}" y1="{y}" x2="{R(x1)}" y2="{y}" stroke="#8E97A6" stroke-width="2.5">{grow("x2",R(x1),R(x2),t,d)}</line>'
            f'<g opacity="0">{show(t+d,0.05)}<circle cx="{R(x2)}" cy="{y}" r="4" fill="#8E97A6"/></g></g>')

# ---------- layouts ----------
def lay_pipeline(sc):
    o = []; x = 250; cy = 112; t = T0
    if sc.get("source"):
        s = sc["source"]
        if s.get("prop", "chat") == "chat":
            parts, out, w = prop_chat(x, cy, t); o += parts; t += 0.9
        else:
            parts, out, w = prop_start(x, cy, t, s.get("icon", "chat")); o += parts; t += 0.4
        o.append(label(x+w/2, cy+84, s.get("label"), t-0.3))
        o.append(connector(out[0]+8, out[0]+44, cy, t)); x = out[0]+52; t += 0.3
    p = sc.get("processor", {"prop": "robot"})
    res = PROPS[p["prop"]](x, cy, t, t+0.35)
    parts, pin, pout, w = res[0], res[1], res[2], res[3]; o += parts
    o.append(label(x+w/2, cy+92, p.get("label"), t+0.3)); t += 0.75
    tf, tw0 = TILES[sc.get("tile", "card")]
    items = sc["items"]; avail = 1236 - (pout[0] + 52)
    gap = 10; tw_ = min(tw0, (avail - gap*(len(items)-1)) / len(items))
    o.append(connector(pout[0]+8, pout[0]+44, cy, t)); t += 0.3
    x = pout[0] + 52
    step = min(0.24, (T_END - 0.6 - t) / max(len(items), 1))
    for i, it in enumerate(items):
        it = dict(it, _i=i); ti = t + i*step
        tile, badge, lab = tf(x, cy, ti, it, tw_)
        o.append(tile); o.append(check_badge(badge[0], badge[1], ti + 0.3 + step*0.5) if it.get("check", True) else "")
        o.append(label(lab[0], lab[1], it.get("label"), ti+0.2)); x += tw_ + gap
    return o

def lay_fly(sc):
    o = []; cy = 108
    dev = sc.get("device", "computer"); dw = 250 if dev == "computer" else 92
    items = sc.get("items", [])[:4]
    dx = 560 if items else 1236 - dw - 20
    t_arr = T0 + 1.3
    res = PROPS[dev](dx, cy, T0 + 0.1, t_arr)
    o += res[0]; scr = res[4]
    o.append(label(dx + (80 if dev == "computer" else 46), cy+96, sc.get("device_label"), t_arr+0.2))
    sx, ex = 300, scr[0] + 26
    trail = lambda wd, col: (f'<line x1="{sx}" y1="{cy}" x2="{sx}" y2="{cy}" stroke="{col}" stroke-width="{wd}" stroke-linecap="round">'
                             f'{grow("x2",sx,ex-34,T0+0.4,t_arr-T0-0.4,"0.5 0 0.9 0.6")}</line>')
    o.append(f'<g opacity="0">{A("opacity",[0,0,1,1,0.45,0.45],[0,T0+0.3,T0+0.4,t_arr,t_arr+0.3,D])}{trail(12,TEAL_L)}{trail(3,TEAL)}</g>')
    o.append(f'<g opacity="0">{A("opacity",[0,0,1,1,0,0],[0,T0+0.3,T0+0.4,t_arr,t_arr+0.12,D])}<g>'
             f'{A(None,[f"{sx} {cy}",f"{sx} {cy}",f"{ex} {cy}",f"{ex} {cy}"],[0,T0+0.4,t_arr,D],["0 0 1 1","0.5 0 0.9 0.6","0 0 1 1"],"translate")}'
             f'<g>{A(None,[-10,-10,8,-6,0,0],[0,T0+0.4,T0+0.7,T0+1.0,t_arr,D],None,"rotate")}'
             f'<rect x="-24" y="-24" width="48" height="48" rx="12" fill="{TEAL}" stroke="#FFFFFF" stroke-width="3" transform="rotate(-12)"/>'
             + f'<circle r="15" fill="#FFFFFF"/>' + icon(sc.get("flyer", "doc"), 0, 0, 0.8) + '</g></g></g>')
    o.append(label(sx-6, cy+40, sc.get("left_label"), T0+0.4, "start"))
    scr_icons = sc.get("screen", [])[:3]
    for i, ic in enumerate(scr_icons):
        n = len(scr_icons); cxs = scr[0] + scr[2]*(i+1)/(n+1); cys = scr[1]+scr[3]/2
        o.append(bounce(cxs, cys, t_arr+0.25+i*0.2, f'<circle cx="{R(cxs)}" cy="{R(cys)}" r="16" fill="#FFFFFF"/>' + icon(ic, cxs, cys, 0.75)))
    t = t_arr + 0.3 + len(scr_icons)*0.2
    o.append(check_badge(scr[0]+scr[2]-4, scr[1]+2, t, 12))
    if items:
        x0 = dx + dw + 8
        o.append(connector(x0, x0+30, cy, t+0.1)); x = x0 + 40; t += 0.4
        avail = 1236 - x; gap = 10; w = min(110, (avail - gap*(len(items)-1)) / len(items))
        step = min(0.25, (T_END - 0.5 - t) / len(items))
        for i, it in enumerate(items):
            ti = t + i*step
            tile, badge, lab = tile_card(x, cy, ti, it, w)
            o += [tile, check_badge(badge[0], badge[1], ti+0.3), label(lab[0], lab[1], it.get("label"), ti+0.2)]
            x += w + gap
    return o

def _bez(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n+1):
        u = i/n; v = 1-u
        pts.append((v**3*p0[0]+3*v*v*u*p1[0]+3*v*u*u*p2[0]+u**3*p3[0], v**3*p0[1]+3*v*v*u*p1[1]+3*v*u*u*p2[1]+u**3*p3[1]))
    return pts

def lay_path(sc):
    o = []; nodes = sc["nodes"]; n = len(nodes)
    sx = 250; parts, out, w = prop_start(sx, 112, T0, sc.get("start_icon", "spark")); o += parts
    o.append(label(sx+34, 168, sc.get("start_label"), T0+0.2))
    xs = [out[0] + 70 + i*(1196 - out[0] - 70)/max(n-1, 1) for i in range(n)]
    ys = [150 if i % 2 == 0 else 66 for i in range(n)]
    pts = [(out[0], 112)] + list(zip(xs, ys))
    d = f"M{R(pts[0][0])} {R(pts[0][1])}"; L = 0; cum = [0]; prev = pts[0]
    for a, b in zip(pts, pts[1:]):
        mx = (a[0]+b[0])/2
        c1, c2 = (mx, a[1]), (mx, b[1])
        d += f"C{R(c1[0])} {R(c1[1])} {R(c2[0])} {R(c2[1])} {R(b[0])} {R(b[1])}"
        seg = _bez(a, c1, c2, b); L += sum(math.hypot(q[0]-p[0], q[1]-p[1]) for p, q in zip(seg, seg[1:])); cum.append(L)
    t1, t2 = T0 + 0.35, T_END - 0.5
    for wdt, col in ((12, TEAL_L), (3, TEAL)):
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{wdt}" stroke-linecap="round" stroke-dasharray="{R(L+2)}" stroke-dashoffset="{R(L+2)}">{grow("stroke-dashoffset",R(L+2),0,t1,t2-t1,"0 0 1 1")}</path>')
    for i, nd in enumerate(nodes):
        ti = t1 + (t2-t1)*cum[i+1]/L - 0.05
        x, y = xs[i], ys[i]
        o.append(bounce(x, y, ti, f'<circle cx="{R(x)}" cy="{y+3}" r="24" fill="{SHADOW}"/><circle cx="{R(x)}" cy="{y}" r="24" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>' + icon(nd.get("icon","spark"), x, y, 0.95)))
        if nd.get("check", True): o.append(check_badge(x+18, y-18, ti+0.3, 8))
        lab_y = y + 44 if y > 100 else y - 34
        o.append(label(x, lab_y, nd.get("label"), ti+0.15))
    return o

LAYOUTS = {"pipeline": lay_pipeline, "fly": lay_fly, "path": lay_path}

# ================= v3: seven more scene skeletons =================
PALE = ["#E3F1EA", "#DDE7F3", "#F5E9D3", "#F6E1D6"]

def drop(t, inner, dy=160):
    """从上方掉下来，落地回弹"""
    return (f'<g opacity="0">{show(t,0.04)}<g>'
            f'{A(None,[f"0 {-dy}",f"0 {-dy}","0 5","0 -2","0 0","0 0"],[0,t,t+0.24,t+0.31,t+0.37,D],["0 0 1 1","0.55 0 1 1","0.3 0 0.6 1","0.4 0 0.6 1","0 0 1 1"],"translate")}'
            f'{inner}</g></g>')

def arrow(x1, x2, y, t, d=0.3):
    return (f'<g opacity="0">{show(t,0.05)}'
            f'<line x1="{R(x1)}" y1="{y}" x2="{R(x1)}" y2="{y}" stroke="#8E97A6" stroke-width="3" stroke-linecap="round">{grow("x2",R(x1),R(x2-8),t,d)}</line>'
            f'<g opacity="0">{show(t+d,0.05)}<path d="M{R(x2-13)} {y-8}L{R(x2)} {y}L{R(x2-13)} {y+8}Z" fill="#8E97A6"/></g></g>')

def mini_doc(cx, cy, ic, rot=0, w=50, h=60):
    return (f'<g transform="rotate({rot} {R(cx)} {R(cy)})"><rect x="{R(cx-w/2)}" y="{R(cy-h/2+3)}" width="{w}" height="{h}" rx="6" fill="{SHADOW}"/>'
            f'<rect x="{R(cx-w/2)}" y="{R(cy-h/2)}" width="{w}" height="{h}" rx="6" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
            + icon(ic, cx, cy-6, 0.75) + f'<rect x="{R(cx-w/2+9)}" y="{R(cy+h/2-15)}" width="{w-18}" height="4" rx="2" fill="#C9CED6"/></g>')

def cards_row(x0, items, t, cy=110, maxw=120, gap=10, x_end=1236):
    o = []; n = len(items)
    if not n: return o, t
    w = max(84, min(maxw, (x_end - x0 - gap*(n-1)) / n))
    step = min(0.25, max(0.12, (T_END - 0.4 - t) / n)); x = x0
    for i, it in enumerate(items):
        ti = t + i*step
        tile, badge, lab = tile_card(x, cy, ti, it, w)
        o += [tile, check_badge(badge[0], badge[1], ti+0.3) if it.get("check", True) else "", label(lab[0], lab[1], it.get("label"), ti+0.2)]
        x += w + gap
    return o, t + n*step

def big_circle(cx, cy, r, ic, s, ring=TEAL):
    return (f'<circle cx="{R(cx)}" cy="{R(cy+4)}" r="{r}" fill="{SHADOW}"/>'
            f'<circle cx="{R(cx)}" cy="{R(cy)}" r="{r}" fill="#FFFFFF" stroke="{ring}" stroke-width="3"/>' + icon(ic, cx, cy, s))

# ---- 4. before_after 前后对比：一堆乱活 → 箭头 → 整齐成品 ----
def lay_before_after(sc):
    o = []; cx0, cy0 = 392, 118
    slots = [(-88,-22,-12),(-36,12,8),(14,-30,-6),(66,8,13),(-64,44,5),(32,48,-10),(92,-28,9)]
    ics = sc.get("before", ["doc","chart","mail","photo","doc","text"])[:7]
    o.append(label(cx0, 30, sc.get("before_label"), T0, size=14))
    pile = "".join(bounce(cx0+dx, cy0+dy, T0+0.05+i*0.1, mini_doc(cx0+dx, cy0+dy, ic, rot)) for i, (ic, (dx, dy, rot)) in enumerate(zip(ics, slots)))
    tw_ = T0 + 0.15 + len(ics)*0.1
    c = f"{cx0} {cy0}"
    o.append(f'<g>{A(None,[f"0 {c}",f"0 {c}",f"-3 {c}",f"3 {c}",f"-2 {c}",f"0 {c}",f"0 {c}"],[0,tw_,tw_+0.08,tw_+0.16,tw_+0.24,tw_+0.32,D],None,"rotate")}{pile}</g>')
    t = tw_ + 0.4
    o.append(arrow(518, 648, 112, t))
    v = sc.get("via", {})
    o.append(bounce(583, 112, t+0.15, big_circle(583, 112, 22, v.get("icon","spark"), 0.85)))
    o.append(label(583, 156, v.get("label"), t+0.25))
    t += 0.45
    o.append(label(662, 30, sc.get("after_label"), t, "start", 14, TEAL))
    parts, _ = cards_row(662, sc.get("items", [])[:4], t+0.1); o += parts
    return o

# ---- 5. hub 中心发散：一个中心，周围能力逐个连上 ----
def lay_hub(sc):
    o = []; cx, cy = 740, 106; nodes = sc["nodes"][:6]; n = len(nodes)
    slots = [(-440,-6),(-300,-56),(-200,52),(200,52),(300,-56),(440,-6)]
    use = sorted([[0,5,2,3,1,4][i] for i in range(n)])
    pos = sorted([slots[i] for i in use], key=lambda p: p[0])
    c = sc.get("center", {})
    for tp in (T0+0.45, T0+1.45, T0+2.45):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="none" stroke="{TEAL}" stroke-width="2" opacity="0">'
                 f'{A("r",[44,44,90,90],[0,tp,tp+1.0,D],["0 0 1 1","0.2 0.6 0.4 1","0 0 1 1"])}{A("opacity",[0,0,0.5,0,0],[0,tp,tp+0.05,tp+1.0,D])}</circle>')
    o.append(bounce(cx, cy, T0, big_circle(cx, cy, 44, c.get("icon","spark"), 1.6)))
    o.append(label(cx, cy+70, c.get("label"), T0+0.2, size=14, col=INK))
    t = T0 + 0.5; step = min(0.42, (T_END - 0.6 - t) / max(n, 1))
    order = sorted(range(n), key=lambda i: abs(pos[i][0]))   # 由近到远依次连上
    for k, i in enumerate(order):
        nd = nodes[i]; nx, ny = cx + pos[i][0], cy + pos[i][1]; ti = t + k*step
        L = math.hypot(nx-cx, ny-cy); ux, uy = (nx-cx)/L, (ny-cy)/L
        x1, y1, x2, y2 = cx+ux*48, cy+uy*48, nx-ux*28, ny-uy*28
        o.append(f'<line x1="{R(x1)}" y1="{R(y1)}" x2="{R(x1)}" y2="{R(y1)}" stroke="#AEB6C2" stroke-width="2.5" stroke-dasharray="5 5" stroke-linecap="round" opacity="0">'
                 f'{show(ti,0.05)}{grow("x2",R(x1),R(x2),ti,0.25)}{grow("y2",R(y1),R(y2),ti,0.25)}</line>')
        o.append(bounce(nx, ny, ti+0.22, f'<circle cx="{R(nx)}" cy="{R(ny+3)}" r="25" fill="{SHADOW}"/><circle cx="{R(nx)}" cy="{R(ny)}" r="25" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>' + icon(nd.get("icon","spark"), nx, ny, 0.95)))
        if nd.get("check", True): o.append(check_badge(nx+19, ny-19, ti+0.5, 8))
        o.append(label(nx, ny-36 if ny < cy-20 else ny+44, nd.get("label"), ti+0.35))
    return o

# ---- 6. stack 搭积木：模块一块块掉进托盘，拼成成品 ----
def lay_stack(sc):
    o = []; blocks = sc["blocks"][:6]; n = len(blocks)
    cols = min(3, max(1, math.ceil(n/2))); bw = 140 if cols == 3 else 160; bh, gap = 54, 10
    x0 = 350 if cols == 3 else 380; Wd = cols*bw + (cols-1)*gap; base = 186
    o.append(f'<g opacity="0">{show(T0,0.2)}<path d="M{x0-14} 58V{base+2}H{x0+Wd+14}V58" fill="none" stroke="#C9CED6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>')
    t = T0 + 0.2; step = min(0.32, 2.0 / max(n, 1))
    for i, b in enumerate(blocks):
        r, cidx = divmod(i, cols)
        x = x0 + cidx*(bw+gap); y = base - 6 - bh - r*(bh+8)
        col = PALE[i % 4]
        inner = (f'<rect x="{x}" y="{y+4}" width="{bw}" height="{bh}" rx="8" fill="{SHADOW}"/>'
                 f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{col}" stroke="#FFFFFF" stroke-width="2"/>'
                 f'<circle cx="{x+26}" cy="{y+bh/2}" r="17" fill="#FFFFFF"/>' + icon(b.get("icon","spark"), x+26, y+bh/2, 0.75)
                 + f'<text x="{x+52}" y="{y+bh/2+5}" font-size="14" fill="{INK}">{esc(b.get("label",""))}</text>')
        o.append(drop(t + i*step, inner))
    t = t + n*step + 0.1
    P = 2*(Wd+28) + 2*(base-48+6)
    o.append(f'<rect x="{x0-14}" y="48" width="{Wd+28}" height="{base-42}" rx="12" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-dasharray="{P}" stroke-dashoffset="{P}">{grow("stroke-dashoffset",P,0,t,0.45,"0 0 1 1")}</rect>')
    o.append(label(x0 + Wd/2, 210, sc.get("label"), t+0.2))
    ax = x0 + Wd + 28; t += 0.45
    o.append(arrow(ax, ax+80, 112, t)); t += 0.3
    res = sc.get("result", {}); rx, rw, rh = ax + 92, 210, 136; ry = 112 - rh/2
    card = (f'<rect x="{rx}" y="{ry+6}" width="{rw}" height="{rh}" rx="14" fill="{SHADOW}"/>'
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
            + "".join(f'<circle cx="{rx+16+i*10}" cy="{ry+15}" r="3" fill="#C9CED6"/>' for i in range(3))
            + f'<circle cx="{rx+52}" cy="{ry+72}" r="28" fill="{TEAL_L}"/>' + icon(res.get("icon","play"), rx+52, ry+72, 1.3)
            + f'<rect x="{rx+96}" y="{ry+52}" width="92" height="9" rx="4.5" fill="{TEAL}"/><rect x="{rx+96}" y="{ry+70}" width="70" height="7" rx="3.5" fill="#C9CED6"/><rect x="{rx+96}" y="{ry+86}" width="80" height="7" rx="3.5" fill="#C9CED6"/>')
    o.append(bounce(rx+rw/2, 112, t, card, 1.1))
    o.append(check_badge(rx+rw-8, ry+6, t+0.4, 13))
    o.append(label(rx+rw/2, ry+rh+24, res.get("label"), t+0.2, size=14, col=INK))
    return o

# ---- 7. dialog 对话来回：你一句它一句，最后交付成品 ----
def lay_dialog(sc):
    o = []; msgs = sc["messages"][:4]; wx, wy, ww, wh = 258, 16, 470, 190
    win = (f'<rect x="{wx}" y="{wy+6}" width="{ww}" height="{wh}" rx="14" fill="{SHADOW}"/>'
           f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
           + "".join(f'<circle cx="{wx+16+i*11}" cy="{wy+16}" r="3.2" fill="#C9CED6"/>' for i in range(3))
           + (f'<text x="{wx+ww/2}" y="{wy+20}" font-size="12" fill="{MUT}" text-anchor="middle">{esc(sc["window_title"])}</text>' if sc.get("window_title") else ""))
    o.append(bounce(wx+ww/2, wy+wh/2, T0, win, 1.06))
    y = wy + 34; t = T0 + 0.3
    for m in msgs:
        txt = m.get("text", ""); bw = tw(txt, 13) + 28; bh = 28
        if m.get("from") == "me":
            bx = wx + ww - 16 - bw
            b = f'<rect x="{R(bx)}" y="{y}" width="{R(bw)}" height="{bh}" rx="14" fill="{TEAL}"/><text x="{R(bx+14)}" y="{y+19}" font-size="13" fill="#FFFFFF">{esc(txt)}</text>'
            o.append(bounce(bx+bw, y+bh/2, t, b, 1.08)); t += 0.42
        else:
            bx = wx + 50
            o.append(bounce(wx+28, y+bh/2, t, f'<circle cx="{wx+28}" cy="{y+bh/2}" r="14" fill="{TEAL_L}"/>' + icon("spark", wx+28, y+bh/2, 0.6)))
            dots = "".join(f'<circle cx="{bx+16+i*10}" cy="{y+bh/2}" r="3" fill="#9AA3AF"/>' for i in range(3))
            o.append(f'<g opacity="0">{A("opacity",[0,0,1,1,0,0],[0,t+0.05,t+0.1,t+0.4,t+0.45,D])}<rect x="{bx}" y="{y}" width="52" height="{bh}" rx="14" fill="#F2F4F7"/>{dots}</g>')
            t += 0.42
            b = f'<rect x="{bx}" y="{y}" width="{R(bw)}" height="{bh}" rx="14" fill="#F2F4F7"/><text x="{bx+14}" y="{y+19}" font-size="13" fill="{INK}">{esc(txt)}</text>'
            o.append(bounce(bx, y+bh/2, t, b, 1.08)); t += 0.42
        y += 40
    x = wx + ww + 10
    o.append(connector(x, x+34, 112, t)); t += 0.3
    parts, _ = cards_row(x+44, sc.get("items", [])[:3], t, maxw=130); o += parts
    return o

# ---- 8. calendar 一周打卡：设一次，每天自动盖章 ----
def lay_calendar(sc):
    o = []; days = sc["days"][:7]; n = len(days)
    parts, out, w = prop_start(254, 108, T0, sc.get("start_icon", "bell")); o += parts
    o.append(label(288, 166, sc.get("start_label"), T0+0.2))
    o.append(connector(out[0]+6, out[0]+30, 108, T0+0.3))
    x0 = out[0] + 38; gap = 10; cw = min(124, (1236 - x0 - gap*(n-1)) / n); ch, y = 116, 46
    for i, d in enumerate(days):
        x = x0 + i*(cw+gap); ti = T0 + 0.5 + i*0.1
        card = (f'<rect x="{R(x)}" y="{y+5}" width="{R(cw)}" height="{ch}" rx="10" fill="{SHADOW}"/>'
                f'<rect x="{R(x)}" y="{y}" width="{R(cw)}" height="{ch}" rx="10" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
                f'<path d="M{R(x)} {y+26}V{y+10}A10 10 0 0 1 {R(x+10)} {y}H{R(x+cw-10)}A10 10 0 0 1 {R(x+cw)} {y+10}V{y+26}Z" fill="{NAVY}"/>'
                f'<text x="{R(x+cw/2)}" y="{y+18}" font-size="12" fill="#FFFFFF" text-anchor="middle">{esc(d.get("day",""))}</text>'
                + icon(d.get("icon", "spark"), x+cw/2, y+66, 1.2))
        o.append(bounce(x+cw/2, y+ch/2, ti, card))
        o.append(label(x+cw/2, y+ch+24, d.get("label"), ti+0.1))
    ts0 = T0 + 0.6 + n*0.1 + 0.2; step = min(0.4, (T_END - 0.2 - ts0) / max(n, 1))
    for i, d in enumerate(days):
        st = d.get("stamp", sc.get("stamp", "已办"))
        if not st: continue
        x = x0 + i*(cw+gap); sx, sy = x + cw - 24, y + ch - 22; ts = ts0 + i*step
        inner = (f'<g transform="rotate(-14 {R(sx)} {sy})"><circle cx="{R(sx)}" cy="{sy}" r="20" fill="#FFFFFF" fill-opacity=".85" stroke="{OR}" stroke-width="2.5"/>'
                 f'<circle cx="{R(sx)}" cy="{sy}" r="15.5" fill="none" stroke="{OR}" stroke-width="1"/>'
                 f'<text x="{R(sx)}" y="{sy+4}" font-size="11" font-weight="700" fill="{OR}" text-anchor="middle">{esc(st)}</text></g>')
        o.append(f'<g opacity="0">{show(ts,0.04)}<g transform="translate({R(sx)} {sy})"><g>'
                 f'{A(None,[1.9,1.9,0.9,1.04,1,1],[0,ts,ts+0.12,ts+0.2,ts+0.26,D],["0 0 1 1","0.6 0 1 1","0.4 0 0.6 1","0.4 0 0.6 1","0 0 1 1"],"scale")}'
                 f'<g transform="translate({R(-sx)} {-sy})">{inner}</g></g></g></g>')
    return o

# ---- 9. funnel 漏斗筛选：一大堆信息倒进去，只出几样重点 ----
def lay_funnel(sc):
    o = []
    ins = sc.get("inputs", ["mail","chat","doc","mail","photo","chat","doc","mail","chart","chat"])[:10]
    P = [(298,62),(356,92),(418,58),(476,96),(306,138),(370,160),(436,128),(494,160),(352,40),(470,40)]
    o.append(label(392, 208, sc.get("input_label"), T0+0.3))
    fx = 560
    fun = (f'<path d="M{fx} 34L{fx+130} 95H{fx+186}V127H{fx+130}L{fx} 188Z" fill="#3B4252"/>'
           f'<path d="M{fx} 34L{fx+130} 95H{fx+186}V100H{fx+130}L{fx} 42Z" fill="#FFFFFF" opacity=".12"/>'
           f'<text x="{fx+64}" y="{116}" font-size="14" fill="#FFFFFF" text-anchor="middle">{esc(sc.get("filter_label",""))}</text>')
    o.append(bounce(fx+93, 111, T0, fun, 1.08))
    tm = T0
    for i, ic in enumerate(ins):
        x, y = P[i]; ti = T0 + 0.15 + i*0.08; tm = T0 + 1.15 + i*0.13
        chip = (f'<rect x="{x-17}" y="{y-17+3}" width="34" height="34" rx="8" fill="{SHADOW}"/>'
                f'<rect x="{x-17}" y="{y-17}" width="34" height="34" rx="8" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.2"/>' + icon(ic, x, y, 0.7))
        o.append(f'<g>{A("opacity",[1,1,0,0],[0,tm+0.24,tm+0.36,D])}<g>'
                 f'{A(None,["0 0","0 0",f"{fx+30-x} {111-y}",f"{fx+30-x} {111-y}"],[0,tm,tm+0.36,D],["0 0 1 1","0.5 0 0.9 0.7","0 0 1 1"],"translate")}'
                 f'{bounce(x, y, ti, chip)}</g></g>')
    t = tm + 0.4
    o.append(connector(fx+192, fx+222, 111, t-0.1))
    parts, _ = cards_row(fx+232, sc.get("items", [])[:3], t+0.1, cy=111, maxw=130); o += parts
    return o

# ---- 10. chart 数据对比：柱子长高，右侧亮出结论 ----
def lay_chart(sc):
    o = []; bars = sc["bars"][:6]; n = len(bars); ax0, ax1, base, maxh = 290, 830, 176, 122
    vmax = max(b["value"] for b in bars) or 1
    o.append(f'<g opacity="0">{show(T0,0.2)}<line x1="{ax0-10}" y1="{base}" x2="{ax1}" y2="{base}" stroke="#C9CED6" stroke-width="2"/></g>')
    slot = (ax1-ax0)/n; bw = min(78, slot*0.56); t = T0 + 0.2; step = min(0.4, 2.2/n)
    cols = {"gray": "#C9CED6", "teal": TEAL, "orange": OR, "blue": BLUE}
    for i, b in enumerate(bars):
        x = ax0 + slot*i + (slot-bw)/2; h = max(4, maxh*b["value"]/vmax); ti = t + i*step
        col = cols.get(b.get("color"), OR if i == n-1 else "#C9CED6")
        sp = ["0 0 1 1", "0.2 0.8 0.3 1", "0 0 1 1"]
        o.append(f'<rect x="{R(x)}" y="{base}" width="{R(bw)}" height="0" rx="6" fill="{col}">'
                 f'{A("y",[base,base,R(base-h),R(base-h)],[0,ti,ti+0.5,D],sp)}{A("height",[0,0,R(h),R(h)],[0,ti,ti+0.5,D],sp)}</rect>')
        o.append(f'<rect x="{R(x)}" y="{base-6}" width="{R(bw)}" height="6" fill="{col}" opacity="0">{show(ti,0.02)}</rect>')
        o.append(label(x+bw/2, base-h-10, b.get("text"), ti+0.45, size=15, col=INK))
        o.append(label(x+bw/2, base+22, b.get("label"), ti))
    t = t + n*step + 0.3
    bd = sc.get("badge", {}); big = bd.get("label", ""); sub = bd.get("sub", "")
    w = max(250, 120 + max(tw(big, 30), tw(sub, 13))); h = 112; x = 1226 - w; y = 110 - h/2
    card = (f'<rect x="{R(x)}" y="{R(y+6)}" width="{R(w)}" height="{h}" rx="16" fill="{SHADOW}"/>'
            f'<rect x="{R(x)}" y="{R(y)}" width="{R(w)}" height="{h}" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>'
            f'<circle cx="{R(x+52)}" cy="110" r="30" fill="{TEAL_L}"/>' + icon(bd.get("icon", "chart"), x+52, 110, 1.3)
            + f'<text x="{R(x+98)}" y="{122 if not sub else 112}" font-size="30" font-weight="700" fill="{OR}">{esc(big)}</text>'
            + (f'<text x="{R(x+100)}" y="138" font-size="13" fill="{MUT}">{esc(sub)}</text>' if sub else ""))
    o.append(bounce(x+w/2, 110, t, card, 1.1))
    o.append(check_badge(x+w-8, y+6, t+0.4, 13))
    return o

LAYOUTS.update({"before_after": lay_before_after, "hub": lay_hub, "stack": lay_stack, "dialog": lay_dialog,
                "calendar": lay_calendar, "funnel": lay_funnel, "chart": lay_chart})


# ================= style "card": 标题卡横幅（左标题 + 右步骤卡 + 结论按钮） =================
CW, CH, TT = 1246, 420, 4.4     # 画布、入场动画总时长（只播一次，停在最终画面）
THEMES = {
    "blue":   dict(main="#2563EB", light="#DBEAFE", line="#93C5FD", border="#BFDBFE", bg="#F8FAFC"),
    "orange": dict(main="#C9643E", light="#F6E1D6", line="#E3A688", border="#EBCBB9", bg="#FBF8F5"),
    "teal":   dict(main="#12A37F", light="#D5F2E8", line="#7FD1B6", border="#BCE7D8", bg="#F6FBF9"),
}

def F(attr, vals, ts, spline=None, typ=None):
    """只播一次并停住（fill=freeze）"""
    kt = ";".join(str(round(min(max(t / TT, 0), 1), 4)) for t in ts); vs = ";".join(str(v) for v in vals); ex = ""
    if spline:
        sp = spline if isinstance(spline, list) else [spline] * (len(ts) - 1)
        ex = f' calcMode="spline" keySplines="{";".join(sp)}"'
    if typ:
        return f'<animateTransform attributeName="transform" type="{typ}" values="{vs}" keyTimes="{kt}"{ex} dur="{TT}s" fill="freeze"/>'
    return f'<animate attributeName="{attr}" values="{vs}" keyTimes="{kt}"{ex} dur="{TT}s" fill="freeze"/>'

def f_in(t, d=0.3):
    return F("opacity", [0, 0, 1, 1], [0, t, t + d, TT])

def f_rise(t, inner, dy=18, d=0.4):
    return (f'<g opacity="0">{f_in(t, d)}<g>{F(None, [f"0 {dy}", f"0 {dy}", "0 0", "0 0"], [0, t, t + d, TT], ["0 0 1 1", EASE, "0 0 1 1"], "translate")}'
            f'{inner}</g></g>')

def f_pop(cx, cy, t, inner, big=1.08):
    return (f'<g opacity="0">{f_in(t, 0.08)}<g transform="translate({R(cx)} {R(cy)})"><g>'
            f'{F(None, [0.6, 0.6, big, 0.98, 1, 1], [0, t, t + 0.18, t + 0.28, t + 0.36, TT], ["0 0 1 1", "0.3 0 0.6 1", "0.4 0 0.6 1", "0.4 0 0.6 1", "0 0 1 1"], "scale")}'
            f'<g transform="translate({R(-cx)} {R(-cy)})">{inner}</g></g></g></g>')

def line_icon(name, cx, cy, c, lt, sc=1.0):
    sn = f'stroke="{c}" stroke-width="{R(4/sc)}" stroke-linecap="round" stroke-linejoin="round"'
    s = 'fill="none" ' + sn
    I = {
     "grid": f'<path d="M-12-30V30M12-30V30M-34-11H34M-34 11H34" {s}/>',
     "code": f'<path d="M-20-18L-38 0L-20 18M20-18L38 0L20 18M6-24L-6 24" {s}/>',
     "play": f'<rect x="-36" y="-26" width="72" height="52" rx="6" fill="{lt}"/><path d="M-10-15L16 0L-10 15Z" fill="{c}"/>',
     "doc": f'<path d="M-20-30H8L22-16V30H-20Z" {s}/><path d="M8-30V-16H22M-10-2H12M-10 12H8" {s}/>',
     "lines": f'<path d="M-36-16H36M-36 0H24M-36 16H30" {s}/>',
     "chat": f'<path d="M-32-24H32V14H-6L-20 28V14H-32Z" {s}/><path d="M-16-6H16" {s}/>',
     "spark": f'<path d="M0-30Q4-4 30 0Q4 4 0 30Q-4 4-30 0Q-4-4 0-30Z" {s}/>',
     "image": f'<rect x="-34" y="-24" width="68" height="48" rx="6" {s}/><path d="M-30 18L-8-4L6 10L14 2L30 18" {s}/><circle cx="14" cy="-10" r="5" fill="{c}"/>',
     "mic": f'<rect x="-9" y="-30" width="18" height="34" rx="9" {s}/><path d="M-20-2A20 20 0 0 0 20-2M0 18V28M-12 28H12" {s}/>',
     "music": f'<path d="M-10 20V-24L22-30V14" {s}/><circle cx="-18" cy="20" r="8" {s}/><circle cx="14" cy="14" r="8" {s}/>',
     "bell": f'<path d="M-20 14V-4A20 20 0 0 1 20-4V14L26 20H-26Z" {s}/><path d="M-6 26H6" {s}/>',
     "calendar": f'<rect x="-30" y="-24" width="60" height="52" rx="6" {s}/><path d="M-30-8H30M-14-32V-18M14-32V-18" {s}/>',
     "chart": f'<rect x="-36" y="-26" width="72" height="52" rx="6" fill="{lt}" opacity=".6"/><path d="M-24 14V2M-12 14V-8M0 14V-2M10-12H28M10 0H28M10 12H22" {s}/>',
     "mail": f'<rect x="-34" y="-22" width="68" height="44" rx="5" {s}/><path d="M-32-18L0 6L32-18" {s}/>',
     "person": f'<circle cy="-14" r="13" {s}/><path d="M-26 28Q-26 4 0 4Q26 4 26 28" {s}/>',
     "cube": f'<path d="M0-30L28-15V15L0 30L-28 15V-15Z" fill="{lt}" {sn}/><path d="M-28-15L0 0L28-15M0 0V30" {s}/>',
     "game": f'<path d="M-24-14H24A14 14 0 0 1 36 4L32 18A8 8 0 0 1 18 22L10 12H-10L-18 22A8 8 0 0 1-32 18L-36 4A14 14 0 0 1-24-14Z" {s}/><path d="M-20-2V8M-25 3H-15" {s}/><circle cx="18" cy="0" r="3" fill="{c}"/><circle cx="24" cy="7" r="3" fill="{c}"/>',
     "scissors": f'<circle cx="-14" cy="18" r="9" {s}/><circle cx="14" cy="18" r="9" {s}/><path d="M-8 11L18-28M8 11L-18-28" {s}/>',
     "text": f'<path d="M-26-24H26M0-24V28M-12 28H12" {s}/>',
     "wand": f'<path d="M-26 26L14-14" {s}/><path d="M18-34L21-23L32-20L21-17L18-6L15-17L4-20L15-23Z" fill="{c}"/>',
     "robot": f'<rect x="-28" y="-18" width="56" height="42" rx="10" {s}/><path d="M0-18V-30" {s}/><circle cy="-32" r="3" fill="{c}"/><circle cx="-11" cy="2" r="4" fill="{c}"/><circle cx="11" cy="2" r="4" fill="{c}"/>',
     "web": f'<rect x="-40" y="-26" width="80" height="52" rx="3" {s}/><rect x="-32" y="-18" width="64" height="36" fill="{lt}"/><path d="M-20 10L-10-6H10L20 10" {s}/><circle cy="4" r="4" fill="{c}"/>',
     "home": f'<path d="M-26-4L0-28L26-4V26H-26Z" fill="{lt}" {sn}/>',
     "dice": f'<rect x="-26" y="-26" width="52" height="52" rx="8" {s}/><circle cx="-11" cy="-11" r="4" fill="{c}"/><circle r="4" fill="{c}"/><circle cx="11" cy="11" r="4" fill="{c}"/>',
     "box": f'<rect x="-30" y="-24" width="60" height="48" rx="3" {s}/><path d="M-30-10H30M-8 2H8" {s}/>',
     "layers": f'<path d="M0-26L30-12L0 2L-30-12Z" {s}/><path d="M-30 0L0 14L30 0M-30 12L0 26L30 12" {s}/>',
     "monitor": f'<rect x="-34" y="-26" width="68" height="44" rx="5" fill="{lt}" {sn}/><path d="M-18-10H18M-18 2H10M-12 30H12M0 18V30" {s}/>',
     "heart": f'<path d="M0 26C-36 4-28-26 0-12C28-26 36 4 0 26Z" {s}/>',
     "film": f'<rect x="-36" y="-24" width="72" height="48" rx="5" {s}/><path d="M-24-24V24M24-24V24M-36-8H-24M-36 8H-24M24-8H36M24 8H36" {s}/>',
     "scene_wide": f'<path d="M-24-28H24L16-16H-16Z" {s}/><path d="M-40 26H40M32 26V-30H44V26" {s}/><circle cy="0" r="7" fill="{c}"/><path d="M-12 26L0 6L12 26Z" fill="{c}"/>',
     "scene_mid": f'<circle cy="-24" r="11" fill="{c}"/><path d="M-22 30L0-10L22 30Z" fill="{c}"/><path d="M-40 10L-18-2M18-2L40-14" {s}/>',
     "scene_close": f'<path d="M-40 24L-10 4L10 14L40-12" fill="none" stroke="{c}" stroke-width="{R(8/sc)}" stroke-linecap="round" opacity=".35"/><rect x="-18" y="-24" width="36" height="26" rx="3" fill="#FFFFFF" {sn}/><path d="M-18-22L0-8L18-22" {s}/>',
    }
    return f'<g transform="translate({R(cx)} {R(cy)}) scale({sc})">{I.get(name, I["spark"])}</g>'

# ---------- card 右栏通用部件 ----------
INK2, GRAY, GRAY2, MONO = "#111827", "#6B7280", "#94A3B8", "#94A3B8"
X0, X1 = 592, 1196

def _txt(x, y, s, size=16, w=400, fill=INK2, anchor="start", ls=0):
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{R(x)}" y="{R(y)}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{lsa}>{esc(s)}</text>'

def _box(x, y, w, h, stroke, fill="#FFFFFF", rx=16, sw=2):
    return f'<rect x="{R(x)}" y="{R(y)}" width="{R(w)}" height="{R(h)}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def _gline(x1, y1, x2, y2, col, t, d=0.25, sw=2.5, dash=""):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{R(x1)}" y1="{R(y1)}" x2="{R(x1)}" y2="{R(y1)}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"{da}>'
            f'{F("x2",[R(x1),R(x1),R(x2),R(x2)],[0,t,t+d,TT])}{F("y2",[R(y1),R(y1),R(y2),R(y2)],[0,t,t+d,TT])}</line>')

def _gpath(d, L, col, t, dur=0.4, sw=2.5):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{L}" stroke-dashoffset="{L}">'
            f'{F("stroke-dashoffset",[L,L,0,0],[0,t,t+dur,TT])}</path>')

def _arrow(x1, x2, y, col, t):
    return _gline(x1, y, x2-2, y, col, t) + f'<g opacity="0">{f_in(t+0.22,0.1)}<path d="M{R(x2-10)} {y-7}L{R(x2)} {y}L{R(x2-10)} {y+7}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>'

def _cycle(i, k, each=1.5, low=0.4):
    """入场后，k 个元素轮流高亮（其余变淡）"""
    if k < 2: return ""
    e = 0.12 / k; s0, s1 = i / k, (i + 1) / k
    if i == 0: pts = [(0, 1), (s1 - e, 1), (s1, low), (1 - e, low), (1, 1)]
    elif i == k - 1: pts = [(0, low), (s0, low), (s0 + e, 1), (1 - e, 1), (1, low)]
    else: pts = [(0, low), (s0, low), (s0 + e, 1), (s1 - e, 1), (s1, low), (1, low)]
    return (f'<animate attributeName="opacity" values="{";".join(str(v) for _, v in pts)}" keyTimes="{";".join(str(round(p, 4)) for p, _ in pts)}" '
            f'dur="{k*each}s" begin="{TT}s" repeatCount="indefinite"/>')

def _button(y, h, text, th, t, x=X0, w=None, size=22):
    w = w or (X1 - x); mid = x + w/2
    shine = (f'<path d="M{x+14} {y}h34l-{R(h*0.35)} {h}h-34Z" fill="#FFFFFF" opacity="0">'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;{R(w-60)} 0;{R(w-60)} 0" keyTimes="0;0.35;1" dur="3.2s" begin="{TT}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;0.28;0.28;0;0" keyTimes="0;0.05;0.3;0.35;1" dur="3.2s" begin="{TT}s" repeatCount="indefinite"/></path>')
    return f_pop(mid, y+h/2, t, f'<rect x="{x}" y="{y}" width="{R(w)}" height="{h}" rx="{min(16, h/2)}" fill="{th["main"]}"/>'
                               + _txt(mid, y+h/2+size*0.36, text, size, 800, "#FFFFFF", "middle") + shine, 1.05)

def _mono(x, y, s, t, anchor="start"):
    return f'<g opacity="0">{f_in(t)}{_txt(x, y, s, 14, 500, MONO, anchor, 2)}</g>'

def _caption(y, s, th, t):
    return f_rise(t, _txt((X0+X1)/2, y, s, 22, 800, th["main"], "middle"), 8)

# ---------- 右栏版式 ----------
def r_steps(c, th, t):
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    steps = c.get("steps", [])[:4]; n = len(steps); gap = 26
    cw = (X1 - X0 - gap*(n-1)) / max(n, 1); y0, h = 72, 150
    for i, st in enumerate(steps):
        x = X0 + i*(cw+gap); ti = t + i*0.28
        if i: o.append(_gline(x-gap, y0+h/2, x, y0+h/2, LN, ti-0.1, 0.18))
        card = _box(x, y0, cw, h, BD, rx=18) + line_icon(st.get("icon","spark"), x+cw/2, y0+56, M, LT) + _txt(x+cw/2, y0+126, st.get("label",""), 19, 700, M, "middle")
        o.append(f_pop(x+cw/2, y0+h/2, ti, card))
    mid = (X0+X1)/2; t2 = t + n*0.28 + 0.15
    o.append(f'<line x1="{mid}" y1="262" x2="{mid}" y2="262" stroke="{LN}" stroke-width="2.5">'
             f'{F("x1",[mid,mid,mid-215,mid-215],[0,t2,t2+0.35,TT],["0 0 1 1",EASE,"0 0 1 1"])}{F("x2",[mid,mid,mid+215,mid+215],[0,t2,t2+0.35,TT],["0 0 1 1",EASE,"0 0 1 1"])}</line>')
    t3 = t2 + 0.25; o.append(_button(294, 64, c.get("result",""), th, t3))
    flow = c.get("flow") or [s.get("label","") for s in steps]; t4 = t3 + 0.35
    o.append(f'<g opacity="0">{f_in(t4,0.2)}<circle cx="{X0+30}" cy="383" r="5" fill="{M}"/></g>')
    spans = "".join(f'<tspan fill-opacity="0">{F("fill-opacity",[0,0,1,1],[0,t4+0.15*i,t4+0.15*i+0.2,TT])}{esc((" → " if i else "") + seg)}</tspan>' for i, seg in enumerate(flow))
    o.append(f'<text x="{X0+46}" y="389" font-size="16" font-weight="700" fill="#4B5563" xml:space="preserve">{spans}</text>')
    return o

def r_remix(c, th, t):
    """三卡流程（源 → 高亮改造 → 结果）+ 下方镜头轨道"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    cards = c.get("cards", [])[:3]; gap = 50; cw = (X1 - X0 - 2*gap) / 3; y0, h = 64, 158
    centers = []
    for i, cd in enumerate(cards):
        x = X0 + i*(cw+gap); ti = t + i*0.35; cx = x + cw/2; centers.append(cx)
        if cd.get("hl"):
            hy, hh = y0+22, h-44
            inner = (_box(x, hy, cw, hh, LN, LT, 16) + _txt(cx, hy+48, cd.get("title",""), 21, 800, M, "middle")
                     + _txt(cx, hy+84, cd.get("sub",""), 19, 600, "#475569", "middle"))
        else:
            art = cd.get("art", "nodes")
            if art == "nodes":
                ax, ay = x+24, y0+70
                a = (f'<path d="M{R(ax+48)} {ay+13}H{R(ax+78)}M{R(ax+30)} {ay+26}V{ay+56}H{R(ax+78)}" fill="none" stroke="{BD}" stroke-width="2"/>'
                     f'<rect x="{R(ax)}" y="{ay}" width="48" height="26" rx="5" fill="#E2E8F0"/><rect x="{R(ax+78)}" y="{ay}" width="{R(cw-126)}" height="26" rx="5" fill="{LT}"/>'
                     f'<rect x="{R(ax+78)}" y="{ay+44}" width="{R(cw-126)}" height="24" rx="5" fill="{LT}" opacity=".55"/>')
            elif art == "image":
                ax, ay, aw = x+18, y0+58, cw-36
                a = (f'<rect x="{R(ax)}" y="{ay}" width="{R(aw)}" height="80" rx="6" fill="{LT}"/>'
                     f'<path d="M{R(ax)} {ay+76}L{R(ax+aw*0.3)} {ay+40}L{R(ax+aw*0.55)} {ay+66}L{R(ax+aw*0.75)} {ay+30}L{R(ax+aw)} {ay+70}V{ay+80}H{R(ax)}Z" fill="{LN}" opacity=".7"/>'
                     f'<circle cx="{R(ax+aw/2)}" cy="{ay+28}" r="9" fill="{M}"/><path d="M{R(ax+aw/2-18)} {ay+58}A18 16 0 0 1 {R(ax+aw/2+18)} {ay+58}Z" fill="{M}"/>')
            else:
                a = line_icon(art, cx, y0+100, M, LT, 0.85)
            col = M if i == len(cards)-1 else "#475569"
            inner = _box(x, y0, cw, h, BD) + _txt(cx, y0+34, cd.get("title",""), 19, 800, col, "middle") + a
        if i: o.append(_arrow(x-gap+8, x-6, y0+h/2, LN, ti-0.15))
        o.append(f_pop(cx, y0+h/2, ti, inner))
    t2 = t + len(cards)*0.35 + 0.1
    tx = X0 + (X1-X0)*0.5
    d = f"M{R(centers[-1])} {y0+h}V{y0+h+30}H{R(tx)}V{y0+h+60}"; L = round(30 + abs(centers[-1]-tx) + 30 + 4)
    o.append(_gpath(d, L, LN, t2, 0.35))
    ty, thh = y0+h+60, 76; t3 = t2 + 0.3
    o.append(f'<g opacity="0">{f_in(t3)}{_box(X0, ty, X1-X0, thh, BD)}{_txt(X0+22, ty+26, c.get("track_label","SHOT"), 14, 700, GRAY2, "start", 2)}</g>')
    segs = c.get("track", [0.36, 0.4, 0.24]); x = X0+22; wtot = X1-X0-44; cols = [LN, LT, LT]
    for i, f in enumerate(segs):
        w = wtot*f - 10; ti = t3 + 0.15 + i*0.18
        o.append(f'<rect x="{R(x)}" y="{ty+40}" width="0" height="20" rx="4" fill="{cols[i%3]}" opacity="{1 if i < 2 else .6}">{F("width",[0,0,R(w),R(w)],[0,ti,ti+0.25,TT])}</rect>')
        x += wtot*f
    o.append(f'<g opacity="0">{f_in(t3+0.7)}<rect x="{X0+22}" y="{ty+32}" width="3" height="36" rx="1.5" fill="{M}">'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;{wtot-4} 0;{wtot-4} 0" keyTimes="0;0.8;1" dur="4s" begin="{TT}s" repeatCount="indefinite"/></rect></g>')
    o.append(_caption(ty+thh+32, c.get("caption",""), th, t3+0.6))
    return o

def r_pick(c, th, t):
    """一堆平均方案 → 「选」→ 一张歪着的高亮卡"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    gx, gy, tw_, th_, gp = X0, 66, 60, 76, 12
    for i in range(6):
        r, cidx = divmod(i, 3); x = gx + cidx*(tw_+gp); y = gy + r*(th_+gp)
        tile = (_box(x, y, tw_, th_, "#E2E8F0", "#FFFFFF", 8, 1.5) + f'<circle cx="{x+30}" cy="{y+24}" r="9" fill="#CBD5E1"/>'
                f'<rect x="{x+14}" y="{y+44}" width="32" height="4" rx="2" fill="#CBD5E1"/><rect x="{x+14}" y="{y+56}" width="32" height="4" rx="2" fill="#CBD5E1"/>')
        o.append(f_pop(x+tw_/2, y+th_/2, t + i*0.08, tile))
    o.append(f'<g opacity="0">{f_in(t+0.5)}{_txt(gx+102, gy+2*(th_+gp)+20, c.get("grid_label",""), 17, 600, GRAY2, "middle")}</g>')
    t2 = t + 0.7; cy = 152; px = X0 + 300
    o.append(_gline(X0+222, cy, px-34, cy, LN, t2, 0.2))
    o.append(f_pop(px, cy, t2+0.15, f'<circle cx="{px}" cy="{cy}" r="32" fill="{LT}" stroke="{LN}" stroke-width="2"/>' + _txt(px, cy+9, c.get("pick","选"), 24, 800, M, "middle"), 1.15))
    o.append(f'<g opacity="0">{f_in(t2+0.3)}{_txt(px, cy+60, c.get("pick_label",""), 17, 600, "#475569", "middle")}</g>')
    o.append(_arrow(px+36, X0+404, cy, LN, t2+0.35))
    hx, hy, hw, hh = X0+418, 44, 176, 236; hc = (hx+hw/2, hy+hh/2); t3 = t2 + 0.6
    card = (f'<g transform="rotate(5 {R(hc[0])} {R(hc[1])})">' + _box(hx, hy, hw, hh, M, "#FFFFFF", 14, 3.5)
            + f'<line x1="{hx+26}" y1="{hy+24}" x2="{hx+hw-26}" y2="{hy+24}" stroke="{LT}" stroke-width="2"/>'
            + _txt(hx+24, hy+66, c.get("card_title1",""), 20, 800, INK2) + _txt(hx+24, hy+102, c.get("card_title2",""), 28, 800, M)
            + f'<circle cx="{hx+118}" cy="{hy+168}" r="38" fill="{LT}"/><path d="M{hx+48} {hy+204}L{hx+96} {hy+136}L{hx+150} {hy+200}Z" fill="{M}"/>'
            + f'<line x1="{hx+26}" y1="{hy+hh-18}" x2="{hx+hw-26}" y2="{hy+hh-18}" stroke="{LN}" stroke-width="2"/></g>')
    float_ = f'<g>{card}<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" keyTimes="0;0.5;1" dur="3s" begin="{TT}s" repeatCount="indefinite"/></g>'
    o.append(f_pop(hc[0], hc[1], t3, float_, 1.12))
    o.append(_gline(X0, 326, X1, 326, LT, t3+0.3, 0.4, 2, "6 7"))
    o.append(_caption(372, c.get("caption",""), th, t3+0.5))
    return o

def r_timeline(c, th, t):
    """竖向时间线：圆点 + 卡片，轮流高亮"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    items = c.get("items", [])[:4]; k = len(items); lx = X0 + 40; cx0 = X0 + 96
    top, bottom = 44, (344 if c.get("result") else 390); gap = 14
    h = (bottom - top - gap*(k-1)) / k; ys = [top + i*(h+gap) for i in range(k)]
    o.append(_gline(lx, ys[0]+h/2, lx, ys[-1]+h/2, LN, t, 0.25*k, 4))
    for i, it in enumerate(items):
        y = ys[i]; ti = t + i*0.25; cy = y + h/2
        inner = (_box(cx0, y, X1-cx0, h, BD, "#FFFFFF", 14) + _txt(cx0+28, cy-4 if it.get("desc") else cy+8, it.get("title",""), 21, 800, M)
                 + (_txt(cx0+28, cy+24, it.get("desc",""), 16, 400, "#475569") if it.get("desc") else ""))
        dot = f'<circle cx="{lx}" cy="{R(cy)}" r="10" fill="{M}"/>'
        o.append(f'<g>{_cycle(i, k)}{f_pop(lx, cy, ti+0.05, dot, 1.4)}{f_pop(cx0+(X1-cx0)/2, cy, ti, inner, 1.04)}</g>')
    if c.get("result"):
        o.append(_button(358, 38, c["result"], th, t + k*0.25 + 0.2, cx0, X1-cx0, 18))
    return o

def r_converge(c, th, t):
    """编号卡并排 → 括号汇合 → 底部大框"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    o.append(_mono((X0+X1)/2, 58, c.get("caption",""), t, "middle"))
    cards = c.get("cards", [])[:4]; n = len(cards); gap = 16; cw = (X1-X0-gap*(n-1))/n; y0, h = 74, 170
    xs = []
    for i, cd in enumerate(cards):
        x = X0 + i*(cw+gap); ti = t + 0.15 + i*0.28; xs.append(x+cw/2)
        if i: o.append(_gline(x-gap, y0+h/2, x, y0+h/2, LN, ti-0.05, 0.12))
        inner = (_box(x, y0, cw, h, BD) + _txt(x+22, y0+30, cd.get("num",""), 15, 700, GRAY2)
                 + line_icon(cd.get("icon","doc"), x+cw/2, y0+86, LN if i == 0 else M, LT, 0.95) + _txt(x+cw/2, y0+146, cd.get("label",""), 20, 800, M, "middle"))
        o.append(f_pop(x+cw/2, y0+h/2, ti, inner))
    t2 = t + 0.15 + n*0.28; by = y0 + h + 22; mid = (X0+X1)/2
    for x in xs: o.append(_gline(x, y0+h, x, by, LN, t2, 0.15))
    o.append(_gline(mid, by, xs[0], by, LN, t2+0.15, 0.25)); o.append(_gline(mid, by, xs[-1], by, LN, t2+0.15, 0.25))
    o.append(_gline(mid, by, mid, by+18, LN, t2+0.35, 0.12))
    bx_y = by + 18; t3 = t2 + 0.45
    inner = (_box(X0, bx_y, X1-X0, 392-bx_y, BD, LT, 16) + _txt(mid, bx_y+40, c.get("box_title",""), 23, 800, M, "middle")
             + _txt(mid, bx_y+72, c.get("box_sub",""), 17, 500, "#475569", "middle"))
    o.append(f_pop(mid, (bx_y+392)/2, t3, inner, 1.04))
    return o

def r_tree(c, th, t):
    """一句话 → 分叉 → 2×2 功能卡（轮流高亮）→ 按钮"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    mid = (X0+X1)/2; hw = 440
    o.append(f_pop(mid, 70, t, _box(mid-hw/2, 44, hw, 52, BD, "#FFFFFF", 26) + _txt(mid, 77, c.get("head",""), 20, 500, "#475569", "middle")))
    items = c.get("items", [])[:4]; gap = 18; cw = (X1-X0-gap)/2; ch = 88; ys = [130, 130+ch+14]
    cxs = [X0+cw/2, X0+cw+gap+cw/2]; t2 = t + 0.3
    o.append(_gline(mid, 96, mid, 112, LN, t2, 0.1))
    o.append(_gline(mid, 112, cxs[0], 112, LN, t2+0.1, 0.2)); o.append(_gline(mid, 112, cxs[1], 112, LN, t2+0.1, 0.2))
    o.append(_gline(cxs[0], 112, cxs[0], 130, LN, t2+0.3, 0.1)); o.append(_gline(cxs[1], 112, cxs[1], 130, LN, t2+0.3, 0.1))
    for i, it in enumerate(items):
        r, ci = divmod(i, 2); x = X0 + ci*(cw+gap); y = ys[r]; ti = t2 + 0.4 + i*0.15
        inner = (_box(x, y, cw, ch, BD, "#FFFFFF", 14) + line_icon(it.get("icon","spark"), x+46, y+ch/2, LN, LT, 0.62)
                 + _txt(x+86, y+38, it.get("title",""), 20, 800, M) + _txt(x+86, y+66, it.get("desc",""), 15, 400, GRAY))
        o.append(f'<g>{_cycle(i, len(items))}{f_pop(x+cw/2, y+ch/2, ti, inner, 1.05)}</g>')
    o.append(_button(338, 54, c.get("result",""), th, t2 + 0.5 + len(items)*0.15, size=19))
    return o

def r_compare(c, th, t):
    """同一题目 → 多家结果并排（轮流高亮）→ 结论按钮"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    o.append(_mono(X0, 56, c.get("caption",""), t))
    mid = (X0+X1)/2
    o.append(f_pop(mid, 98, t+0.1, _box(X0, 72, X1-X0, 52, BD, LT, 14) + _txt(mid, 105, c.get("head",""), 20, 800, M, "middle", 2), 1.04))
    items = c.get("items", [])[:4]; n = len(items); gap = 22; cw = (X1-X0-gap*(n-1))/n; y0, h = 150, 132
    cxs = [X0 + i*(cw+gap) + cw/2 for i in range(n)]; t2 = t + 0.4
    o.append(_gline(mid, 124, mid, 138, LN, t2, 0.1))
    o.append(_gline(mid, 138, cxs[0], 138, LN, t2+0.1, 0.2)); o.append(_gline(mid, 138, cxs[-1], 138, LN, t2+0.1, 0.2))
    for x in cxs: o.append(_gline(x, 138, x, y0, LN, t2+0.3, 0.08))
    for i, it in enumerate(items):
        x = X0 + i*(cw+gap); ti = t2 + 0.4 + i*0.2
        inner = _box(x, y0, cw, h, BD) + line_icon(it.get("icon","web"), x+cw/2, y0+52, LN, LT, 0.95) + _txt(x+cw/2, y0+108, it.get("label",""), 19, 800, "#334155", "middle")
        o.append(f'<g>{_cycle(i, n)}{f_pop(x+cw/2, y0+h/2, ti, inner)}</g>')
    o.append(_button(306, 66, c.get("result",""), th, t2 + 0.5 + n*0.2))
    return o

def r_storyboard(c, th, t):
    """一个角色 → 分镜（全景/中景/特写，取景框扫过）→ 流程按钮"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    o.append(_mono(X0, 56, c.get("caption",""), t))
    who = c.get("who", {}); wx, wy, ww, wh = X0, 72, 152, 186
    if who.get("avatar"):
        art = f'<image x="{wx+18}" y="{wy+18}" width="{ww-36}" height="120" preserveAspectRatio="xMidYMax meet" href="GIF_URL_HERE"/>'
    else:
        art = line_icon(who.get("icon","person"), wx+ww/2, wy+78, M, LT, 1.2)
    o.append(f_pop(wx+ww/2, wy+wh/2, t+0.1, _box(wx, wy, ww, wh, BD) + f'<rect x="{wx+16}" y="{wy+16}" width="{ww-32}" height="124" rx="10" fill="{LT}" opacity=".6"/>' + art
                   + _txt(wx+ww/2, wy+wh-18, who.get("label",""), 19, 800, "#1F2937", "middle")))
    o.append(_arrow(wx+ww+12, wx+ww+48, wy+wh/2, LN, t+0.4))
    px = wx + ww + 60; pw = X1 - px; t2 = t + 0.55
    o.append(f_pop(px+pw/2, wy+wh/2, t2, _box(px, wy, pw, wh, BD) + f'<line x1="{px+18}" y1="{wy+20}" x2="{X1-18}" y2="{wy+20}" stroke="{LT}" stroke-width="6" stroke-dasharray="18 12"/>', 1.03))
    shots = c.get("shots", [])[:3]; n = max(len(shots), 1); g = 14; sw = (pw - 36 - g*(n-1)) / n; sy, sh = wy+38, 104
    for i, sh_ in enumerate(shots):
        x = px + 18 + i*(sw+g); ti = t2 + 0.3 + i*0.22
        o.append(f_pop(x+sw/2, sy+sh/2, ti, f'<rect x="{R(x)}" y="{sy}" width="{R(sw)}" height="{sh}" rx="8" fill="{LT}" opacity=".7"/>'
                       + line_icon(sh_.get("icon","image"), x+sw/2, sy+sh/2, M, LT, 0.9) + _txt(x+sw/2, sy+sh+30, sh_.get("label",""), 16, 500, GRAY, "middle")))
    fr = (f'<rect x="{R(px+16)}" y="{sy-3}" width="{R(sw+4)}" height="{sh+6}" rx="10" fill="none" stroke="{M}" stroke-width="3">'
          + (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{R(sw+g)} 0;{R(sw+g)} 0;{R(2*(sw+g))} 0;{R(2*(sw+g))} 0;0 0" keyTimes="0;0.25;0.33;0.58;0.66;0.92;1" dur="4.5s" begin="{TT}s" repeatCount="indefinite"/>' if n == 3 else "") + '</rect>')
    o.append(f'<g opacity="0">{F("opacity",[0,0,1,1],[0,TT-0.3,TT,TT])}{fr}</g>')
    t3 = t2 + 0.4 + n*0.22; by, bh = 296, 66
    flow = c.get("flow", [])
    spans = "".join(f'<tspan fill-opacity="0">{F("fill-opacity",[0,0,1,1],[0,t3+0.3+0.18*i,t3+0.5+0.18*i,TT])}{esc((" → " if i else "") + seg)}</tspan>' for i, seg in enumerate(flow))
    o.append(f_pop((X0+X1)/2, by+bh/2, t3, f'<rect x="{X0}" y="{by}" width="{X1-X0}" height="{bh}" rx="16" fill="{M}"/><circle cx="{X0+38}" cy="{by+bh/2}" r="6" fill="#FFFFFF" opacity=".6"/>'
                   f'<text x="{X0+64}" y="{by+bh/2+8}" font-size="22" font-weight="800" fill="#FFFFFF" xml:space="preserve">{spans}</text>', 1.04))
    return o

def r_chat(c, th, t):
    """聊天窗口里来回几句 → 弹出交付卡"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    msgs = c.get("messages", [])[:4]; nai = sum(1 for m in msgs if m.get("from") != "me")
    wx, ww = X0, 372; wh = 58 + len(msgs)*54; wy = 46 + (270 - wh)/2
    o.append(f_pop(wx+ww/2, wy+wh/2, t, _box(wx, wy, ww, wh, BD) + "".join(f'<circle cx="{wx+20+i*12}" cy="{wy+20}" r="4" fill="#CBD5E1"/>' for i in range(3))
                   + (_txt(wx+ww/2, wy+25, c["window_title"], 14, 600, GRAY2, "middle") if c.get("window_title") else ""), 1.03))
    y = wy + 44; tt = t + 0.3
    for m in msgs:
        s = m.get("text",""); bw = tw(s, 16) + 32; bh = 38
        if m.get("from") == "me":
            bx = wx + ww - 18 - bw
            o.append(f_pop(bx+bw, y+bh/2, tt, f'<rect x="{R(bx)}" y="{y}" width="{R(bw)}" height="{bh}" rx="19" fill="{M}"/>' + _txt(bx+16, y+25, s, 16, 600, "#FFFFFF"), 1.06)); tt += 0.32
        else:
            bx = wx + 18
            dots = "".join(f'<circle cx="{bx+18+i*11}" cy="{y+bh/2}" r="3.5" fill="{LN}"/>' for i in range(3))
            o.append(f'<g opacity="0">{F("opacity",[0,0,1,1,0,0],[0,tt,tt+0.05,tt+0.3,tt+0.35,TT])}<rect x="{bx}" y="{y}" width="58" height="{bh}" rx="19" fill="{LT}"/>{dots}</g>'); tt += 0.32
            o.append(f_pop(bx, y+bh/2, tt, f'<rect x="{R(bx)}" y="{y}" width="{R(bw)}" height="{bh}" rx="19" fill="{LT}"/>' + _txt(bx+16, y+25, s, 16, 600, "#1E293B"), 1.06)); tt += 0.32
        y += bh + 16
    o.append(_arrow(wx+ww+12, wx+ww+50, 181, LN, tt))
    rx = wx + ww + 62; rw = X1 - rx; ry, rh = 66, 230; tt += 0.25
    inner = (_box(rx, ry, rw, rh, M, "#FFFFFF", 16, 3) + f'<rect x="{rx+20}" y="{ry+20}" width="{rw-40}" height="96" rx="10" fill="{LT}"/>'
             + line_icon(c.get("result_icon","doc"), rx+rw/2, ry+68, M, LT, 0.85)
             + _txt(rx+rw/2, ry+156, c.get("result_title",""), 22, 800, M, "middle") + _txt(rx+rw/2, ry+188, c.get("result_sub",""), 16, 500, GRAY, "middle"))
    o.append(f_pop(rx+rw/2, ry+rh/2, tt, inner, 1.08))
    o.append(_caption(368, c.get("caption",""), th, tt+0.3))
    return o

def r_stats(c, th, t):
    """2–3 个大数字，下划线长出来 → 结论按钮"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    o.append(_mono(X0, 56, c.get("caption",""), t))
    items = c.get("items", [])[:3]; n = len(items); gap = 40; cw = (X1-X0-gap*(n-1))/n; y0, h = 72, 196
    for i, it in enumerate(items):
        x = X0 + i*(cw+gap); ti = t + 0.15 + i*0.35; cx = x + cw/2
        hl = it.get("hl", i == n-1)
        inner = (_box(x, y0, cw, h, M if hl else BD, LT if hl else "#FFFFFF", 18, 3 if hl else 2)
                 + _txt(cx, y0+48, it.get("label",""), 17, 700, "#475569", "middle")
                 + _txt(cx, y0+122, it.get("value",""), 52, 800, M if hl else "#334155", "middle")
                 + _txt(cx, y0+170, it.get("note",""), 15, 400, GRAY2, "middle"))
        if i: o.append(f'<g opacity="0">{f_in(ti-0.1)}{_txt(x-gap/2, y0+h/2+10, "→", 26, 800, LN, "middle")}</g>')
        o.append(f_pop(cx, y0+h/2, ti, inner, 1.08))
        o.append(f'<rect x="{R(cx-50)}" y="{y0+136}" width="0" height="5" rx="2.5" fill="{M if hl else LN}">{F("width",[0,0,100,100],[0,ti+0.3,ti+0.6,TT])}</rect>')
    o.append(_button(300, 64, c.get("result",""), th, t + 0.3 + n*0.35))
    return o

def r_checklist(c, th, t):
    """待办清单逐项打勾，进度条走满"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    items = c.get("items", [])[:5]; n = len(items); x, w = X0, X1-X0; rowh = 40; h = 74 + n*rowh + 34; y = max(44, (CH - h - 60)/2)
    o.append(f_pop(x+w/2, y+h/2, t, _box(x, y, w, h, BD) + _txt(x+26, y+40, c.get("title",""), 21, 800, INK2)
                   + f'<rect x="{x+26}" y="{y+h-28}" width="{w-52}" height="8" rx="4" fill="{LT}"/>', 1.03))
    tt = t + 0.35; step = min(0.35, 1.8 / max(n, 1))
    for i, s in enumerate(items):
        ry = y + 66 + i*rowh; ti = tt + i*step
        o.append(f'<g opacity="0">{f_in(ti-0.15)}<rect x="{x+26}" y="{ry}" width="24" height="24" rx="6" fill="#FFFFFF" stroke="{LN}" stroke-width="2"/>{_txt(x+64, ry+19, s, 18, 500, "#334155")}</g>')
        o.append(f_pop(x+38, ry+12, ti+0.1, f'<rect x="{x+26}" y="{ry}" width="24" height="24" rx="6" fill="{M}"/><path d="M{x+32} {ry+12}l5 5l9 -10" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>', 1.3))
    pw = w - 52
    o.append(f'<rect x="{x+26}" y="{y+h-28}" width="0" height="8" rx="4" fill="{M}">{F("width",[0,0,pw,pw],[0,tt,tt+n*step+0.2,TT])}</rect>')
    o.append(f'<g opacity="0">{f_in(tt+n*step)}{_txt(x+w-26, y+40, c.get("done", f"{n}/{n} 完成"), 17, 800, M, "end")}</g>')
    o.append(_caption(y+h+44, c.get("caption",""), th, tt+n*step+0.2))
    return o

def r_terminal(c, th, t):
    """深色终端：命令一行行出现，最后亮绿勾"""
    M, LT, LN, BD = th["main"], th["light"], th["line"], th["border"]; o = []
    lines = c.get("lines", [])[:6]; x, w = X0, X1-X0; h = 70 + (len(lines)+1)*34; y = max(44, (CH - h - 60)/2)
    o.append(f_pop(x+w/2, y+h/2, t, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#0F172A"/>'
                   + "".join(f'<circle cx="{x+22+i*16}" cy="{y+22}" r="5" fill="{col}"/>' for i, col in enumerate(["#F87171", "#FBBF24", "#34D399"]))
                   + _txt(x+w/2, y+27, c.get("title",""), 14, 600, "#64748B", "middle"), 1.03))
    cols = {"cmd": "#E2E8F0", "out": "#94A3B8", "ok": "#34D399"}
    ly = y + 70; tt = t + 0.35; last = None
    for ln in lines:
        typ = ln.get("type", "out"); s = ln.get("text", "")
        pre = "$ " if typ == "cmd" else ("✓ " if typ == "ok" else "  ")
        o.append(f'<g opacity="0">{f_in(tt, 0.12)}<text x="{x+28}" y="{ly}" font-size="17" font-weight="{700 if typ != "out" else 400}" fill="{cols[typ]}" font-family="Menlo,Consolas,monospace" xml:space="preserve">'
                 f'<tspan fill="{LN}">{esc(pre)}</tspan>{esc(s)}</text></g>')
        last = (ly, tw(pre + s, 17) * 0.62 + 6); ly += 34; tt += 0.4 if typ == "cmd" else 0.22
    o.append(f'<g opacity="0">{F("opacity",[0,0,1,1],[0,tt,tt+0.05,TT])}<text x="{x+28}" y="{ly}" font-size="17" font-weight="700" fill="{LN}" font-family="Menlo,Consolas,monospace">$</text>'
             f'<rect x="{x+46}" y="{ly-15}" width="10" height="19" fill="#E2E8F0"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{TT}s" repeatCount="indefinite"/></rect></g>')
    o.append(_caption(y+h+44, c.get("caption",""), th, tt+0.1))
    return o

RIGHTS = {"steps": r_steps, "remix": r_remix, "pick": r_pick, "timeline": r_timeline, "converge": r_converge, "tree": r_tree,
          "compare": r_compare, "storyboard": r_storyboard, "chat": r_chat, "stats": r_stats, "checklist": r_checklist, "terminal": r_terminal}

def build_card(spec):
    c = spec["card"]; th = THEMES.get(c.get("theme", "blue"), THEMES["blue"])
    M, LT, LN, BD, BG = th["main"], th["light"], th["line"], th["border"], th["bg"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CW} {CH}" width="100%" style="display:block;width:100%;height:auto;max-width:{CW}px;margin:0 auto;background:transparent;font-family:\'PingFang SC\',\'Helvetica Neue\',sans-serif">']
    o.append(f_pop(CW/2, CH/2, 0, f'<rect x="10" y="10" width="{CW-20}" height="{CH-20}" rx="34" fill="{BG}" stroke="{BD}" stroke-width="2"/>', 1.01))
    L = 70
    dot = (f'<circle cx="{L+8}" cy="62" r="6" fill="{M}"/>'
           f'<circle cx="{L+8}" cy="62" r="6" fill="none" stroke="{M}" stroke-width="2" opacity="0">'
           f'<animate attributeName="r" values="6;16;16" keyTimes="0;0.5;1" dur="2.4s" begin="{TT}s" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values="0.6;0;0" keyTimes="0;0.5;1" dur="2.4s" begin="{TT}s" repeatCount="indefinite"/></circle>')
    o.append(f'<g opacity="0">{f_in(0.25)}{dot}<text x="{L+28}" y="69" font-size="17" font-weight="700" letter-spacing="1" fill="{M}">{esc(c.get("eyebrow",""))}</text></g>')
    o.append(f_rise(0.4, f'<text x="{L}" y="150" font-size="46" font-weight="800" fill="{INK2}">{esc(c.get("title1",""))}</text>'))
    o.append(f_rise(0.6, f'<text x="{L}" y="218" font-size="46" font-weight="800" fill="{M}">{esc(c.get("title2",""))}</text>'))
    o.append(f'<rect x="{L}" y="250" width="0" height="7" rx="3.5" fill="{M}">{F("width",[0,0,90,90],[0,0.85,1.2,TT],["0 0 1 1",EASE,"0 0 1 1"])}</rect>')
    o.append(f_rise(1.0, f'<text x="{L}" y="302" font-size="21" fill="{GRAY}">{esc(c.get("sub",""))}</text>', 10))
    if c.get("avatar", True):
        o.append(f_pop(L+36, 356, 1.2, f'<circle cx="{L+36}" cy="358" r="34" fill="{LT}"/><image x="{L-6}" y="314" width="84" height="80" preserveAspectRatio="xMidYMax meet" href="GIF_URL_HERE"/>'))
        o.append(f_rise(1.35, f'<text x="{L+86}" y="352" font-size="18" font-weight="700" fill="#1F2937">{esc(c.get("author","林月半子的AI笔记"))}</text>'
                              f'<text x="{L+86}" y="378" font-size="14" fill="#9CA3AF">{esc(c.get("slogan","我是林月半子，教你用AI干掉90%的重复劳动"))}</text>', 8))
    else:
        o.append(f_rise(1.2, f'<text x="{L}" y="372" font-size="15" letter-spacing="1" fill="#9CA3AF">{esc(c.get("foot", c.get("eyebrow","")))}</text>', 8))
    o.append(f'<line x1="548" y1="72" x2="548" y2="72" stroke="{LT}" stroke-width="2">{F("y2",[72,72,372,372],[0,0.5,1.0,TT],["0 0 1 1",EASE,"0 0 1 1"])}</line>')
    o += RIGHTS[c.get("right", "steps")](c, th, 1.1)
    o.append('</svg>')
    return "".join(o)

# ================= 风格三/四：大字海报（poster）和潮酷（neo）=================
# 按手机可读设计：一条横幅只放 2–3 个元素，最小的字也有 30px（手机上约 9px）
def _pw(t, size): return sum(size if ord(c) > 255 else size * 0.58 for c in str(t))
def _fit(t, size, maxw): return int(min(size, size * maxw / max(_pw(t, size), 1)))
def _pt(x, y, t, size, fill, w=800, anchor="start", extra=""):
    return f'<text x="{R(x)}" y="{R(y)}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(str(t))}</text>'
def _pcheck(cx, cy, r=28):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}" stroke="#FFFFFF" stroke-width="5"/>'
            f'<path d="M{R(cx-r*0.42)} {cy}l{R(r*0.3)} {R(r*0.32)}l{R(r*0.56)} {R(-r*0.6)}" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')

def build_poster(spec, neo=False):
    c = spec.get("poster") or spec.get("card") or {}
    th = THEMES.get(c.get("theme", "orange"), THEMES["orange"])
    M, LT, LN, BG = th["main"], th["light"], th["line"], th["bg"]
    K = "#111827"; H_ = 484 if neo else 460
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CW} {H_}" width="100%" style="display:block;width:100%;height:auto;max-width:{CW}px;margin:0 auto;background:transparent;font-family:\'PingFang SC\',\'Helvetica Neue\',sans-serif">']
    def panel(x, y, w, h, fill, rot=0, rx=30):
        """右栏的块：海报是圆角浅色块，潮酷是黑描边 + 错位投影 + 微微歪着"""
        if not neo: return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{LT if fill != M else M}" stroke-width="3"/>', ""
        sh = "".join(f'<rect x="{x+4-k*2}" y="{y+8+k*4}" width="{w-8+k*4}" height="{h}" rx="{rx}" fill="#0F172A" opacity="0.035"/>' for k in range(3))   # 三层淡色叠出柔和阴影
        return sh + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{M if fill == M else LT}" stroke-width="2"/>', ""
    t1, t2 = c.get("title1", ""), c.get("title2", ""); eb = c.get("eyebrow", "")
    if neo:
        big = str(c.get("big", ""))
        o.append("".join(f'<rect x="{14-k*3}" y="{14+k*5}" width="{CW-28+k*6}" height="{H_-36}" rx="40" fill="#0F172A" opacity="0.03"/>' for k in range(3))
                 + f'<rect x="8" y="3" width="{CW-16}" height="{H_-30}" rx="38" fill="#FFFFFF" stroke="{LT}" stroke-width="2.5"/>')
        if big: o.append(f'<text x="{CW-64}" y="{H_-62}" font-size="{_fit(big, 300, 500)}" font-weight="900" font-style="italic" fill="{LT}" opacity="0.5" text-anchor="end" font-family="Helvetica,Arial,sans-serif" letter-spacing="-10">{esc(big)}</text>')
        ew = _pw(eb, 30) + len(eb) * 3 + 86
        o.append(f'<rect x="60" y="48" width="{R(ew)}" height="58" rx="29" fill="{K}"/><circle cx="92" cy="77" r="7" fill="{M}"/>' + _pt(60 + ew / 2 + 12, 88, eb, 30, "#FFFFFF", 800, "middle", ' letter-spacing="3"'))
        fs = min(_fit(t1, 82, 640), _fit(t2, 80, 590))
        o.append(_pt(60, 210, t1, fs, K, 900))
        sw = _pw(t2, fs) + 48
        o.append(f_rise(0.3, f'<rect x="56" y="240" width="{R(sw)}" height="108" rx="20" fill="{M}"/>' + _pt(80, 294 + fs * 0.34, t2, fs, "#FFFFFF", 900), 24))
        ay = 404
    else:
        o.append(f'<rect x="2" y="2" width="{CW-4}" height="{H_-4}" rx="40" fill="{BG}" stroke="{LT}" stroke-width="3"/>')
        o.append(f'<circle cx="76" cy="76" r="10" fill="{M}"><animate attributeName="r" values="10;14;10" dur="2s" repeatCount="indefinite"/></circle>' + _pt(100, 88, eb, 32, M, 800, "start", ' letter-spacing="3"'))
        fs = min(_fit(t1, 80, 640), _fit(t2, 80, 640))
        o.append(_pt(60, 196, t1, fs, K, 900)); o.append(f_rise(0.3, _pt(60, 300, t2, fs, M, 900), 20))
        o.append(f'<rect x="64" y="330" width="0" height="12" rx="6" fill="{M}">{F("width", [0, 0, 110, 110], [0, 0.6, 1.0, TT], ["0 0 1 1", EASE, "0 0 1 1"])}</rect>')
        ay = 404
    if c.get("avatar", True):
        o.append(f'<circle cx="96" cy="{ay}" r="34" fill="{LT}"' + f'/><image x="54" y="{ay-44}" width="84" height="80" preserveAspectRatio="xMidYMax meet" href="GIF_URL_HERE"/>'
                 + _pt(146, ay + 12, c.get("author", "林月半子的AI笔记"), 33, K, 900 if neo else 800))
    # ---- 右栏 ----
    X, W = 770, 400; top = 60 if neo else 56; r = c.get("right") or ("tags" if neo and c.get("tags") else "flow")
    if r == "tags":
        tags = (c.get("tags") or [])[:3]; rots = [-5, 4, -3]; gap = (H_ - 100 - len(tags) * 88) / max(len(tags) - 1, 1) if len(tags) > 1 else 0
        for i, tg in enumerate(tags):
            y = 50 + i * (88 + min(gap, 40)) + (0 if len(tags) == 3 else 60); hl = i == 1 or len(tags) == 1
            x = X + 40; w = 320
            a, b = panel(x, y, w, 88, M if hl else "#FFFFFF", rots[i % 3], 44)
            o.append(f_pop(x + w / 2, y + 44, 0.9 + i * 0.3, a + _pt(x + w / 2, y + 44 + 15, tg, _fit(tg, 42, w - 50), "#FFFFFF" if hl else K, 900, "middle") + b))
    elif r == "stat":
        a, b = panel(X, top + 20, W, H_ - 2 * top - 50, "#FFFFFF", -2)
        v = str(c.get("value", "")); cy = H_ / 2
        o.append(f_pop(X + W / 2, cy, 0.9, a + _pt(X + W / 2, cy - 78, c.get("label", ""), 34, GRAY, 700, "middle")
                       + _pt(X + W / 2, cy + 44, v, _fit(v, 120, W - 60), M, 900, "middle") + _pt(X + W / 2, cy + 104, c.get("note", ""), 30, K, 700, "middle") + b))
    elif r == "steps":
        st_ = (c.get("steps") or [])[:3]; hh = 92; y0 = (H_ - (len(st_) * hh + (len(st_) - 1) * 18)) / 2 - (6 if neo else 0)
        for i, tx in enumerate(st_):
            y = y0 + i * (hh + 18); last = i == len(st_) - 1
            a, b = panel(X, round(y), W, hh, M if last else "#FFFFFF", (-2, 2, -1)[i % 3])
            o.append(f_rise(0.9 + i * 0.35, a + f'<circle cx="{X+52}" cy="{R(y+hh/2)}" r="26" fill="{"#FFFFFF" if last else M}"/>'
                            + _pt(X + 52, y + hh / 2 + 11, i + 1, 30, M if last else "#FFFFFF", 900, "middle")
                            + _pt(X + 96, y + hh / 2 + 14, tx, _fit(tx, 38, W - 120), "#FFFFFF" if last else K, 800) + b, 22))
    else:   # flow：一句话 → 结果
        ask, res, sub = c.get("ask", ""), c.get("result", ""), c.get("result_sub", "")
        a, b = panel(X, top, W, 116, "#FFFFFF", -3)
        tail = "" if neo else f'<path d="M{X+330} {top+114}l40 40l-4 -42z" fill="#FFFFFF" stroke="{LT}" stroke-width="3"/><rect x="{X+320}" y="{top+104}" width="60" height="12" fill="#FFFFFF"/>'
        o.append(f_rise(0.9, a + tail + _pt(X + W / 2, top + 74, ask, _fit(ask, 44, W - 50), K, 800, "middle") + b, 22))
        o.append(f_rise(1.5, f'<path d="M{X+W/2} {top+142}v52m-18 -20l18 22l18 -22" fill="none" stroke="{M}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>', -14, 0.3))
        y2 = top + 214; a, b = panel(X, y2, W, 140, M, 2)
        ic = f'<circle cx="{X+80}" cy="{y2+70}" r="42" fill="#FFFFFF"/><path d="M{X+66} {y2+46}v48l40 -24z" fill="{M}"/>'
        o.append(f_rise(1.9, a + ic + _pt(X + 146, y2 + (60 if sub else 86), res, _fit(res, 46, W - 170), "#FFFFFF", 900)
                        + (f'<text x="{X+146}" y="{y2+106}" font-size="{_fit(sub, 30, W-170)}" font-weight="500" fill="#FFFFFF" opacity="0.88">{esc(sub)}</text>' if sub else "") + b, 26))
        o.append(f_pop(X + W - 8, y2 + 6, 2.4, _pcheck(X + W - 8, y2 + 6, 30)))
    o.append('</svg>')
    return "".join(o)

def build(spec):
    if spec.get("style") in ("poster", "neo"):
        return build_poster(spec, spec["style"] == "neo")
    if spec.get("style") == "card":
        return build_card(spec)
    o = head()
    sc = spec["scene"]
    o.append(f'<g opacity="0">{A("opacity",[0,0,1,1,0,0],[0,2.3,2.4,6.7,6.9,D])}')
    o += LAYOUTS[sc["layout"]](sc)
    if spec.get("caption"):
        o.append(label(1236, 22, spec["caption"], T0+0.3, "end", 12))
    o.append('</g></svg>')
    return "".join(o)

PAGE = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>__TITLE__ · 复制到公众号</title>
<style>
body{margin:0;background:#EEE;font-family:'PingFang SC',sans-serif;color:#222}
.wrap{max-width:1300px;margin:0 auto;padding:24px 20px}
h1{font-size:22px;margin:0 0 6px} ol{margin:6px 0 16px;padding-left:20px;line-height:1.8;font-size:14px;color:#555}
.card{background:#fff;border-radius:12px;padding:18px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
label{font-size:13px;color:#555} input[type=text]{flex:1;min-width:320px;padding:10px;border:1.5px solid #ccc;border-radius:8px;font-size:14px}
button{border:0;background:#C9643E;color:#fff;padding:10px 16px;border-radius:8px;font-size:14px;cursor:pointer}
button.ghost{background:#fff;color:#C9643E;border:1.5px solid #C9643E}
.msg{font-size:14px;margin:4px 0 10px} .ok{color:#2F9E5A} .err{color:#C9643E;font-weight:700}
.preview{background:#F7F7F7;border-radius:8px;padding:8px}
.variant{margin:14px 0 22px} .vhead{display:flex;gap:10px;align-items:center;margin-bottom:8px} .vhead b{font-size:15px;min-width:64px}
#manual{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center}
#manual>div{background:#fff;border-radius:12px;padding:18px;width:min(720px,90vw)} #manual textarea{width:100%;height:220px;font-size:12px;box-sizing:border-box}
</style></head><body><div class="wrap">
<h1>__TITLE__</h1>
<ol><li>头像 GIF 地址填一次就会记住（公众号编辑器里插入 GIF → 右键「复制图片地址」，以 https://mmbiz.qpic.cn/ 开头）</li>
<li>可选：选一个本地 GIF，只用于这里的预览，不会被复制出去</li>
<li>点「复制到公众号」，回到公众号编辑器空行里粘贴，保存后发预览到手机确认</li></ol>
<div class="card">
<div class="row"><label for="gif">头像 GIF 地址</label><input type="text" id="gif" placeholder="https://mmbiz.qpic.cn/mmbiz_gif/…"></div>
<div class="row"><label for="local">本地预览 GIF</label><input type="file" id="local" accept="image/gif,image/png,image/jpeg"></div>
<div class="msg" id="m"></div>
<div id="list"></div>
</div></div>
<div id="manual"><div><b>浏览器没让我写剪贴板，请手动复制</b><p style="font-size:13px;color:#666;margin:6px 0 10px">源码已全选，按 ⌘C / Ctrl+C，然后贴进 mdnice 等能粘贴 HTML 的编辑器。</p><textarea readonly></textarea><p style="text-align:right;margin:10px 0 0"><button onclick="document.getElementById('manual').style.display='none'">关闭</button></p></div></div>
<script>
const V=__VARIANTS__;
const G=document.getElementById('gif'),L=document.getElementById('local');
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
G.value=ls('lq_banner_gif')||'';
let local=ls('lq_banner_gif_local')||'';
function esc(u){return u.replace(/&/g,'&amp;').replace(/"/g,'&quot;')}
function render(){const u=esc(local||G.value.trim()||'');document.getElementById('list').innerHTML=V.map((v,i)=>'<div class="variant"><div class="vhead"><b>'+v.label+'</b><button onclick="copyRich(this,'+i+')">'+(V.length>1?'复制这个到公众号':'复制到公众号')+'</button><button class="ghost" onclick="copySrc(this,'+i+')">复制源码</button></div><div class="preview">'+v.svg.split('GIF_URL_HERE').join(u)+'</div></div>').join('')}
G.addEventListener('input',()=>{ls('lq_banner_gif',G.value.trim());render()});
L.addEventListener('change',()=>{const f=L.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{local=r.result;ls('lq_banner_gif_local',local);render()};r.readAsDataURL(f)});
render();
function msg(t,ok){const m=document.getElementById('m');m.textContent=t;m.className='msg '+(ok?'ok':'err')}
function flash(b,t){const o=b.dataset.l||b.textContent;b.dataset.l=o;b.textContent=t;setTimeout(()=>b.textContent=o,1800)}
function fill(i){const SVG=V[i].svg;if(SVG.indexOf('GIF_URL_HERE')<0)return SVG;const u=G.value.trim();
  if(!u){msg('先填头像 GIF 的公众号图片地址，再点复制',false);G.focus();return null}
  if(!/^https:\/\/mmbiz\.qpic\.cn\//.test(u)){msg('地址要以 https://mmbiz.qpic.cn/ 开头（公众号图库里的图）',false);G.focus();return null}
  return SVG.split('GIF_URL_HERE').join(esc(u))}
function legacy(h,p){let d=false;const f=e=>{e.clipboardData.setData('text/html',h);e.clipboardData.setData('text/plain',p);e.preventDefault();d=true};
  document.addEventListener('copy',f);let ok=false;try{ok=document.execCommand('copy')}catch(e){}document.removeEventListener('copy',f);return ok&&d}
async function put(h,p){if(legacy(h,p))return true;
  try{if(navigator.clipboard&&window.ClipboardItem){await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([h],{type:'text/html'}),'text/plain':new Blob([p],{type:'text/plain'})})]);return true}}catch(e){}return false}
function manual(p){const d=document.getElementById('manual');const t=d.querySelector('textarea');t.value=p;d.style.display='flex';t.focus();t.select()}
async function copyRich(b,i){const s=fill(i);if(s===null)return;const h='<section style="margin:0 auto;max-width:1246px">'+s+'</section>';
  if(await put(h,s)){flash(b,'已复制 ✓');msg('已复制，去公众号编辑器里粘贴',true)}else{msg('这个窗口不允许写剪贴板：请用 Chrome 直接打开本文件，或在弹出框里手动复制',false);manual(s)}}
async function copySrc(b,i){const s=fill(i);if(s===null)return;if(await put(s,s)){flash(b,'已复制 ✓');msg('源码已复制',true)}else manual(s)}
</script></body></html>"""


# ---------------- 文字自查（代替截图）----------------
def _w(t): return sum(1 if ord(c) > 255 else 0.5 for c in str(t))
def check_spec(spec, svgs):
    """查字数、数量超限和公众号会吞掉的写法。返回问题列表，空 = 通过"""
    out = []
    def lim(v, n, what):
        if v is not None and _w(v) > n: out.append(f"{what}「{v}」有 {_w(v):g} 个字宽，超过 {n}，会挤出去或重叠，缩短一点")
    def cnt(v, lo, hi, what):
        if v is not None and not (lo <= len(v) <= hi): out.append(f"{what} 有 {len(v)} 个，要在 {lo}–{hi} 个之间，多出来的会画不下")
    if spec.get("style") in ("poster", "neo"):
        c = spec.get("poster", {}); r = c.get("right") or ("tags" if spec["style"] == "neo" and c.get("tags") else "flow")
        lim(c.get("eyebrow"), 10, "眉标 eyebrow"); lim(c.get("title1"), 8, "标题第一行"); lim(c.get("title2"), 8, "标题第二行"); lim(c.get("big"), 2, "底纹大字 big")
        if r not in ("flow", "tags", "stat", "steps"): out.append(f"没有「{r}」这个右栏，可选：flow、tags、stat、steps")
        if r == "flow":
            for k, n in (("ask", 9), ("result", 6), ("result_sub", 9)): lim(c.get(k), n, k)
            if not c.get("ask") or not c.get("result"): out.append("flow 右栏要写 ask（你说的一句话）和 result（得到的结果）")
        if r == "tags":
            cnt(c.get("tags") or [], 2, 3, "tags")
            for x in c.get("tags") or []: lim(x, 6, "贴纸")
        if r == "steps":
            cnt(c.get("steps") or [], 2, 3, "steps")
            for x in c.get("steps") or []: lim(x, 8, "步骤")
        if r == "stat": lim(c.get("value"), 5, "大数字 value"); lim(c.get("label"), 10, "label"); lim(c.get("note"), 12, "note")
    elif spec.get("style") == "card":
        c = spec.get("card", {}); r = c.get("right", "steps")
        lim(c.get("eyebrow"), 15, "眉标 eyebrow"); lim(c.get("title1"), 9, "标题第一行"); lim(c.get("title2"), 9, "标题第二行"); lim(c.get("sub"), 20, "副标题")
        if r not in RIGHTS: out.append(f"没有「{r}」这个右栏版式，可选：{'、'.join(RIGHTS)}")
        for k in ("caption", "result", "result_title", "result_sub", "head", "box_title", "box_sub", "pick_label", "grid_label"):
            lim(c.get(k), 18, k)
        for k, (lo, hi) in {"steps": (2, 4), "items": (2, 5), "cards": (2, 4), "shots": (3, 3), "messages": (1, 4), "lines": (1, 6)}.items():
            if k in c: cnt(c[k], lo, hi, k)
        for it in (c.get("steps") or []) + (c.get("cards") or []) + (c.get("shots") or []) + [x for x in (c.get("items") or []) if isinstance(x, dict)]:
            lim(it.get("label"), 8, "卡片标题"); lim(it.get("title"), 8, "卡片标题"); lim(it.get("desc"), 14, "卡片描述"); lim(it.get("sub"), 14, "卡片描述")
        for m in c.get("messages") or []: lim(m.get("text"), 12, "聊天气泡")
        for l in c.get("lines") or []: lim(l.get("text"), 17, "终端一行")
        if r == "checklist":
            for x in c.get("items") or []: lim(x, 14, "清单一项")
    else:
        sc = spec.get("scene", {}); lay = sc.get("layout", "")
        if lay not in LAYOUTS: out.append(f"没有「{lay}」这个场景模板，可选：{'、'.join(LAYOUTS)}"); return out
        lim(spec.get("caption"), 14, "右上角 caption")
        caps = {"pipeline": ("items", 1, 5 if sc.get("tile") == "card" or not sc.get("source") else 4), "path": ("nodes", 3, 5), "fly": ("items", 0, 4),
                "before_after": ("items", 1, 4), "hub": ("nodes", 2, 6), "stack": ("blocks", 2, 6), "dialog": ("items", 0, 3),
                "calendar": ("days", 3, 7), "funnel": ("items", 1, 3), "chart": ("bars", 2, 6)}
        if lay in caps and caps[lay][0] in sc: cnt(sc[caps[lay][0]], caps[lay][1], caps[lay][2], caps[lay][0])
        if lay == "pipeline" and sc.get("tile") == "film": cnt(sc.get("items") or [], 1, 4, "胶片帧 items")
        if lay == "before_after": cnt(sc.get("before") or [], 1, 7, "before")
        if lay == "funnel": cnt(sc.get("inputs") or [], 1, 10, "inputs"); lim(sc.get("filter_label"), 5, "filter_label")
        if lay == "dialog":
            cnt(sc.get("messages") or [], 1, 4, "messages")
            for m in sc.get("messages") or []: lim(m.get("text"), 12, "聊天气泡")
        def walk(o):
            if isinstance(o, dict):
                if "label" in o: lim(o["label"], 5 if lay == "stack" and o in (sc.get("blocks") or []) else 8, "标签")
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(sc)
        for k in ("before_label", "after_label", "input_label", "start_label", "left_label", "device_label"): lim(sc.get(k), 10, k)
    for sv in svgs:
        if re.search(r'\s(id|class)="', sv) or "<style" in sv or "<script" in sv or "Gradient" in sv or "<use" in sv:
            out.append("生成的 SVG 里有 id/class/style/script/渐变/use，公众号会吞掉"); break
    return out

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(out, exist_ok=True)
    slug = spec.get("slug", "banner"); variants = []
    key = "card" if spec.get("style") == "card" else "poster"
    if spec.get("style") in ("card", "poster", "neo") and spec.get(key, {}).get("theme", "all") == "all":   # 标题卡 / 海报 / 潮酷默认三色都出
        for name, lab in (("orange", "品牌橙"), ("blue", "蓝色"), ("teal", "绿色")):
            sp = json.loads(json.dumps(spec)); sp[key]["theme"] = name
            variants.append({"name": name, "label": lab, "svg": build(sp)})
    else:
        variants.append({"name": "", "label": "", "svg": build(spec)})
    for v in variants:
        open(os.path.join(out, f"{slug}{'-' + v['name'] if v['name'] else ''}.svg"), "w", encoding="utf-8").write(v["svg"])
    page = PAGE.replace("__TITLE__", esc(spec.get("title", "开头横幅"))).replace("__VARIANTS__", json.dumps(variants, ensure_ascii=False).replace("</", "<\\/"))
    open(os.path.join(out, f"{slug}-复制到公众号.html"), "w", encoding="utf-8").write(page)
    print(f"ok  {len(variants)} 个版本  ->  {out}/{slug}-复制到公众号.html")
    issues = check_spec(spec, [v["svg"] for v in variants])
    if issues:
        print("要改的地方：")
        for x in issues: print("  - " + x)
    else:
        print("自查通过：字数、数量都在范围内，没有公众号会吞掉的写法")
