---
name: wechat-opening-banner
description: 给林月半子公众号文章做开头动画横幅（SVG）：GIF 头像与像素口号固定，后半段按文章主题生成剧情，输出可直接复制到公众号的 HTML。
---

# 公众号开头横幅

给「林月半子的AI笔记」每篇文章做一条 1246×220 的开头动画横幅，7 秒一轮：

- **固定部分（不要改）**：左侧头像 GIF（`GIF_URL_HERE` 占位，复制页里填公众号图库地址）；像素点阵口号「我是林月半子，教你用AI干掉90%的重复劳动」打出后散开。
- **每篇要换的部分**：口号散开后的后半段。用**插画式小物件**讲文章的故事：物件一个个「蹦」出来（0 → 放大 → 回弹），之间用连接线串起来，最后挂绿色对勾。少用文字，标签只写 2–7 个字。

最终交付 `<slug>-复制到公众号.html`：用 Chrome 打开 → 填一次 GIF 地址（会记住）→ 点「复制到公众号」→ 去公众号编辑器粘贴。

## 步骤

1. **读文章**，提炼：起点（用户交代了什么 / 输入是什么）、谁在干活（Agent、Skill、工具）、产出了哪几样东西或哪几个节点。全部取自原文，不编数字、不编功能。
2. **先定风格**（一共四种，用户没说就问一下）：`poster` 大字海报和 `neo` 质感是按手机可读设计的新风格，见「风格三 / 风格四」，选了就跳过下面的场景模板。
   其余两种：默认是「头像 + 像素口号 + 场景动画」；用户要标题卡时用 `card` 风格（见「风格二」，右栏 12 种版式），跳过下面的场景模板。
   **按文章类型选场景模板**（见下），不要每篇都用同一个，也尽量别和上一篇重复；拿不准时出两个版本让用户挑。速查：
   - 工具替你产出一批东西 → `pipeline`；一句话出结果的演示 → `dialog`
   - 效率对比（以前/现在）→ `before_after`；有真实数字 → `chart`
   - 一个入口管很多事 → `hub`；多个模块拼成一个产品 → `stack`
   - 长期跟进、按时间推进 → `path`；每天/每周自动跑 → `calendar`
   - 丢进去它就开始干活 → `fly`；从一堆信息里挑重点 → `funnel`
3. **写 `spec.json`**，然后直接运行 skill 目录里的脚本，不要读脚本源码，也不要把它抄一遍：
   `python3 <skill 目录>/scripts/banner.py spec.json out`
4. **看命令打印的自查结果**。脚本会检查每个标签的字数、物件数量有没有超限、有没有公众号会吞掉的写法。
   - 打印「自查通过」就可以交付。
   - 打印「要改的地方」就按提示改 `spec.json` 再跑一次。
   - **默认不截图**。用户说「截图看看」时才截，截 6.3 秒那一帧（默认风格）或 5 秒那一帧（标题卡），最多一张。
5. **交付** HTML，一句话说明剧情，提醒用 Chrome 直接打开（聊天窗口预览里写不了剪贴板）。

**省时规则**：示例都在 `examples/` 里，只在不确定某个模板的字段时看对应的那一个，不要全部读一遍。

## 十种场景模板

### 1. `pipeline` 流水线：输入 → 干活的 → 一排产出
适合：工具替你做出一批东西（剪辑、生成、整理、写作、设计）。

```json
{"slug":"chatcut","title":"开头横幅 · ChatCut 2.0","caption":"ChatCut 2.0 实测",
 "scene":{"layout":"pipeline",
   "source":{"prop":"chat","label":"一句大白话"},
   "processor":{"prop":"clapper","label":"剪辑 Skill"},
   "tile":"film",
   "items":[{"icon":"person","label":"我的照片"},{"icon":"cup","label":"商品图"},{"icon":"mic","label":"口播剪辑"},{"icon":"play","label":"成片"}]}}
```

- `source`（可省略）：`{"prop":"chat"}` 聊天窗口，气泡一条条冒出；或 `{"prop":"start","icon":"bell"}` 圆形图标。
- `processor.prop`：`clapper` 场记板（会打板）、`robot` 方块机器人（抱着笔记本、眨眼、头顶冒对勾）、`computer` 复古电脑（屏幕亮起）、`phone` 手机。
- `tile`：`film` 胶片帧（最多 4 个，适合视频/画面类）、`card` 小卡片（最多 5 个，适合文档/任务/功能类）。
- 省略 `source` 时，产出区更宽，可放 5 张卡片（例：机器人 + 5 张功能卡）。

