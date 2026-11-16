import sys; sys.path.insert(0, '/home/claude/f45-social-assets/tools/top-attendees')
from top_attendees import photo_b64, b64, LOGO, BASE, INK, RED, GOLD, shoot
PHOTO = '/home/claude/work/wh/photo.jpg'
css = f"""
.ph{{position:absolute;left:0;top:0;width:1920px;height:1080px}}
.shade{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(18,12,51,.96) 0%,rgba(18,12,51,.88) 30%,rgba(18,12,51,.45) 52%,rgba(18,12,51,0) 72%),linear-gradient(0deg,rgba(18,12,51,.7) 0%,rgba(18,12,51,0) 22%)}}
.tb{{position:absolute;left:100px;top:0;bottom:100px;width:900px;display:flex;flex-direction:column;justify-content:center}}
.logo{{height:130px;width:auto;align-self:flex-start;margin-bottom:48px}}
.kick{{display:inline-block;align-self:flex-start;background:{RED};color:#fff;font-size:30px;font-weight:800;letter-spacing:4px;text-transform:uppercase;padding:12px 26px;border-radius:6px;margin-bottom:26px}}
.hl{{font-family:'Bebas Neue',Impact,sans-serif;font-weight:700;letter-spacing:3px;line-height:.86;color:#fff;font-size:136px;white-space:nowrap}}
.hl span{{color:{GOLD}}}
.tag{{font-size:44px;font-weight:700;color:#fff;margin-top:34px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:100px;background:{RED};display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}}
"""
body = f"""<img class="ph" src="{photo_b64(PHOTO,1920,1080,.5,.42)}"><div class="shade"></div>
<div class="tb"><img class="logo" src="{b64(LOGO)}"><div class="kick">Welcome to</div>
<div class="hl">F45 Training<br><span>West Highland</span></div><div class="tag">No one trains alone.</div></div>
<div class="foot">3460 W 38th Ave, Denver, CO 80211</div>"""
html = f'<html><head><meta charset="utf-8"><style>{BASE}html,body,.wrap{{width:1920px;height:1080px}}.wrap{{background:{INK}}}{css}</style></head><body><div class="wrap">{body}</div></body></html>'
import os; os.makedirs('/home/claude/work/wh/out_welcome', exist_ok=True)
print(shoot(html, 1920, 1080, '/home/claude/work/wh/out_welcome/west_highland_welcome_16x9.png'))
