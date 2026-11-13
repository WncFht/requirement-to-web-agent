"""Build editable draw.io diagrams and SVG previews from one scene description."""
from pathlib import Path
import base64
import html
import json
import xml.etree.ElementTree as E

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
STEM = '2026-11-13-适配器架构与运行轨迹'
W, H = 1600, 1080
INK, MUTED, LINE = '#172B4D', '#61748B', '#DCE5EF'
BLUE, TEAL, PURPLE, ORANGE = '#2764E7', '#138775', '#7952C5', '#C07824'
SCENES = []
ICONS = {
 'file': '<path d="M7 3h7l4 4v14H7z M14 3v5h5 M10 12h5 M10 16h5"/>',
 'cpu': '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="10" y="10" width="4" height="4"/><path d="M9 2v4 M15 2v4 M9 18v4 M15 18v4 M2 9h4 M2 15h4 M18 9h4 M18 15h4"/>',
 'terminal': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3 M13 15h4"/>',
 'app': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 8h18 M7 5h1 M11 5h1 M8 12h8 M8 16h5"/>',
 'db': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5 M4 12c0 4 16 4 16 0"/>',
 'check': '<path d="m5 12 4 4L20 5 M20 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/>',
 'layers': '<path d="m3 7 9-5 9 5-9 5z M3 12l9 5 9-5 M3 17l9 5 9-5"/>',
 'chart': '<path d="M4 3v18h18 M8 16v-5 M13 16V7 M18 16V4"/>',
}

def icon_svg(name, color):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g></svg>'

class Scene:
 def __init__(self, name, title, subtitle):
  self.name, self.items = name, []
  SCENES.append(self)
  self.box(0,0,W,H,'#F7F9FC',None,0)
  self.text(48,32,1500,24,'MINI-SWE-AGENT / ARC-BENCH',13,BLUE,True)
  self.text(48,68,1500,50,title,34,INK,True)
  self.text(48,126,1500,30,subtitle,16,MUTED)
  self.box(48,1040,1504,1,LINE,None,0)
  self.text(48,1052,1460,22,'源码走读 + 本地归档轨迹  ·  2026-11-13  ·  原生可编辑 draw.io  ·  无 MCP',12,MUTED)
 def box(self,x,y,w,h,fill='white',stroke=LINE,radius=14):
  self.items.append(dict(kind='box',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,radius=radius))
 def text(self,x,y,w,h,text,size=16,color=INK,bold=False):
  self.items.append(dict(kind='text',x=x,y=y,w=w,h=h,text=text,size=size,color=color,bold=bold))
 def icon(self,x,y,name,color):
  self.items.append(dict(kind='icon',x=x,y=y,w=28,h=28,name=name,color=color))
 def panel(self,x,y,w,h,label,color=BLUE):
  self.box(x,y,w,h,'#FFFFFF',LINE)
  self.text(x+20,y+16,w-40,28,label,17,color,True)
 def card(self,x,y,w,h,title,lines,color=BLUE,icon='file'):
  self.box(x,y,w,h,'#FFFFFF',LINE,12)
  self.box(x,y,5,h,color,None,2)
  self.icon(x+17,y+18,icon,color)
  self.text(x+55,y+17,w-68,30,title,19,INK,True)
  self.text(x+18,y+59,w-36,h-65,'\n'.join(lines),15,MUTED)
 def edge(self,points,color=BLUE,dashed=False,label=None,lx=0,ly=0,lw=230):
  self.items.append(dict(kind='edge',points=points,color=color,dashed=dashed))
  if label:self.text(lx,ly,lw,25,label,13,color)