### 2. `path` 路线：一条波浪线画出来，沿途节点逐个点亮
适合：长期跟进、按时间推进、一步步完成的事（提醒、助理、日程、学习计划、工作流）。

```json
{"slug":"lingguang","title":"开头横幅 · 灵光 2.0","caption":"灵光 2.0 实测",
 "scene":{"layout":"path","start_icon":"bell","start_label":"交代一次",
   "nodes":[{"icon":"sun","label":"06:00 吃药"},{"icon":"pill","label":"14:30 再催"},{"icon":"wallet","label":"12/01 巡检扣费"},{"icon":"train","label":"出发前看车次"},{"icon":"moon","label":"没变化不打扰","check":false}]}}
```

- 节点 3–5 个，上下交替排布；`"check": false` 表示这个节点不打勾（如「还在盯」「安静待命」）。

### 3. `fly` 飞入：一个小物件拖着光尾飞进电脑/手机，屏幕亮起，再弹出结果
适合：「交代一次 / 丢一个东西进去，它就开始干活」的主题。

```json
{"slug":"lingguang-fly","title":"开头横幅 · 灵光（飞入版）","caption":"灵光 2.0 实测",
 "scene":{"layout":"fly","flyer":"pill","left_label":"交代一次","device":"computer","device_label":"它记着、盯着",
   "screen":["bell","calendar","wallet"],
   "items":[{"icon":"pill","label":"到点提醒"},{"icon":"bell","label":"没回再催"},{"icon":"wallet","label":"每月巡检"}]}}
```

- `device`：`computer` 或 `phone`；`screen` 最多 3 个图标，在屏幕上蹦出来；`items` 最多 4 张卡片（可省略，省略时设备放在最右）。

### 4. `before_after` 前后对比：一堆乱活抖一抖 → 箭头 → 一排整齐成品
适合：「以前手动 X，现在一句话 Y」的效率对比文章。

```json
{"slug":"chatcut-ba","title":"开头横幅 · ChatCut","caption":"ChatCut 2.0 实测",
 "scene":{"layout":"before_after","before_label":"以前：素材一堆手动剪","before":["photo","mic","text","music","scissors","play"],
   "via":{"icon":"chat","label":"一句话"},"after_label":"现在：一句话出片",
   "items":[{"icon":"mic","label":"口播初剪"},{"icon":"text","label":"字幕包装"},{"icon":"music","label":"配乐压低"},{"icon":"play","label":"成片"}]}}
```
- `before` 最多 7 个图标（乱堆的纸片）；`items` 最多 4 张卡；两个标题各 ≤10 字。

### 5. `hub` 中心发散：中心亮起、脉冲扩散，周围能力一个个连上来
适合：「一个入口 / 一个 Agent 管很多事」。

```json
{"scene":{"layout":"hub","center":{"icon":"spark","label":"交代一次就行"},
  "nodes":[{"icon":"pill","label":"吃药提醒"},{"icon":"wallet","label":"扣费巡检"},{"icon":"train","label":"出发看车次"},
           {"icon":"calendar","label":"日程"},{"icon":"bell","label":"没回再催"},{"icon":"moon","label":"不打扰","check":false}]}}
```
- 节点 2–6 个，偶数（4 或 6）最对称。

### 6. `stack` 搭积木：模块一块块掉进托盘，框起来，箭头指向一个成品
适合：多个 Skill / 插件 / 步骤组合成一个完整东西。

```json
{"scene":{"layout":"stack","label":"一个个 Skill",
  "blocks":[{"icon":"doc","label":"写稿"},{"icon":"text","label":"起标题"},{"icon":"photo","label":"配图"},{"icon":"image","label":"封面"},{"icon":"code","label":"排版"},{"icon":"mail","label":"发布"}],
  "result":{"icon":"play","label":"公众号写作驾驶舱"}}}
```
- `blocks` 2–6 块，块内文字 ≤5 字；先填下排再填上排。

### 7. `dialog` 对话来回：你一句、它先「…」再回一句，最后交付成品卡
适合：「跟 AI 说几句话就做完了」的演示类文章。

