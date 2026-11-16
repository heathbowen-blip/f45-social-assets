"""Top 10 Attendees template: OptiSigns 16:9, IG feed 4:5, IG story 9:16.
Usage: python top_attendees.py data.json outdir
data.json: {studio, city, period, month_slug, show_counts, attendees:[{name:"First L.", visits:29}, ...10]}
Names must already be first name + last initial."""
import base64, glob, json, sys, os, io
from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

LOGO = glob.glob("/root/.claude/skills/synced/*/f45-motm-newsletter/assets/f45_logo_white.png")[0]
NAVY, INK, RED, CREAM = "#211551", "#120C33", "#D6001C", "#FAF8F3"
GOLD = "#F5C451"

def photo_b64(p, w, h, fx=0.5, fy=0.4):
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    sc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x0 = round((im.width - w) * fx); y0 = round((im.height - h) * fy)
    im = im.crop((x0, y0, x0 + w, y0 + h))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=84)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def b64(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

BASE = f"""*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{overflow:hidden;font-family:Montserrat,Arial,sans-serif;color:{CREAM}}}
.wrap{{position:relative;overflow:hidden;background:
 radial-gradient(900px 700px at 8% 0%,#3A2A8C55,transparent 70%),
 radial-gradient(800px 600px at 100% 100%,#D6001C33,transparent 70%),{INK}}}
.grid{{position:absolute;inset:0;background-image:repeating-linear-gradient(115deg,rgba(255,255,255,.035) 0 2px,transparent 2px 44px)}}
.hl{{font-family:'Bebas Neue',Impact,sans-serif;font-weight:700;letter-spacing:2px;line-height:.86;color:#fff}}
.kick{{display:inline-block;background:{RED};color:#fff;font-weight:800;letter-spacing:3px;text-transform:uppercase;border-radius:6px}}
.row{{display:flex;align-items:center;white-space:nowrap}}
.rk{{font-family:'Bebas Neue',Impact,sans-serif;font-weight:700;color:{RED};text-align:center}}
.nm{{font-weight:800;color:#fff}}
.ct{{margin-left:auto;font-weight:600;color:#C9C3E8}}
.r1 .rk{{color:{GOLD}}} .r1 .nm{{color:{GOLD}}}
"""

def rows(att, show, label=True):
    out = ""
    for i, a in enumerate(att, 1):
        ct = f'<span class="ct">{a["visits"]}{" classes" if label else ""}</span>' if show else ""
        out += f'<div class="row r{i}"><span class="rk">{i}</span><span class="nm">{a["name"]}</span>{ct}</div>'
    return out

PH_CSS = f""".ph{{position:absolute;inset:0;width:100%;height:100%;filter:blur(1.5px) saturate(.95);transform:scale(1.03)}}
.row{{background:rgba(18,12,51,.8)!important}} .r1{{background:rgba(70,52,20,.80)!important}}"""

def page(w, h, css, body, photo=None, fx=0.5, fy=0.4, scrim=''):
    ph = f'<img class="ph" src="{photo_b64(photo, w, h, fx, fy)}"><div style="position:absolute;inset:0;background:{scrim}"></div>' if photo else ""
    extra = PH_CSS if photo else ""
    return f'<html><head><meta charset="utf-8"><style>{BASE}html,body,.wrap{{width:{w}px;height:{h}px}}{css}{extra}</style></head><body><div class="wrap">{ph}<div class="grid"></div>{body}</div></body></html>'

def billboard(d):
    att = d['attendees']; n = len(att); R = (n + 1) // 2; big = n <= 10
    titl = f"Top {n}<br>Attendees"
    css = f"""
.left{{position:absolute;left:90px;top:0;bottom:0;width:640px;display:flex;flex-direction:column;justify-content:center}}
.left img{{height:96px;width:auto;align-self:flex-start;margin-bottom:46px}}
.kick{{font-size:28px;padding:11px 24px;align-self:flex-start;margin-bottom:24px}}
.hl.t{{font-size:168px}} .hl.s{{font-size:92px;color:{GOLD};margin-top:18px}}
.per{{font-size:32px;font-weight:600;color:#C9C3E8;margin-top:30px;line-height:1.35}}
.board{{position:absolute;left:800px;right:90px;top:{90 if big else 48}px;bottom:{150 if big else 128}px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:36px;row-gap:{14 if big else 7}px}}
.row{{background:rgba(255,255,255,.06);border-left:6px solid {RED};border-radius:10px;padding:0 22px}}
.r1{{border-left-color:{GOLD};background:rgba(245,196,81,.12)}}
.rk{{font-size:{80 if big else 52}px;width:{80 if big else 62}px;margin-right:{18 if big else 12}px}} .nm{{font-size:{38 if big else 34}px;margin-right:14px}} .ct{{font-size:{24 if big else 21}px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:100px;background:{RED};display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}}
"""
    body = f"""<div class="left"><img src="{b64(LOGO)}"><div class="kick">Community Spotlight</div>
<div class="hl t">{titl}</div><div class="hl s">{d['studio']}</div>
<div class="per">{d['period']}</div></div>
<div class="board">{rows(att, d.get('show_counts', True))}</div>
<div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    return page(1920, 1080, css, body, d.get('photo'), .5, .30, 'linear-gradient(95deg,rgba(18,12,51,.9) 0%,rgba(18,12,51,.82) 38%,rgba(18,12,51,.6) 100%)')

def feed(d):
    att = d['attendees']; n = len(att); R = (n + 1) // 2; big = n <= 10
    css = f"""
.head{{position:absolute;left:70px;right:70px;top:{64 if big else 56}px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.head img{{height:{78 if big else 62}px;margin-bottom:{26 if big else 18}px}}
.kick{{font-size:{24 if big else 21}px;padding:{9 if big else 7}px 20px;margin-bottom:{18 if big else 12}px}}
.hl.t{{font-size:{150 if big else 124}px}} .hl.s{{font-size:{60 if big else 54}px;color:{GOLD};margin-top:12px}}
.per{{font-size:{26 if big else 23}px;font-weight:600;color:#C9C3E8;margin-top:{16 if big else 12}px}}
.board{{position:absolute;left:50px;right:50px;top:{660 if big else 470}px;bottom:{130 if big else 126}px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:22px;row-gap:{10 if big else 7}px}}
.row{{background:rgba(255,255,255,.06);border-left:5px solid {RED};border-radius:8px;padding:0 14px}}
.r1{{border-left-color:{GOLD};background:rgba(245,196,81,.12)}}
.rk{{font-size:{56 if big else 42}px;width:{54 if big else 50}px;margin-right:10px}} .nm{{font-size:{30 if big else 30}px;margin-right:8px}} .ct{{font-size:{18 if big else 22}px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:96px;background:{RED};display:flex;align-items:center;justify-content:center;font-size:29px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}}
"""
    body = f"""<div class="head"><img src="{b64(LOGO)}"><div class="kick">Community Spotlight</div>
<div class="hl t">Top {n} Attendees</div><div class="hl s">{d['studio']}</div><div class="per">{d['period']}</div></div>
<div class="board">{rows(att, d.get('show_counts', True), label=big)}</div>
<div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    sc = 'linear-gradient(180deg,rgba(18,12,51,.55) 0%,rgba(18,12,51,.5) 30%,rgba(18,12,51,.9) 48%,rgba(18,12,51,.92) 100%)' if big else 'linear-gradient(180deg,rgba(18,12,51,.5) 0%,rgba(18,12,51,.5) 22%,rgba(18,12,51,.9) 36%,rgba(18,12,51,.93) 100%)'
    return page(1080, 1350, css, body, d.get('photo'), .5, .28, sc)

def story(d):
    att = d['attendees']; n = len(att); R = (n + 1) // 2; big = n <= 10
    css = f"""
.head{{position:absolute;left:70px;right:70px;top:240px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.head img{{height:{84 if big else 70}px;margin-bottom:{28 if big else 22}px}}
.kick{{font-size:{24 if big else 22}px;padding:9px 20px;margin-bottom:{18 if big else 14}px}}
.hl.t{{font-size:{150 if big else 124}px}} .hl.s{{font-size:{60 if big else 54}px;color:{GOLD};margin-top:12px}}
.per{{font-size:{27 if big else 24}px;font-weight:600;color:#C9C3E8;margin-top:{16 if big else 12}px}}
.board{{position:absolute;left:60px;right:60px;top:{860 if big else 650}px;height:{700 if big else 910}px;display:grid;{"grid-template-rows:repeat(10,1fr);row-gap:8px" if big else f"grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:20px;row-gap:8px"}}}
.row{{background:rgba(255,255,255,.06);border-left:5px solid {RED};border-radius:8px;padding:0 {22 if big else 14}px}}
.r1{{border-left-color:{GOLD};background:rgba(245,196,81,.12)}}
.rk{{font-size:{50 if big else 46}px;width:{60 if big else 54}px;margin-right:{16 if big else 10}px}} .nm{{font-size:{33 if big else 32}px;margin-right:8px}} .ct{{font-size:{22 if big else 24}px}}
.foot{{position:absolute;left:90px;right:90px;top:1585px;height:70px;background:{RED};border-radius:35px;display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}}
"""
    body = f"""<div class="head"><img src="{b64(LOGO)}"><div class="kick">Community Spotlight</div>
<div class="hl t">{"Top 10<br>Attendees" if big else f"Top {n} Attendees"}</div><div class="hl s">{d['studio']}</div><div class="per">{d['period']}</div></div>
<div class="board">{rows(att, d.get('show_counts', True), label=big)}</div>
<div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    sc = 'linear-gradient(180deg,rgba(18,12,51,.6) 0%,rgba(18,12,51,.5) 28%,rgba(18,12,51,.92) 44%,rgba(18,12,51,.94) 100%)' if big else 'linear-gradient(180deg,rgba(18,12,51,.55) 0%,rgba(18,12,51,.5) 24%,rgba(18,12,51,.9) 36%,rgba(18,12,51,.94) 100%)'
    return page(1080, 1920, css, body, d.get('photo'), .55, .30, sc)

def shoot(html, w, h, out):
    open("/tmp/_ta.html", "w").write(html)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": w, "height": h})
        pg.goto("file:///tmp/_ta.html"); pg.wait_for_timeout(500)
        over = pg.evaluate("()=>[...document.querySelectorAll('.row,.hl,.per')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent.slice(0,30))")
        pg.screenshot(path=out); br.close()
    return over


def hero(d, fmt):
    """Photo-forward layout: clear photo panel + solid navy board."""
    att = d['attendees']; n = len(att); R = (n + 1) // 2; sh = d.get('show_counts', True)
    lab = n <= 10
    ph = d['photo']
    common = f"""
.hl.t{{white-space:nowrap}} .hl.s{{color:{GOLD}}}
.row{{background:rgba(255,255,255,.07);border-left:5px solid {RED};border-radius:8px}}
.r1{{border-left-color:{GOLD};background:rgba(245,196,81,.14)}}
.foot{{position:absolute;background:{RED};display:flex;align-items:center;justify-content:center;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}}
.ph{{position:absolute;object-fit:cover}}"""
    if fmt == "billboard":
        W, H = 1920, 1080
        css = common + f"""
.ph{{left:0;top:0;width:1000px;height:1080px;-webkit-mask-image:linear-gradient(to right,#000 72%,transparent 100%);mask-image:linear-gradient(to right,#000 72%,transparent 100%)}}
.shade{{position:absolute;left:0;top:0;width:1000px;height:1080px;background:linear-gradient(to top,rgba(18,12,51,.96) 0%,rgba(18,12,51,.82) 26%,rgba(18,12,51,0) 52%),linear-gradient(to bottom,rgba(18,12,51,.55) 0%,rgba(18,12,51,0) 22%)}}
.logo{{position:absolute;left:70px;top:56px;height:92px}}
.tb{{position:absolute;left:70px;bottom:128px;width:860px}}
.kick{{font-size:26px;padding:10px 22px;margin-bottom:20px}}
.hl.t{{font-size:118px}} .hl.s{{font-size:66px;margin-top:12px}} .per{{font-size:28px;font-weight:600;color:#D9D4F2;margin-top:16px}}
.board{{position:absolute;left:990px;right:56px;top:44px;bottom:128px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:26px;row-gap:7px}}
.row{{padding:0 18px}} .rk{{font-size:52px;width:62px;margin-right:12px}} .nm{{font-size:33px;margin-right:10px}} .ct{{font-size:23px}}
.foot{{left:0;right:0;bottom:0;height:100px;font-size:36px}}"""
        bpos = (.55, .45)
        body = f"""<img class="ph" src="{photo_b64(ph,1000,1080,*bpos)}"><div class="shade"></div><img class="logo" src="{b64(LOGO)}">
<div class="tb"><div class="kick">Community Spotlight</div><div class="hl t">Top {n} Attendees</div><div class="hl s">{d['studio']}</div><div class="per">{d['period']}</div></div>
<div class="board">{rows(att, sh, label=False)}</div><div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    elif fmt == "feed":
        W, H = 1080, 1350
        css = common + f"""
.ph{{left:0;top:0;width:1080px;height:560px}}
.shade{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(to bottom,rgba(18,12,51,.6) 0%,rgba(18,12,51,0) 22%,rgba(18,12,51,0) 40%,rgba(18,12,51,.88) 78%,{INK} 100%)}}
.logo{{position:absolute;left:40px;top:30px;height:58px}}
.tb{{position:absolute;left:0;right:0;top:318px;text-align:center}}
.hl.t{{font-size:118px}} .hl.s{{font-size:54px;margin-top:6px}} .per{{font-size:23px;font-weight:600;color:#D9D4F2;margin-top:10px}}
.board{{position:absolute;left:50px;right:50px;top:572px;bottom:122px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:20px;row-gap:6px}}
.row{{padding:0 14px}} .rk{{font-size:42px;width:52px;margin-right:10px}} .nm{{font-size:30px;margin-right:8px}} .ct{{font-size:22px}}
.foot{{left:0;right:0;bottom:0;height:92px;font-size:28px}}"""
        body = f"""<img class="ph" src="{photo_b64(ph,1080,560,.5,.4)}"><div class="shade"></div><img class="logo" src="{b64(LOGO)}">
<div class="tb"><div class="hl t">Top {n} Attendees</div><div class="hl s">{d['studio']}</div><div class="per">{d['period']}</div></div>
<div class="board">{rows(att, sh, label=False)}</div><div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    else:
        W, H = 1080, 1920
        css = common + f"""
.ph{{left:0;top:0;width:1080px;height:860px}}
.shade{{position:absolute;left:0;top:0;width:1080px;height:860px;background:linear-gradient(to bottom,rgba(18,12,51,.75) 0%,rgba(18,12,51,.68) 34%,rgba(18,12,51,0) 48%,rgba(18,12,51,0) 56%,rgba(18,12,51,.9) 84%,{INK} 100%)}}
.logo{{position:absolute;left:56px;top:236px;height:68px}}
.tb{{position:absolute;left:0;right:0;top:640px;text-align:center}}
.hl.t{{font-size:124px}} .hl.s{{font-size:56px;margin-top:6px}} .per{{font-size:25px;font-weight:600;color:#D9D4F2;margin-top:10px}}
.board{{position:absolute;left:60px;right:60px;top:880px;height:690px;display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat({R},1fr);column-gap:20px;row-gap:7px}}
.row{{padding:0 14px}} .rk{{font-size:46px;width:54px;margin-right:10px}} .nm{{font-size:32px;margin-right:8px}} .ct{{font-size:24px}}
.foot{{left:60px;right:60px;top:1592px;height:68px;border-radius:34px;font-size:24px}}"""
        body = f"""<img class="ph" src="{photo_b64(ph,1080,860,.5,.4)}"><div class="shade"></div><img class="logo" src="{b64(LOGO)}">
<div class="tb"><div class="hl t">Top {n} Attendees</div><div class="hl s">{d['studio']}</div><div class="per">{d['period']}</div></div>
<div class="board">{rows(att, sh, label=False)}</div><div class="foot">{d.get('footer','Real consistency. Real results.')}</div>"""
    html = f'<html><head><meta charset="utf-8"><style>{BASE}html,body,.wrap{{width:{W}px;height:{H}px}}.wrap{{background:{INK}}}{css}</style></head><body><div class="wrap"><div class="grid"></div>{body}</div></body></html>'
    return html, W, H

if __name__ == "__main__":
    d = json.load(open(sys.argv[1])); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    s = d["slug"]
    res = {}
    if d.get("photo"):
        for k, nm in (("billboard", "billboard_16x9"), ("feed", "feed_4x5"), ("story", "story_9x16")):
            html, W, H = hero(d, k); res[k] = shoot(html, W, H, f"{od}/{s}_{nm}.png")
    else:
        res["billboard"] = shoot(billboard(d), 1920, 1080, f"{od}/{s}_billboard_16x9.png")
        res["feed"] = shoot(feed(d), 1080, 1350, f"{od}/{s}_feed_4x5.png")
        res["story"] = shoot(story(d), 1080, 1920, f"{od}/{s}_story_9x16.png")
    print(res)
