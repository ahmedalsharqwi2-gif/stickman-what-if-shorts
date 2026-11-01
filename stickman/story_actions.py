"""Character-led visual storyboards: goal, failed attempt, intervention, payoff.

These silent previews validate choreography. They are not narrated daily films.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont
from .candidate import FONT,CHANNEL_NAME

W,H=1080,1920
STORIES={
 'orbital_phone':{
  'world':'orbital_cabin','title':'سامي والموبايل الهارب',
  'goal':'يمسك الموبايل ويرجع للسرير',
  'beats':[
   ('bed_zone','wake','سامي صحي لقى نفسه بيطفو','الموبايل بعيد، وسامي عايز يرجع يمسكه'),
   ('window_zone','reach_miss','حاول يمسكه، فبعد أكتر','إيده لم توصل، والدفعة حرّكت الموبايل'),
   ('wall_zone','wall_push','غيّر خطته ودفع الحيطة','لمس الحيطة أولًا، ثم اتحرك بعيد عنها'),
   ('cabin_wide','air_run','جرّب يجري في الهوا وفشل','رجليه بتتحرك، لكنه مش بيوصل للموبايل'),
   ('handrail_zone','rope_throw','صاحبه رمى له الحبل','سامي مد إيده، والحبل وصل له فعلًا'),
   ('cabin_wide','rope_pull','مسك الحبل وسحب بهدوء','سحبة قصيرة غيّرت اتجاهه نحو الموبايل'),
   ('phone_close','phone_catch','المرة دي مسك الموبايل','الإيد والموبايل بقوا في نفس المكان'),
   ('bed_zone','return_secure','رجع وربطه جنب السرير','الهدف اتحقق، والموبايل مش هيفلت تاني')],
  'note':'شخصيات خيالية، الطفو المداري سقوط حر والجاذبية لم تختف'},
 'slippery_luggage':{
  'world':'station_corridor','title':'منى والشنطة اللي مش بتقف',
  'goal':'تلحق الشنطة قبل بوابة المحطة',
  'beats':[
   ('entrance','bag_roll','منى دخلت والشنطة زحلقت','في قصتنا الأرض بقت عديمة الاحتكاك'),
   ('long_corridor','chase_slip','جرت وراها، فرجليها زحلقت','المحاولة الأولى زوّدت المشكلة'),
   ('bench_zone','bench_push','مسكت الدكة ودفعت نفسها','استخدمت جسمًا ثابتًا لتغيّر حركتها'),
   ('gate_zone','bag_overshoot','قربت، لكن الشنطة سبقتها','لازم تلحق المقبض، مش تجري وخلاص'),
   ('helper_zone','scarf_throw','صاحبها مد لها الوشاح','ظهر حل جديد يربطها بنقطة ثابتة'),
   ('long_corridor','scarf_brake','مسكته وقللت سرعتها','الشد غيّر الحركة، من غير قفزة سحرية'),
   ('bag_close','bag_catch','وصلت للمقبض ومسكت الشنطة','إيدها اتقفلت على المقبض فعلًا'),
   ('gate_zone','bag_secure','ربطتها وعدّت البوابة','المشكلة انتهت بفعل واضح ونتيجة')],
  'note':'تجربة خيالية مبسطة، وليست محاكاة أو تعليمات أمان'}
}

def lerp(a,b,p):return a+(b-a)*p
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def point(a,b,p):return (lerp(a[0],b[0],p),lerp(a[1],b[1],p))

def solve_joint(base,target,a,b,bend=1):
 dx,dy=target[0]-base[0],target[1]-base[1];distance=math.hypot(dx,dy)
 d=max(abs(a-b)+.01,min(a+b-.01,distance));angle=math.atan2(dy,dx)
 offset=math.acos(max(-1,min(1,(a*a+d*d-b*b)/(2*a*d))))
 joint=(base[0]+a*math.cos(angle+bend*offset),base[1]+a*math.sin(angle+bend*offset))
 end=(base[0]+d*math.cos(angle),base[1]+d*math.sin(angle))
 return joint,end

def state_at(scenario,t,seconds=32):
 spec=STORIES[scenario];beat=min(7,max(0,int(t/seconds*8)));p=max(0,min(1,t/seconds*8-beat));q=ease(p)
 hip=(600,1060);left=(500,960);right=(710,920);feet=[(550,1290),(650,1290)]
 phone=(970,665);bag=(940,1190);rope=None;held=False
 if scenario=='orbital_phone':
  if beat==0:
   hip=point((545,1250),(610,1030),q);left=point((420,1230),(480,850),q);right=point((680,1190),(750,825),q);feet=[(hip[0]-95,hip[1]+150),(hip[0]+80,hip[1]+175)]
  elif beat==1:
   hip=point((610,1030),(710,955),q);right=point((720,875),(888,716),q);left=(hip[0]-85,hip[1]-70);phone=point((925,680),(1000,630),q)
  elif beat==2:
   hip=point((210,1000),(590,1020),ease(max(0,(p-.35)/.65)));left=(90,835) if p<.35 else (hip[0]-100,hip[1]-80);right=(hip[0]+100,hip[1]-170);feet=[(hip[0]-85,hip[1]+195),(hip[0]+80,hip[1]+165)]
  elif beat==3:
   hip=(625+12*p,1020);left=(hip[0]-100,850+60*math.sin(p*math.pi*6));right=(hip[0]+100,850-60*math.sin(p*math.pi*6));feet=[(hip[0]-70+70*math.sin(p*math.pi*6),hip[1]+170+70*math.cos(p*math.pi*6)),(hip[0]+70-70*math.sin(p*math.pi*6),hip[1]+170-70*math.cos(p*math.pi*6))]
  elif beat==4:
   hip=(770,1030);left=(650,860);right=(855,915);tip=point((270,930),left,q);tip=(tip[0],tip[1]-160*math.sin(p*math.pi));rope=((170,1080),tip)
  elif beat==5:
   hip=point((770,1030),(560,1010),q);left=(hip[0]-110,hip[1]-170);right=(hip[0]-20,hip[1]-90-35*math.sin(p*math.pi*4));rope=((170,1080),left)
  elif beat==6:
   hip=point((650,1010),(800,925),q);phone=(910,715);right=point((770,870),phone,q);left=(hip[0]-90,hip[1]-30);held=p>.94
  else:
   hip=point((800,925),(555,1185),q);left=point((710,900),(435,1210),q);right=(hip[0]+90,hip[1]-130);phone=right if p<.85 else(680,1190);held=True;feet=[(hip[0]-100,hip[1]+155),(hip[0]+95,hip[1]+135)]
 else:
  if beat==0:hip=point((350,1110),(465,1110),q);bag=point((570,1210),(920,1210),q);left=(hip[0]-85,1010);right=(hip[0]+90,990)
  elif beat==1:
   hip=point((380,1110),(460,1120),q);bag=point((850,1210),(985,1210),q);feet=[(hip[0]-100-70*math.sin(p*math.pi*6),1370),(hip[0]+100+70*math.sin(p*math.pi*6),1340)];left=(hip[0]-100,950);right=(hip[0]+115,1010)
  elif beat==2:
   hip=point((250,1110),(610,1110),ease(max(0,(p-.3)/.7)));left=(110,945) if p<.3 else(hip[0]-90,1000);right=(hip[0]+100,950)
  elif beat==3:hip=point((610,1110),(750,1110),q);bag=point((880,1210),(1010,1210),q);right=(hip[0]+130,980);left=(hip[0]-85,1030)
  elif beat==4:
   hip=(760,1110);left=(640,950);right=(855,1030);tip=point((260,950),left,q);tip=(tip[0],tip[1]-120*math.sin(p*math.pi));rope=((140,1100),tip)
  elif beat==5:
   hip=point((760,1110),(650,1110),q);left=(hip[0]-100,965);right=(hip[0]+75,1010);rope=((140,1100),left);bag=(930,1210)
  elif beat==6:
   hip=point((650,1110),(790,1110),q);bag=(940,1210);right=point((750,1010),(940,1095),q);left=(hip[0]-90,1015);held=p>.94
  else:hip=point((790,1110),(630,1110),q);right=(hip[0]+125,1085);left=(hip[0]-90,1010);bag=(right[0],1200);held=True
 if beat not in (0,3,7) or scenario!='orbital_phone':
  if not(scenario=='slippery_luggage' and beat==1):feet=[(hip[0]-55,hip[1]+235),(hip[0]+65,hip[1]+220)]
 shoulders=[(hip[0]-24,hip[1]-160),(hip[0]+24,hip[1]-160)]
 left_elbow,left_hand=solve_joint(shoulders[0],left,110,115,-1);right_elbow,right_hand=solve_joint(shoulders[1],right,110,115,1)
 if held and scenario=='orbital_phone' and beat==6:phone=right_hand
 if rope and beat in (4,5):rope=(rope[0],left_hand if beat==5 or p>.98 else rope[1])
 return {'world':spec['world'],'beat':beat,'p':p,'setting':spec['beats'][beat][0],'action':spec['beats'][beat][1],'hip':hip,'shoulders':shoulders,'elbows':[left_elbow,right_elbow],'hands':[left_hand,right_hand],'feet':feet,'phone':phone,'bag':bag,'rope':rope,'held':held,'goal_achieved':beat==7 and p>.8}

def font(size):return ImageFont.truetype(str(FONT),size)
def actor(draw,state,color='#f6c36b',friend=False):
 hip=state['hip'];head=(hip[0],hip[1]-275);outline='#131c2b';width=13
 draw.ellipse((hip[0]-115,hip[1]+228,hip[0]+115,hip[1]+251),fill='#172634')
 draw.line(((hip[0],hip[1]-205),hip),fill=color,width=width)
 for side in range(2):
  points=[state['shoulders'][side],state['elbows'][side],state['hands'][side]];draw.line(points,fill=color,width=width,joint='curve')
  knee,foot=solve_joint((hip[0]+(-18 if side==0 else 18),hip[1]),state['feet'][side],125,125,-1 if side==0 else 1)
  draw.line((hip,knee,foot),fill=color,width=width,joint='curve')
  for point_ in (state['elbows'][side],knee):draw.ellipse((point_[0]-7,point_[1]-7,point_[0]+7,point_[1]+7),fill=color)
  hand=state['hands'][side];draw.ellipse((hand[0]-13,hand[1]-13,hand[0]+13,hand[1]+13),fill='#fff1d6',outline=color,width=3)
 draw.ellipse((head[0]-68,head[1]-68,head[0]+68,head[1]+68),fill='#fffaf0',outline=color,width=6)
 happy=state['beat']==7
 for offset in (-23,23):
  x=head[0]+offset;draw.ellipse((x-6,head[1]-16,x+6,head[1]+1),fill=outline)
 if happy:draw.arc((head[0]-28,head[1]-2,head[0]+28,head[1]+35),0,180,fill=outline,width=5)
 else:draw.ellipse((head[0]-10,head[1]+14,head[0]+10,head[1]+33),outline=outline,width=4)

def frame(scenario,t,seconds=32):
 spec=STORIES[scenario];s=state_at(scenario,t,seconds);orbital=scenario=='orbital_phone';im=Image.new('RGB',(W,H),'#07172b' if orbital else'#e8cfaa');d=ImageDraw.Draw(im)
 for y in range(0,H,12):
  if orbital:c=(8+int(y/H*12),24+int(y/H*20),44+int(y/H*24))
  else:c=(235-int(y/H*22),221-int(y/H*30),193-int(y/H*33))
  d.rectangle((0,y,W,y+12),fill=c)
 if orbital:
  # Different physically staged zones, rather than a single bed background.
  zone=s['setting'];window_x=620 if zone in ('window_zone','phone_close') else 330
  d.rounded_rectangle((window_x-260,330,window_x+260,825),radius=55,fill='#020914',outline='#6d8c9c',width=15)
  d.ellipse((window_x-185,400,window_x+185,770),fill='#2e7caa',outline='#64b8ca',width=6)
  for n in range(14):
   x=(n*137+31)%1080;y=345+(n*89)%430;d.ellipse((x,y,x+3,y+3),fill='#d5e8ec')
  d.polygon(((0,1390),(1080,1390),(1080,1920),(0,1920)),fill='#263e50')
  for n in range(-3,5):d.line((540+n*85,1390,540+n*400,1920),fill='#466379',width=3)
  if zone in ('bed_zone','cabin_wide'):
   d.polygon(((230,1310),(825,1255),(955,1360),(320,1430)),fill='#64809d',outline='#b3c2c9');d.polygon(((320,1430),(955,1360),(955,1410),(320,1480)),fill='#344f6b')
  if zone=='wall_zone':
   d.rectangle((30,310,110,1450),fill='#516e83');d.rounded_rectangle((60,715,105,1090),radius=12,fill='#aac3cd')
  if zone in ('handrail_zone','cabin_wide'):
   d.rounded_rectangle((95,1050,200,1125),radius=20,outline='#bfd3d8',width=12)
  if zone=='phone_close':
   d.rounded_rectangle((760,400,1040,1200),radius=25,fill='#18334c',outline='#6b8c9c',width=6)
   for y in range(460,1000,100):d.line((795,y,995,y),fill='#446779',width=4)
 else:
  zone=s['setting'];d.rectangle((0,350,1080,1340),fill='#dfc39d')
  for x in range(0,1080,180):d.rectangle((x+12,365,x+140,820),fill='#8ca3a8',outline='#faf0d8',width=8)
  d.polygon(((0,1300),(1080,1300),(1080,1920),(0,1920)),fill='#b49b78')
  for n in range(-4,6):d.line((540+n*65,1300,540+n*300,1920),fill='#d1bd99',width=3)
  if zone in ('entrance','gate_zone','long_corridor'):
   d.rectangle((820,300,910,1460),fill='#546b6b');d.rectangle((910,940,1060,1000),fill='#ab654c')
   d.rounded_rectangle((780,340,1030,460),radius=10,fill='#294f5a');d.text((1005,375),'بوابة المحطة',font=font(29),fill='#fff4d9',anchor='ra',direction='rtl')
  if zone in ('bench_zone','helper_zone'):
   d.rounded_rectangle((40,1050,330,1130),radius=16,fill='#a26848');d.rectangle((75,1130,100,1400),fill='#485754');d.rectangle((285,1130,310,1400),fill='#485754')
  if zone=='bag_close':d.rounded_rectangle((690,590,1060,1360),radius=35,fill='#ccb58c',outline='#faf0db',width=7)
 # Friend appears at the actual intervention rather than waving in every scene.
 if s['beat'] in (4,5):
  helper=state_at(scenario,0,seconds);helper.update(hip=(180,1100),beat=7,shoulders=[(156,940),(204,940)],elbows=[(110,1000),(250,930)],hands=[(95,1055),(280,940)],feet=[(120,1330),(240,1330)])
  actor(d,helper,'#8fd3bf',True)
 if s['rope']:
  start,end=s['rope'];d.line((start,((start[0]+end[0])/2,max(start[1],end[1])+55),end),fill='#efb779',width=8,joint='curve')
 actor(d,s)
 if orbital:
  x,y=s['phone'];d.rounded_rectangle((x-28,y-48,x+28,y+48),radius=9,fill='#112031',outline='#f6ca72',width=5);d.rectangle((x-17,y-33,x+17,y+25),fill='#80c8cd')
  if s['goal_achieved']:d.line((640,1155,720,1240),fill='#ecb96c',width=10)
 else:
  x,y=s['bag'];d.rounded_rectangle((x-65,y-95,x+65,y+80),radius=22,fill='#a05d3d',outline='#473b30',width=5);d.rounded_rectangle((x-26,y-118,x+26,y-92),radius=8,outline='#473b30',width=7)
  for dx in (-42,42):d.ellipse((x+dx-12,y+70,x+dx+12,y+94),fill='#34424a')
 d.rounded_rectangle((55,65,1025,250),radius=22,fill='#142d40' if orbital else'#4f665e')
 d.text((975,98),spec['title'],font=font(43),fill='#fff0bf',anchor='ra',direction='rtl')
 d.text((975,170),CHANNEL_NAME+'، '+spec['goal'],font=font(28),fill='#e1e8dd',anchor='ra',direction='rtl')
 title,caption=spec['beats'][s['beat']][2:]
 d.rounded_rectangle((55,1500,1025,1735),radius=22,fill='#10283a' if orbital else'#4f665e')
 d.text((970,1533),title,font=font(38),fill='#ffe1a0',anchor='ra',direction='rtl')
 d.text((970,1610),caption,font=font(28),fill='#f8f0df',anchor='ra',direction='rtl')
 d.text((540,1790),'مراجعة قصة وحركة صامتة، لا تصلح للنشر',font=font(27),fill='#e7bc79' if orbital else'#384d49',anchor='ma',direction='rtl')
 d.text((540,1840),spec['note'],font=font(21),fill='#bfd0d4' if orbital else'#384d49',anchor='ma',direction='rtl')
 return im

def render(scenario,output,seconds=32,fps=24):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 if output.exists():raise FileExistsError('Existing preview is retained')
 partial=output.with_name(output.stem+'.partial.mp4')
 if partial.exists():raise FileExistsError('Incomplete preview is retained')
 process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(partial)],stdin=subprocess.PIPE)
 try:
  for n in range(round(seconds*fps)):process.stdin.write(frame(scenario,n/fps,seconds).tobytes())
  process.stdin.close()
  if process.wait():raise RuntimeError('Frame encoding failed')
 except BaseException:process.kill();process.wait();raise
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(partial),'-f','null','-'],check=True)
 partial.rename(output)
 report={'scenario':scenario,'world':STORIES[scenario]['world'],'duration':seconds,'fps':fps,'frames':round(seconds*fps),'width':W,'height':H,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'full_decode':'PASS','silent_visual_review':True,'publishable':False,'actions':[b[1] for b in STORIES[scenario]['beats']]}
 output.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--scenario',choices=STORIES,required=True);p.add_argument('--output',required=True);p.add_argument('--seconds',type=float,default=32);p.add_argument('--fps',type=int,default=24);a=p.parse_args();print(json.dumps(render(a.scenario,a.output,a.seconds,a.fps),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
