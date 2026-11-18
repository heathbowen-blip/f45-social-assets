"""Build an adaptive white logo card on a transparent zone PNG (Plu Ultra BOTM option A).
usage: logo_card.py LOGO OUT ZONE_W ZONE_H LOGO_AREA ALIGN(left|right)"""
import sys, math
from PIL import Image, ImageFont, ImageDraw
def trim(im):
    im=im.convert('RGBA'); a=im.getchannel('A')
    if a.getextrema()[0]<250: mask=a.point(lambda v:255 if v>20 else 0)
    else:
        bg=im.getpixel((2,2))[:3]; rgb=im.convert('RGB')
        diff=Image.eval(Image.merge('RGB',[c.point(lambda v,b=b:abs(v-b)) for c,b in zip(rgb.split(),bg)]).convert('L'),lambda v:255 if v>13 else 0)
        mask=diff; im.putalpha(mask)
    bb=mask.getbbox(); return im.crop(bb)
def card(logo,zw,zh,area,align,scale=4):
    zw,zh=zw*scale,zh*scale; area*=scale*scale
    r=logo.width/logo.height; h=math.sqrt(area/r); w=h*r
    pad=lambda hh:max(22*scale,hh*0.28)
    s=min(1,(zw-2*pad(h))/w,(zh-2*pad(h))/h); w,h=int(w*s),int(h*s); p=int(pad(h))
    cw,ch=w+2*p,h+2*p
    out=Image.new('RGBA',(zw,zh),(0,0,0,0))
    c=Image.new('RGBA',(cw,ch),(255,255,255,255)); L=logo.resize((w,h),Image.LANCZOS); c.paste(L,(p,p),L)
    x=0 if align=='left' else zw-cw; out.paste(c,(x,(zh-ch)//2)); return out
if __name__=='__main__':
    src,dst,zw,zh,area,align=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    if src=='PLACEHOLDER':
        logo=Image.new('RGBA',(600,200),(0,0,0,0)); d=ImageDraw.Draw(logo)
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',120); d.text((300,100),'LOGO',font=f,fill=(150,150,160,255),anchor='mm'); logo=logo.crop(logo.getchannel('A').getbbox())
    else: logo=trim(Image.open(src))
    card(logo,zw,zh,area,align).save(dst); print(dst)