```json
{"scene":{"layout":"dialog","window_title":"ChatCut",
  "messages":[{"from":"me","text":"把这段口播剪一下"},{"from":"ai","text":"收到，粗剪完成"},{"from":"me","text":"配乐再小一点"},{"from":"ai","text":"已调好，正在导出"}],
  "items":[{"icon":"play","label":"成片"},{"icon":"text","label":"字幕"},{"icon":"image","label":"封面"}]}}
```
- `messages` 最多 4 条，每条 ≤12 字；`items` 最多 3 张，可省略。

### 8. `calendar` 一周打卡：设一次，日历卡片逐天被盖章
适合：每天 / 每周自动跑的事（提醒、日报、定时发布）。

```json
{"scene":{"layout":"calendar","start_icon":"bell","start_label":"交代一次","stamp":"已提醒",
  "days":[{"day":"周一","icon":"pill"},{"day":"周二","icon":"pill"},{"day":"周三","icon":"train"},{"day":"周四","icon":"pill"},
          {"day":"周五","icon":"wallet"},{"day":"周六","icon":"sun"},{"day":"周日","icon":"moon","stamp":"休息"}]}}
```
- `days` 3–7 个，`day` 可写日期（如「11/03」）；章文字 2–3 字，单天可用 `"stamp"` 覆盖，`"stamp": ""` 表示不盖章；每天可加 `label` 显示在卡片下方。

### 9. `funnel` 漏斗筛选：一堆信息块飞进漏斗，出口只出几张重点卡
适合：信息过滤、总结、提炼（群聊日报、邮件筛选、资讯摘要）。

```json
{"scene":{"layout":"funnel","input_label":"群里一天几百条","filter_label":"只挑重点",
  "inputs":["chat","chat","photo","chat","mail","chat","doc","chat","photo","chat"],
  "items":[{"icon":"doc","label":"今日日报"},{"icon":"bell","label":"@我的事"},{"icon":"spark","label":"值得看"}]}}
```
- `inputs` 最多 10 个图标；`filter_label` ≤5 字（写在漏斗上）；`items` 最多 3 张。

### 10. `chart` 数据对比：柱子依次长高，右侧弹出结论大字卡
适合：文章里**有真实数字**的对比（耗时、数量、成本）。没有数字就别用这个模板。

```json
{"scene":{"layout":"chart",
  "bars":[{"label":"手动","value":180,"text":"3 小时"},{"label":"用 Skill","value":10,"text":"10 分钟","color":"teal"}],
  "badge":{"icon":"spark","label":"省 94%","sub":"同一条视频的剪辑时间"}}}
```
- `bars` 2–6 根，`value` 决定高度，`text` 写在柱顶；默认最后一根橙色、其余灰色，可用 `color`: gray / teal / orange / blue；`badge.label` 是大字结论（≤6 字），`sub` 一行小字。
- 数字必须出自文章原文。

### 公共字段
- `caption`：右上角一行小字，一般写「产品名 + 实测」。
- 每个 `label` 2–7 个字最好，最长不超过 8 个字；路线节点可以带时间（如「06:00 吃药」）。

### 可用图标（`icon` / `flyer` / `screen` / `start_icon`）
`sun` 太阳 · `moon` 月亮 · `paw` 爪印 · `pin` 定位 · `pill` 药丸 · `bell` 铃铛 · `wallet` 钱包/扣费 · `calendar` 日历 · `train` 火车/出行 · `doc` 文档 · `scissors` 剪刀 · `music` 音乐 · `text` 字幕/文字 · `play` 播放/成片 · `chart` 图表 · `person` 人物 · `photo` 图片 · `cup` 饮品/商品 · `chat` 对话 · `mic` 麦克风/口播 · `mail` 邮件 · `spark` 灵感/AI · `code` 代码

需要新图标时，在 `_icon()` 里按同样方式加一个 28px 左右、以 (0,0) 为中心的简单图形；颜色只用脚本顶部的调色板。

## 风格二：`card` 标题卡

整张横幅是一块浅色圆角卡片，尺寸 1246×420，比默认风格高。

- **左栏（每篇都一样的结构）**：眉标 → 两行大标题（一黑一主题色）→ 强调短条 → 副标题 → 左下角头像署名加口号。
- **右栏**：有 12 种版式，按文章内容挑。

