"""Plu Ultra photo prep: add a soft navy top fade ONLY when the logo corner is bright.
usage: photo_prep.py IN OUT TARGET_W TARGET_H [logo_box=x,y,w,h in target px]
Crops to the target ratio (center), measures mean luminance of the logo box; if > THRESH, blends navy #211551
from the top (alpha 0.9 -> 0 over 32% of height). Prints 'fade:added' or 'fade:none' for the hand-off notes."""
import sys
from PIL import Image, ImageStat
NAVY=(33,21,81); BRIGHT=165; SHARE=0.20  # fade if >20% of logo-corner pixels are bright
def cover(im,w,h):
    r=max(w/im.width,h/im.height); im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2; return im.crop((x,y,x+w,y+h))
src,dst,w,h=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
box=[int(v) for v in (sys.argv[5] if len(sys.argv)>5 else '40,40,260,140').split(',')]
im=cover(Image.open(src).convert('RGB'),w,h)
g=im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3])).convert('L'); hist=g.histogram()
share=sum(hist[BRIGHT+1:])/sum(hist); lum=share*100
if share>SHARE:
    fh=int(h*0.32); mask=Image.new('L',(w,fh))
    mask.putdata([int(255*0.9*(1-y/fh)**1.6) for y in range(fh) for x in range(w)])
    im.paste(Image.new('RGB',(w,fh),NAVY),(0,0),mask); print(f'fade:added ({lum:.0f}% of logo corner is bright)')
else: print(f'fade:none ({lum:.0f}% of logo corner is bright)')
im.save(dst,quality=92)