s=Scene('01 系统架构','从需求输入到可运行 Web 应用','当前源码 edcc3ae：adapter 准备任务；mini-SWE-agent 决策；bash 执行；验证记录提供可追溯证据。')
s.panel(48,190,280,592,'01  输入与任务准备')
s.card(66,248,244,126,'ARC-Bench 输入',['requirements.yaml 原文','reference/ 原始参考图片'],BLUE,'file')
s.card(66,414,244,150,'main.py',['参数 / .env / 模型选择','prepare_output() 补齐模板','build_info 记录源码身份'],BLUE,'layers')
s.card(66,600,244,154,'build_task()',['YAML + 工作流约束','参考图缩至 ≤1280px','原始素材留在工作目录'],BLUE,'file')
s.edge([(188,374),(188,414)])
s.edge([(188,564),(188,600)])
s.panel(366,190,590,592,'02  Agent 决策与执行',PURPLE)
s.card(390,248,280,146,'DefaultAgent',['messages 追加历史','query → execute_actions','每步保存 trajectory.json'],PURPLE,'cpu')
s.card(710,248,222,146,'LoggedModel',['LiteLLM + 重试','OpenAI 兼容端点','仅注册 bash 工具'],PURPLE,'cpu')
s.edge([(670,292),(710,292)],PURPLE)
s.edge([(710,350),(670,350)],PURPLE)
s.text(720,408,218,26,'模型返回 bash tool calls',13,PURPLE)
s.card(390,454,280,148,'LoggedEnvironment',['LocalEnvironment → Bash','固定应用目录 / pipefail','日志落盘 + 有限输出'],TEAL,'terminal')
s.edge([(524,394),(524,454)],TEAL,label='解析工具动作',lx=538,ly=418,lw=140)
s.edge([(390,550),(378,550),(378,326),(390,326)],PURPLE,True)
s.text(396,620,520,28,'observation → 下一轮模型请求',16,PURPLE,True)
s.text(396,660,520,70,'退出条件：提交标记、步数 / 时间上限、异常\nSubmitted 表示 agent 结束，评测结果单独记录。',15,MUTED)
s.edge([(310,675),(350,675),(350,300),(390,300)],BLUE)
s.panel(994,190,558,592,'03  生成应用与验证',TEAL)
s.card(1018,248,510,114,'React + Vite 前端',['页面 / 交互 / API 调用；构建生成 frontend/dist'],TEAL,'app')
s.card(1018,408,306,114,'Express 后端',['业务 API + 静态页面服务','会话 / 校验 / 数据访问'],TEAL,'app')
s.card(1360,408,168,114,'SQLite',['持久化存储','初始化 / 迁移'],TEAL,'db')
s.edge([(1170,362),(1170,408)],TEAL,label='HTTP /api',lx=1190,ly=374,lw=130)
s.edge([(1324,465),(1360,465)],TEAL)
s.card(1018,590,510,156,'构建、API 与浏览器自测',['run_check.py：--check / --case','scenario.cjs：逐场景 started → passed / failed / blocked','Playwright 经 bash 启动，结果回到 agent'],TEAL,'check')
s.edge([(670,515),(970,515),(970,552),(1272,552),(1272,590)],TEAL,label='bash 修改文件 / 启动服务 / 执行检查',lx=691,ly=523,lw=320)
s.panel(48,818,1504,196,'04  审计、部署与外部评测',ORANGE)
s.card(68,872,468,116,'模型与源码审计',['.arc_adapter/：calls / payloads / trajectory / summary','build_info：commit、源码 hash、运行配置'],ORANGE,'chart')
s.card(564,872,438,116,'命令与验证证据',['.agent/commands/：完整命令输出','checks.jsonl + coverage.json：最新执行状态'],ORANGE,'check')
s.card(1030,872,502,116,'应用交付与独立评测',['deploy.sh → build → Express；SQLite 数据持久化','平台测试独立执行；本地 baseline 脚本可串联官方测试'],ORANGE,'app')

s=Scene('02 真实运行轨迹','一次 run 实际如何完成','代表 run：ticket-booking / 68c7c302a985 / edcc3ae；对照 run：Ctrip / 135eb769a91b / 57cc284。')
for x,w,big,small,color in [(48,340,'44 次','逻辑模型调用；HTTP 尝试也是 44 次',BLUE),(410,340,'16.0 分钟','agent run_seconds = 961.45',PURPLE),(772,340,'2 / 2 场景','agent 自测最新覆盖状态',TEAL),(1134,418,'5 / 5 测试','归档平台 run.json；通过率 100%',TEAL)]:
 s.box(x,190,w,112,'white',LINE);s.text(x+22,207,w-44,45,big,29,color,True);s.text(x+22,264,w-44,24,small,14,MUTED)
s.panel(48,334,990,668,'真实轨迹：读取 → 实现 → 诊断 → 回归 → 提交',BLUE)
# Message indices are exact, zero-based trajectory.messages offsets, not model call numbers.
rows=[
 (402,'读取项目与验收约束','msg[2–15]','读取模板、后端 / 前端、run_check、场景助手与需求文件。','file',BLUE),
 (508,'实现全栈注册与登录','msg[17–39]','创建 users / sessions 表、认证校验、页面、样式和自测脚本。','layers',BLUE),
 (614,'失败驱动的诊断与修正','msg[41–61]','browser 未定义 → 修正作用域；标签匹配失败 → 修正表单语义。','terminal',ORANGE),
 (720,'源码修改后再次完整回归','msg[63–85]','多轮 build / backend / browser；最后记录 2 个场景 passed。','check',TEAL),
 (826,'提交完成；平台另行评测','msg[87–91]','检查最终项目；输出提交标记；平台归档结果为 5/5。','app',PURPLE),
]
for y,title,ref,body,ic,color in rows:
 s.box(76,y,52,52,'#F0F4FA',None,12);s.icon(88,y+11,ic,color)
 s.text(148,y-1,630,30,title,21,color,True);s.text(807,y+2,200,24,ref,14,MUTED)
 s.text(148,y+39,850,48,body,16,INK)
 if y<826:s.edge([(102,y+57),(102,y+99)],LINE)