动画只在入场时播一次，约 4 秒，播完停在最终画面。之后只保留几个小循环：眉标脉冲、按钮扫光、多卡片轮流高亮、播放头或取景框扫过、悬浮卡上下浮动、光标闪烁。

适合：用户点名要「标题卡 / card」，或者想把文章标题直接放进横幅、要「封面感」的时候。没点名就用默认风格。

### 左栏字段（所有版式通用）
```json
{"slug":"card-xxx","title":"开头横幅 · 标题卡 · XXX","style":"card",
 "card":{"theme":"blue","eyebrow":"PRODUCT · TOPIC","title1":"第一行黑字","title2":"第二行主题色","sub":"关键词 · 关键词 · 关键词",
         "right":"tree", "...右栏字段...": "..."}}
```
- `theme`：默认不写，复制页会同时出蓝、品牌橙、绿三个版本，每个版本有自己的复制按钮，让用户自己挑；写了 `blue` / `orange` / `teal` 就只出那一种。
- `eyebrow`：≤26 字符。
- `title1` / `title2`：每行 ≤9 个汉字。
- `sub`：一句话或 3–4 个关键词，≤20 字。
- `avatar`：默认 `true`，显示头像署名和口号。设为 `false` 时改显示 `foot` 一行灰字，复制页也不用再填 GIF。

### 右栏 12 种版式（`right`）

| `right` | 画面 | 适合 | 字段 |
|---|---|---|---|
| `steps` | 2–4 张步骤卡连线，下面是结论按钮和流程字 | 通用：几步做成一件事 | `steps:[{icon,label}]`, `result`, `flow?` |
| `remix` | 源卡 → 高亮改造卡 → 结果卡，折线连到镜头轨道（播放头会扫过） | 复刻、改编、模板二创、视频生成 | `cards:[{title,art:"nodes"/"image"/图标名}, {title,sub,hl:true}, {title,art}]`, `track_label?`, `track?:[比例]`, `caption` |
| `pick` | 6 张灰色平均方案 → 圆圈「选」→ 一张歪着的高亮卡（会浮动） | 观点文：审美、判断、取舍 | `grid_label`, `pick`, `pick_label`, `card_title1`, `card_title2`, `caption` |
| `timeline` | 竖线串起 2–4 张卡片，轮流高亮，底部小按钮 | 时间顺序、记忆、长期陪伴、阶段 | `items:[{title,desc}]`, `result?` |
| `converge` | 编号卡并排，括号线汇到底部大框 | 多个能力汇成一个平台或底座 | `caption`, `cards:[{num,icon,label}]`, `box_title`, `box_sub` |
| `tree` | 一句话胶囊分叉成 2×2 功能卡（轮流高亮），下面是按钮 | 一个入口做出很多东西 | `head`, `items:[{icon,title,desc}]×4`, `result` |
| `compare` | 顶部横条分叉成 2–4 张对比卡（轮流高亮），下面是按钮 | 横评、同题对比、多模型 | `caption`, `head`, `items:[{icon,label}]`, `result` |
| `storyboard` | 角色卡（可用你的 GIF 头像）→ 分镜面板，取景框扫过三格 → 流程按钮 | 短剧、视频、分镜、角色 | `caption`, `who:{avatar:true 或 icon,label}`, `shots:[{icon,label}]×3`, `flow:[...]` |
| `chat` | 聊天窗口里来回几句（AI 先显示「…」），箭头指向交付卡 | 「说几句话就做完」的演示 | `window_title?`, `messages:[{from:"me"/"ai",text}]≤4`, `result_icon`, `result_title`, `result_sub`, `caption` |
| `stats` | 2–3 张大数字卡，下划线长出来，最后一张高亮，下面是按钮 | 有真实数字的前后对比 | `caption`, `items:[{label,value,note?,hl?}]`, `result` |
| `checklist` | 待办清单逐项打勾，进度条走满 | 助理、自动化、替你盯事 | `title`, `items:["…"]≤5`, `done?`, `caption` |
| `terminal` | 深色终端，命令一行行出现，最后亮绿勾，光标闪烁 | Claude Code、命令行、开发者工具 | `title`, `lines:[{type:"cmd"/"out"/"ok",text}]≤6`, `caption` |

