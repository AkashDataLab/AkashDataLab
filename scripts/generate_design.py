"""Generate GitHub-safe SVG artwork. No external services or dependencies."""
from pathlib import Path
import base64, html, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
P=json.loads((ROOT/'profile.json').read_text())
FONT='ui-monospace, SFMono-Regular, Consolas, monospace'

def txt(x,y,s,size=15,color='#dce4f2',anchor='start',weight=400):
 return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(s)}</text>'
def rect(x,y,w,h,fill,stroke='none',r=8):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" rx="{r}"/>'
def save(name,w,h,body):
 (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(name.removesuffix(".svg").replace("-"," "))}</title>{body}</svg>')

for mode in ['dark','light']:
 dark=mode=='dark'
 bg,panel,edge,fg,muted,cyan,purple=('#0a101f','#0f1b2e','#263650','#e3e8f4','#8e9eb9','#22d3ee','#aa9bef') if dark else ('#f4f6fc','#ffffff','#d8deec','#202d48','#63728c','#007e97','#7254bb')
 # A dotted mask creates the terminal portrait inside SVG; the source avatar is unchanged.
 avatar=base64.b64encode((OUT/'avatar.png').read_bytes()).decode()
 body=f'''<defs><clipPath id="portrait"><rect x="56" y="138" width="370" height="370" rx="4"/></clipPath><pattern id="dots" width="3" height="3" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.15" fill="white"/></pattern><mask id="dotmask"><rect x="56" y="138" width="370" height="370" fill="url(#dots)"/></mask><filter id="tint"><feColorMatrix type="matrix" values=".17 .57 .06 0 .03 .16 .52 .06 0 .02 .21 .71 .07 0 .05 0 0 0 1 0"/></filter></defs>'''
 body+=rect(0,0,1180,610,bg,r=18)+rect(13,13,1154,584,panel,edge,13)
 body+=f'<path d="M13 62H1167" stroke="{edge}"/>'
 for x,c in [(38,'#ff5f57'),(59,'#febc2e'),(80,'#28c840')]: body+=f'<circle cx="{x}" cy="38" r="6" fill="{c}"/>'
 body+=txt(590,43,'akash@quants:~  $ ./profile.sh --live',13,muted,'middle')
 body+=rect(35,88,412,472,bg,edge,6)+rect(468,88,677,472,bg,edge,6)
 body+=f'<path d="M35 124H447 M468 124H1145" stroke="{edge}"/>'
 body+=txt(51,111,'PROFILE.PORTRAIT',13,cyan,weight=700)+txt(432,111,'01 / AK',11,muted,'end')
 body+=f'<image x="56" y="138" width="370" height="370" xlink:href="data:image/png;base64,{avatar}" clip-path="url(#portrait)" mask="url(#dotmask)" filter="url(#tint)"/>'
 body+=txt(241,542,'AKASH KUMAR / INDIA',13,purple,'middle',700)
 body+=txt(485,111,'SYSTEM.INFO',13,cyan,weight=700)
 body+=txt(1127,111,'@'+P['username'],13,cyan,'end',700)
 rows=[('Name',P['name']),('Role','Aspiring Data Specialist'),('Primary.Focus','Data Analytics'),('Location','India'),('Status','Learning + Building'),('Languages','Python / SQL'),('Analysis','Pandas'),('Databases','PostgreSQL / MySQL / Oracle'),('Other.Tools','Firebase / Zapier'),('Current.Project','Retail Company Analysis'),('Learning','Content Creation'),('LinkedIn','/in/akashchaudharry'),('Email',P['email'])]
 for i,(k,v) in enumerate(rows):
  y=153+i*27
  body+=txt(486,y,k,13,muted)+txt(1127,y,v,13,fg,'end')
 body+=f'<path d="M485 514H1128" stroke="{edge}"/>'
 body+=f'<circle cx="490" cy="541" r="3" fill="{cyan}"/>'+txt(501,545,'BUILDING MY DATA PORTFOLIO',11,cyan)+txt(1127,545,'UTC+5:30 / IN',11,muted,'end')
 save(f'banner-{mode}.svg',1180,610,body)
 # Local animated typing line; a full static line remains when animation is disabled.
 body=f'''<style>@keyframes reveal{{0%,8%{{width:0}}55%,100%{{width:920px}}}}@keyframes blink{{50%{{opacity:0}}}}.reveal{{animation:reveal 8s steps(55,end) infinite}}.cursor{{animation:blink 1s steps(1) infinite}}@media(prefers-reduced-motion:reduce){{.reveal,.cursor{{animation:none}}}}</style><defs><clipPath id="line"><rect class="reveal" x="0" y="0" width="920" height="60"/></clipPath></defs>'''
 body+=f'<g clip-path="url(#line)">'+txt(460,36,'Akash Kumar · Aspiring Data Specialist',27,purple,'middle',700)+'</g>'
 save(f'typing-{mode}.svg',920,60,body)
 body=rect(0,0,960,160,bg,edge,12)+txt(26,30,'MY TOOLKIT',13,cyan,weight=700)
 tools=[('Python',110),('SQL',80),('Pandas',110),('PostgreSQL',155),('MySQL',105),('Oracle',110)]
 x=26
 for name,w in tools:
  body+=rect(x,52,w,40,panel,edge,7)+txt(x+w/2,77,name,14,purple,'middle',700);x+=w+14
 body+=txt(26,132,'ALSO EXPLORING',11,muted)+txt(190,132,'Firebase  /  Zapier  /  Content creation',13,fg)
 save(f'toolkit-{mode}.svg',960,160,body)
 body=rect(0,0,960,246,bg,edge,12)+txt(26,34,'HOW I APPROACH AN ANALYSIS',14,cyan,weight=700)
 labels=[('01','ASK','Define the question'),('02','CLEAN','Prepare the data'),('03','EXPLORE','Find patterns'),('04','EXPLAIN','Share the findings')]
 for i,(n,title,desc) in enumerate(labels):
  x=26+i*232
  body+=rect(x,62,212,142,panel,edge,8)+txt(x+18,91,n,13,cyan)+txt(x+18,126,title,18,purple,weight=700)+txt(x+18,163,desc,12,fg)
 body+=txt(26,230,'FOCUS: DATA ANALYTICS / CUSTOMER SHOPPING BEHAVIOUR',11,muted)
 save(f'focus-{mode}.svg',960,246,body)
 for name,label in [('linkedin','LINKEDIN'),('email','EMAIL'),('github','PROJECTS')]:
  save(f'{name}-{mode}.svg',142,38,rect(1,1,140,36,panel,edge,6)+txt(71,25,label,13,cyan,'middle',700))
print('Generated terminal banners, typing lines, toolkit, focus graphics and social buttons.')