s.text(76,943,920,35,'msg[n] 为 trajectory.messages 的零基下标；本 run 含 1 次无工具调用的格式错误，逻辑调用数与 assistant 消息数不同。',13,MUTED)
s.panel(1070,334,482,326,'同一架构内的生成应用',TEAL)
s.card(1090,392,442,80,'Home / Register / Login',[],TEAL,'app')
s.edge([(1310,472),(1310,500)],TEAL)
s.card(1090,500,260,134,'Express Auth API',['校验 / 密码处理 / 会话','注册、登录、退出'],TEAL,'terminal')
s.card(1374,500,158,134,'SQLite',['users','sessions'],TEAL,'db')
s.edge([(1350,567),(1374,567)],TEAL)
s.panel(1070,692,482,310,'对照：Ctrip 提交成功 ≠ 全部通过',ORANGE)
s.text(1092,750,438,42,'76 / 152',34,ORANGE,True)
s.text(1092,800,438,33,'平台测试通过；通过率 50%',19,INK,True)
s.text(1092,848,438,105,'较早版本 57cc284；97 次逻辑调用\nrun_seconds = 3078.66（51.3 分钟）\ntrajectory 与 summary 均为 Submitted\n评测数字来自独立的 run.json。',16,MUTED)

mx=E.Element('mxfile',host='app.diagrams.net',agent='local-python',version='24.7.17')
for page, scene in enumerate(SCENES,1):
 diagram=E.SubElement(mx,'diagram',id=f'page-{page}',name=scene.name)
 model=E.SubElement(diagram,'mxGraphModel',dx=str(W),dy=str(H),grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),math='0',shadow='0')
 root=E.SubElement(model,'root');E.SubElement(root,'mxCell',id='0');E.SubElement(root,'mxCell',id='1',parent='0')
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="context-stroke"/></marker></defs>']
 for n,item in enumerate(scene.items):
  a=item;k=a['kind'];id=f'p{page}-{n}'
  if k=='edge':
   pts=a['points'];style=f'edgeStyle=none;rounded=1;endArrow=block;endFill=1;strokeWidth=2;strokeColor={a["color"]};'+('dashed=1;' if a['dashed'] else '')
   cell=E.SubElement(root,'mxCell',id=id,style=style,edge='1',parent='1');g=E.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
   E.SubElement(g,'mxPoint',x=str(pts[0][0]),y=str(pts[0][1]),attrib={'as':'sourcePoint'});E.SubElement(g,'mxPoint',x=str(pts[-1][0]),y=str(pts[-1][1]),attrib={'as':'targetPoint'})
   arr=E.SubElement(g,'Array',attrib={'as':'points'})
   for x,y in pts[1:-1]:E.SubElement(arr,'mxPoint',x=str(x),y=str(y))
   svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{a["color"]}" stroke-width="2" stroke-linejoin="round" marker-end="url(#arrow)"'+(' stroke-dasharray="6 5"' if a['dashed'] else '')+'/>')
   continue
  x,y,w,h=(a[z] for z in ['x','y','w','h']);value=''
  if k=='box':
   stroke=a['stroke'] or 'none';style=f'rounded={int(a["radius"]>0)};arcSize=10;fillColor={a["fill"]};strokeColor={stroke};strokeWidth=1;'
   svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{a["radius"]}" fill="{a["fill"]}" stroke="{stroke}"/>')
  elif k=='text':
   value=a['text'];style=f'text;html=0;whiteSpace=wrap;overflow=hidden;align=left;verticalAlign=top;spacing=0;strokeColor=none;fillColor=none;fontFamily=PingFang SC;fontSize={a["size"]};fontColor={a["color"]};fontStyle={int(a["bold"])};'
   svg.append(f'<text x="{x}" y="{y+a["size"]}" font-family="PingFang SC,Arial,sans-serif" font-size="{a["size"]}" font-weight="{600 if a["bold"] else 400}" fill="{a["color"]}">')
   for j,line in enumerate(value.splitlines()):svg.append(f'<tspan x="{x}" dy="{0 if j==0 else a["size"]*1.5}">{html.escape(line)}</tspan>')
   svg.append('</text>')
  else:
   data=icon_svg(a['name'],a['color']);uri='data:image/svg+xml,'+__import__('urllib.parse',fromlist=['quote']).quote(data,safe='')
   style=f'shape=image;imageAspect=1;aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;image={uri};'
   svg.append(f'<g transform="translate({x} {y}) scale({w/24})" fill="none" stroke="{a["color"]}" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{ICONS[a["name"]]}</g>')
  cell=E.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1');E.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
 svg.append('</svg>');(OUT/f'{STEM}-{page:02}.svg').write_text('\n'.join(svg))
E.indent(mx);E.ElementTree(mx).write(OUT/f'{STEM}.drawio',encoding='utf-8',xml_declaration=True)
print(f'Built {len(SCENES)} pages in {OUT}')