- `stats` 的数字必须出自文章原文。
- 文字长度：卡片标题 ≤8 字，描述 ≤12 字，按钮和 caption ≤18 字，聊天每条 ≤12 字，终端每行 ≤34 字符。
- 线条图标：`grid` `code` `play` `doc` `lines` `chat` `spark` `image` `mic` `music` `bell` `calendar` `chart` `mail` `person` `cube` `game` `scissors` `text` `wand` `robot` `web` `home` `dice` `box` `layers` `monitor` `heart` `film`；分镜专用 `scene_wide` `scene_mid` `scene_close`。
- 选版式时也尽量别和上一篇重复。拿不准就出两个版本让用户挑。
- 每种版式的完整示例在 `examples/card-*.json`。

## 风格三：`poster` 大字海报　风格四：`neo` 质感

这两种是**按手机可读设计的**：一条横幅只放 2–3 个元素，标题 80px，最小的字也有 30px（手机上约 9px）。默认风格和标题卡上的小标签在手机上很难看清，想让读者在手机上一眼看懂时用这两种。

- `poster`：浅色圆角卡，左边眉标 + 两行大标题 + 头像署名，右边一组大元素。尺寸 1246×460。
- `neo`：同样的结构，换成白卡、细线描边、柔和阴影、淡色巨型数字底纹，眉标是深色胶囊，第二行标题是色块白字。尺寸 1246×484。和排版的「质感」风格成套。不要用实色错位投影和粗黑描边。

两种的字段完全一样，只有 `style` 不同。动画入场播一次后停住。默认品牌橙、蓝、绿三色一起出。

```json
{"slug":"poster-chatcut","title":"开头横幅 · 大字海报 · ChatCut","style":"poster",
 "poster":{"eyebrow":"CHATCUT 2.0 实测","title1":"剪辑提示词写不好","title2":"交给视频 Agent",
   "right":"flow","ask":"帮我剪一下口播","result":"成片好了","result_sub":"20 秒剪到 14 秒",
   "tags":["AI 广告","口播剪辑","复刻爆款"],"big":"2.0"}}
```

- `eyebrow` ≤10 个字宽（英文算半个）；`title1` / `title2` 每行 ≤8 个汉字，超了会自动缩小字号。
- `big`：只有 `neo` 用，右下角的巨型底纹字，1–2 个字符最好（版本号、数字、「AI」）。不写就没有底纹。
- `avatar`：默认 `true`。
- 右栏 `right` 四选一：

| `right` | 画面 | 字段 |
|---|---|---|
| `flow` | 一句话气泡 → 箭头 → 结果卡（带对勾） | `ask` ≤9 字，`result` ≤6 字，`result_sub` ≤9 字（可省） |
| `tags` | 3 张关键词贴纸，中间一张高亮 | `tags`：2–3 个，每个 ≤6 字 |
| `steps` | 3 行编号步骤，最后一行高亮 | `steps`：2–3 条，每条 ≤8 字 |
| `stat` | 一个大数字或大词 | `label` 上方小字，`value` ≤5 字，`note` 下方一行。数字必须出自原文 |

- 不写 `right` 时：`poster` 用 `flow`；`neo` 有 `tags` 就用 `tags`，否则用 `flow`。
- 建议 `ask`/`result` 和 `tags` 都写上：通过排版 skill 生成时，正文切到质感风格，横幅会自动换成 `neo` 版。
- 示例在 `examples/poster-*.json` 和 `examples/neo-*.json`。

## 设计规则

- 物件一个接一个蹦出，最后再挂对勾，节奏是「先出东西，再确认完成」。
- 颜色：绿（`TEAL`）= 完成、通过；橙 = 品牌强调、播放；藏青/金 = 图标点缀。背景透明，放在公众号浅灰底上。
- 不画任何产品 logo 或品牌角色；产品名只出现在 `caption` 和标签里。
- 文字只做标签，不写长句。

## 公众号限制（脚本已处理，改脚本时别破坏）

- 只用 SMIL（`<animate>`/`<animateTransform>`）；不能用 `<script>`、`<style>`、`id`、`class`、渐变、`<use>`、`clipPath`、`mask`。
- 头像只能用公众号图库地址（`https://mmbiz.qpic.cn/...`）。base64 已实测，公众号不显示。
- 像素口号用点阵数据画，不依赖字体。

## 脚本

`scripts/banner.py` 已经写好、测过，直接运行。只有命令报错时才去看报错的那一段代码。需要加新图标或新模板时再改它。
