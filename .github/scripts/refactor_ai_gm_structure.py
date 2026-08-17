from pathlib import Path
import hashlib
import os
import re

ROOT = Path('.')


def read(path: str) -> str:
    return Path(path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')


def find(text: str, marker: str) -> int:
    pos = text.find(marker)
    if pos < 0:
        raise RuntimeError(f'marker not found: {marker}')
    return pos


MD_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')


def relocate_links(text: str, old_path: str, new_path: str) -> str:
    """Preserve local Markdown link targets when moving prose to another directory."""
    old_parent = Path(old_path).parent
    new_parent = Path(new_path).parent

    def repl(match: re.Match) -> str:
        label, raw = match.group(1), match.group(2).strip()
        if not raw or '://' in raw or raw.startswith('#') or raw.startswith('mailto:'):
            return match.group(0)
        if raw.startswith('<') and raw.endswith('>'):
            return match.group(0)
        target, sep, anchor = raw.partition('#')
        if not target or '<' in target or '>' in target:
            return match.group(0)
        resolved = (old_parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            return match.group(0)
        rel = os.path.relpath(resolved, start=new_parent.resolve()).replace(os.sep, '/')
        result = rel + (sep + anchor if sep else '')
        return f'{label}({result})'

    return MD_LINK_RE.sub(repl, text)


def module(title: str, body: str, note: str, old_path: str, new_path: str) -> str:
    body = relocate_links(body.strip(), old_path, new_path)
    lines = body.splitlines()
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
        body = '\n'.join(lines).lstrip()
    return f'# {title}\n\n> {note}\n\n{body}\n'


# ---------------------------------------------------------------------------
# 60 KB script-design monolith -> stable router + 4 semantic modules.
# ---------------------------------------------------------------------------
old = '劇本設計規則/設計.md'
text = read(old)
a = find(text, '# 第一部分：因果倒推式設計')
b = find(text, '# 第二部分：把世界模型變成可跑模組')
c = find(text, '# 第三部分：正式模板')
parts = [
    ('劇本設計規則/設計/基礎規格與能力.md', '劇本設計：基礎規格與角色能力', text[:a],
     '承接原 `劇本設計規則/設計.md` 第 0–4 節；章節編號保留，舊引用可由路由定位。'),
    ('劇本設計規則/設計/因果與調查.md', '劇本設計：因果倒推與調查', text[a:b],
     '承接原第 5–14 節，處理世界真相、人物認知、線索、反轉與調查結構。'),
    ('劇本設計規則/設計/場景遭遇與獎勵.md', '劇本設計：場景、遭遇與獎勵', text[b:c],
     '承接原第 15–23 節，處理場景、遭遇、非戰鬥挑戰、獎勵、危機與偏離。'),
    ('劇本設計規則/設計/模板與流程.md', '劇本設計：正式模板與設計流程', text[c:],
     '承接原第 24–29 節及核心公式，供正式交付與最後組裝使用。'),
]
for new, title, body, note in parts:
    write(new, module(title, body, note, old, new))
write(old, '''# 劇本設計規則：設計（讀取路由）

本檔只負責**載入路由與舊章節定位**；具體設計規則已按工作性質拆成四個權威模組。這樣可避免 AI／GM 為了查一個規則而一次載入整份六萬字元文件。

| 原章節 | 權威模組 | 主要用途 |
|---|---|---|
| 0–4 | [`設計/基礎規格與能力.md`](設計/基礎規格與能力.md) | 交付形式、規格頭、NPC／連續性、世界與內容庫引用、角色能力影響 |
| 5–14 | [`設計/因果與調查.md`](設計/因果與調查.md) | 世界真相、人物認知、因果痕跡、線索網、反轉、調查 |
| 15–23 | [`設計/場景遭遇與獎勵.md`](設計/場景遭遇與獎勵.md) | 場景、戰鬥／非戰鬥遭遇、獎勵、歷練、危機、動態 NPC、偏離 |
| 24–29、核心公式 | [`設計/模板與流程.md`](設計/模板與流程.md) | 正式模板、建議設計流程與公式 |

**完整創作一份新劇本時，四個模組都要讀；查核或修正單一問題時，只讀與該問題相符的模組。** 舊文件若寫「`設計.md` 第 18.8 節」，先讀本路由，再到「場景、遭遇與獎勵」模組找同號章節；章節編號沒有因拆檔改變。
''')


# ---------------------------------------------------------------------------
# 54 KB GM runtime monolith -> stable router + 6 execution modules.
# ---------------------------------------------------------------------------
old = 'GM規則/遊戲流程.md'
text = read(old)
s21 = find(text, '### 2.1 AI GM 遊戲狀態與持久化存檔')
s3 = find(text, '## 3. 《武與俠》判定使用')
s7 = find(text, '## 7. NPC與社交')
s10 = find(text, '## 10. 戰鬥主持')
s14 = find(text, '## 14. 玩家偏離劇本與任務邊界')
parts = [
    ('GM規則/遊戲流程/基本主持.md', 'GM遊戲流程：基本主持', text[:s21],
     '劇本內循環入口與基本主持節奏；與本局存檔規則分拆以降低常駐上下文。'),
    ('GM規則/遊戲流程/遊戲狀態與存檔.md', 'GM遊戲流程：遊戲狀態與存檔', text[s21:s3],
     '原第 2.1 節完整移入此檔；只在建立、保存、暫停、續跑或恢復 game save 時必須載入。'),
    ('GM規則/遊戲流程/判定與調查.md', 'GM遊戲流程：判定與調查', text[s3:s7],
     '承接原第 3–6 節；處理可行性、擲骰鎖定、重試、玩家自主權、資訊與調查。'),
    ('GM規則/遊戲流程/NPC社交與內容庫.md', 'GM遊戲流程：NPC、社交與內容庫', text[s7:s10],
     '承接原第 7–9 節；NPC 姓名、社交、名譽與內容庫引用集中於此。'),
    ('GM規則/遊戲流程/戰鬥資源與世界推進.md', 'GM遊戲流程：戰鬥、資源與世界推進', text[s10:s14],
     '承接原第 10–13 節；配合 `遊玩規則/遊玩流程/` 的權威機械使用。'),
    ('GM規則/遊戲流程/偏離資訊邊界與即場生成.md', 'GM遊戲流程：偏離、資訊邊界與即場生成', text[s14:],
     '承接原第 14–16 節及核心原則；只在偏離、線索斷裂、資訊邊界或即場生成時載入。'),
]
for new, title, body, note in parts:
    write(new, module(title, body, note, old, new))
write(old, '''# GM規則：遊戲流程（讀取路由）

本檔是已開局／續跑劇本的**AI GM 執行路由**。具體主持規則已拆成小模組；不要在每個回合一次載入全部模組。

| 原章節 | 模組 | 何時讀 |
|---|---|---|
| 1、2（不含 2.1） | [`遊戲流程/基本主持.md`](遊戲流程/基本主持.md) | 進入劇本內循環、一般回合主持 |
| 2.1 | [`遊戲流程/遊戲狀態與存檔.md`](遊戲流程/遊戲狀態與存檔.md) | 開始／續跑、保存、暫停、恢復、存檔衝突 |
| 3–6 | [`遊戲流程/判定與調查.md`](遊戲流程/判定與調查.md) | 玩家行動、判定、重試、調查、資訊取得、PvP／裁定異議 |
| 7–9 | [`遊戲流程/NPC社交與內容庫.md`](遊戲流程/NPC社交與內容庫.md) | NPC、社交、名譽、內容庫引用 |
| 10–13 | [`遊戲流程/戰鬥資源與世界推進.md`](遊戲流程/戰鬥資源與世界推進.md) | 戰鬥主持、資源／休息、失敗向前、時間與危機 |
| 14–16、核心原則 | [`遊戲流程/偏離資訊邊界與即場生成.md`](遊戲流程/偏離資訊邊界與即場生成.md) | 偏離任務、不可回復線索斷裂、GM 資訊邊界、即場 NPC／物件 |

開始或續跑時至少讀「基本主持」及「遊戲狀態與存檔」。之後依當前行動載入對應模組；戰鬥／探索／整備的具體玩家機械仍由 [`../遊玩規則/遊玩流程/README.md`](../遊玩規則/遊玩流程/README.md) 路由。

舊引用如「`GM規則/遊戲流程.md` 第 3.3 節」仍有效：先由本表定位「判定與調查」，再讀同號章節。章節號沒有因拆檔改變。
''')


# ---------------------------------------------------------------------------
# 30 KB settlement -> router + 3 fixed-sequence modules.
# ---------------------------------------------------------------------------
old = 'GM規則/結算.md'
text = read(old)
q6 = find(text, '## 6. 歷練、社會名譽、升級與其他持續後果')
q8 = find(text, '## 8. 玩家可見結算憑證')
parts = [
    ('GM規則/結算/結局參與與物質.md', 'GM結算：結局、參與與物質', text[:q6],
     '承接原第 1–5 節；先凍結來源、確認結局、參與資格、財產與特殊傷患。'),
    ('GM規則/結算/歷練名譽與履歷.md', 'GM結算：歷練、名譽與履歷', text[q6:q8],
     '承接原第 6–7 節；所有歷練、社會名譽、升級與江湖履歷計算集中於此。'),
    ('GM規則/結算/憑證更新與關閉.md', 'GM結算：憑證、角色卡更新與關閉', text[q8:],
     '承接原第 8–10 節；處理玩家可見憑證、角色卡更新窗口、校正、交付與存檔清理。'),
]
for new, title, body, note in parts:
    write(new, module(title, body, note, old, new))
write(old, '''# GM規則：結算（讀取路由）

結算仍是一個固定順序的獨立階段，但原單檔已拆成三個權威模組，讓 AI GM 可以**逐段完成、逐段驗證**，不用同時持有整份結算正文。

依序讀取並完成：

1. [`結算/結局參與與物質.md`](結算/結局參與與物質.md) — 原第 1–5 節。
2. [`結算/歷練名譽與履歷.md`](結算/歷練名譽與履歷.md) — 原第 6–7 節。
3. [`結算/憑證更新與關閉.md`](結算/憑證更新與關閉.md) — 原第 8–10 節。

三個模組共同構成完整結算權威規則，**不得只讀最後一檔便直接寫回角色卡**。舊引用到 `GM規則/結算.md` 某節時，依上列原章節範圍定位；章節號保留不變。
''')


# ---------------------------------------------------------------------------
# 25 KB advancement -> router + 3 semantic modules.
# ---------------------------------------------------------------------------
old = '遊玩規則/角色/升級與武學成長.md'
text = read(old)
u2 = find(text, '## 2. 外功等級點')
u4 = find(text, '## 4. 取得與修習新武學')
parts = [
    ('遊玩規則/角色/升級與武學成長/歷練與升級.md', '升級與武學成長：歷練與升級', text[:u2],
     '承接原第 1 節；歷練 tag、升級門檻、等級差折算、履歷、重跑與連續性集中於此。'),
    ('遊玩規則/角色/升級與武學成長/外功與等級進程.md', '升級與武學成長：外功與等級進程', text[u2:u4],
     '承接原第 2–3 節；處理外功等級點及基礎等級進程摘要。'),
    ('遊玩規則/角色/升級與武學成長/武學來源與修習.md', '升級與武學成長：武學來源與修習', text[u4:],
     '承接原第 4 節；師承、秘笈、殘本、來源上限、失效、入門與修習集中於此。'),
]
for new, title, body, note in parts:
    write(new, module(title, body, note, old, new))
write(old, '''# 升級、歷練與武學成長（讀取路由）

本檔只作成長規則路由；原章節號保留於三個權威模組：

- 第 1 節：[`升級與武學成長/歷練與升級.md`](升級與武學成長/歷練與升級.md)
- 第 2–3 節：[`升級與武學成長/外功與等級進程.md`](升級與武學成長/外功與等級進程.md)
- 第 4 節：[`升級與武學成長/武學來源與修習.md`](升級與武學成長/武學來源與修習.md)

結算只需要計算歷練／升級時先讀第一、第二模組；只有取得、修習、失去或變更武學來源時才讀第三模組。舊引用到本檔某節時，依章節範圍定位即可。
''')


# ---------------------------------------------------------------------------
# Sixteen sects: keep index/table in old path, split individual sect details.
# Preserve old heading anchors as routing stubs.
# ---------------------------------------------------------------------------
old = '世界知識庫/勢力/門派.md'
text = read(old)
matches = list(re.finditer(r'^## ([^\n]+)$', text, flags=re.M))
first = next(i for i, m in enumerate(matches) if m.group(1).strip() == '禪林寺')
prefix = text[:matches[first].start()].rstrip()
sects = matches[first:]
stubs = []
for i, m in enumerate(sects):
    name = m.group(1).strip()
    end = sects[i + 1].start() if i + 1 < len(sects) else len(text)
    body = text[m.end():end].strip()
    new = f'世界知識庫/勢力/門派/{name}.md'
    body = relocate_links(body, old, new)
    write(new, f'# {name}\n\n> 本檔是 `世界知識庫/勢力/門派.md` 索引下的單一門派權威條目。\n\n{body}')
    stubs.append(f'## {name}\n\n完整條目：[{name}](門派/{name}.md)')
write(old, prefix + '\n\n' + '\n\n'.join(stubs))


# ---------------------------------------------------------------------------
# Internal-arts catalogue: old path becomes anchor-preserving index.
# ---------------------------------------------------------------------------
old = '內容庫/武學/內功.md'
text = read(old)
matches = list(re.finditer(r'^## (【([^】]+)】[^\n]*)$', text, flags=re.M))
if not matches:
    raise RuntimeError('no internal arts found')
prefix = text[:matches[0].start()].rstrip()
stubs = []
for i, m in enumerate(matches):
    display = m.group(1).strip()
    name = m.group(2).strip()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    body = text[m.end():end].strip()
    new = f'內容庫/武學/內功/{name}.md'
    body = relocate_links(body, old, new)
    write(new, f'# {display}\n\n> 本檔是 `內容庫/武學/內功.md` 索引下的單一內功權威條目。\n\n{body}')
    stubs.append(f'## {display}\n\n完整條目：[{name}](內功/{name}.md)')
write(old, prefix + '\n\n## 內功條目索引\n\n' + '\n\n'.join(stubs))


# ---------------------------------------------------------------------------
# High-level feats: split by acquisition tier; index retains feat-name anchors.
# ---------------------------------------------------------------------------
old = '內容庫/高等絕活.md'
text = read(old)
tiers = list(re.finditer(r'^# (\d+級高等絕活)$', text, flags=re.M))
if not tiers:
    raise RuntimeError('no high-level feat tiers found')
prefix = text[:tiers[0].start()].rstrip()
index_chunks = []
for i, m in enumerate(tiers):
    title = m.group(1)
    level = re.match(r'(\d+)級', title).group(1)
    end = tiers[i + 1].start() if i + 1 < len(tiers) else len(text)
    body = text[m.start():end].strip()
    new = f'內容庫/高等絕活/{level}級.md'
    body = relocate_links(body, old, new)
    lines = body.splitlines()
    lines.insert(1, '')
    lines.insert(2, '> 本檔是 `內容庫/高等絕活.md` 索引下的分級權威條目。')
    write(new, '\n'.join(lines))
    feat_names = [x.group(1).strip() for x in re.finditer(r'^## ([^\n]+)$', body, flags=re.M)]
    chunk = [f'# {title}', '', f'完整分級條目：[{title}](高等絕活/{level}級.md)']
    for feat in feat_names:
        chunk += ['', f'## {feat}', '', f'完整條目見：[{title}](高等絕活/{level}級.md#{feat})']
    index_chunks.append('\n'.join(chunk))
write(old, prefix + '\n\n' + '\n\n'.join(index_chunks))


# ---------------------------------------------------------------------------
# Retired duplicate rulebooks -> compatibility routers only.
# ---------------------------------------------------------------------------
write('GM規則/可重覆小型副本.md', '''# 可重覆小型副本（舊路徑相容）

本檔已退役，**不再保存另一套主持規則**。現行可重覆內容統一使用 [`可重覆任務.md`](可重覆任務.md)。

若舊劇本仍寫「可重覆小型副本」，先按遷移／相容需要確認其實際運行類別，再依現行 `可重覆任務.md` 主持；不得以本舊檔覆蓋新規則。
''')
write('劇本設計規則/可重覆小型副本設計.md', '''# 可重覆小型副本設計（舊路徑相容）

本檔已退役，**不再保存另一套設計規則**。現行可重覆內容設計統一使用 [`可重覆任務設計.md`](可重覆任務設計.md)。

舊檔名只為歷史劇本與外部引用提供可追蹤入口；新增或修訂劇本不得依本檔建立第二套標準。
''')
write('劇本設計規則/可重覆小型副本檢查.md', '''# 可重覆小型副本檢查（舊路徑相容）

本檔已退役，**不再保存另一套檢查清單**。現行可重覆內容驗收統一使用 [`可重覆任務檢查.md`](可重覆任務檢查.md)。
''')


# ---------------------------------------------------------------------------
# AI-GM minimal-load router. It defines load strategy, not new mechanics.
# ---------------------------------------------------------------------------
write('AI_GM讀取路由.md', '''# AI GM 最小讀取路由

本文件只處理**上下文載入策略**，不建立新的遊戲規則。任何機械衝突仍以各權威規則正文為準。

## 原則

- **不要整庫預載。** 先讀模組 README／路由，再只載入當前階段與當前行動需要的正文。
- **流程檔只常駐最小核心。** 已開局時常駐 `GM規則/遊戲流程/基本主持.md`；涉及存檔才加載 `遊戲狀態與存檔.md`，涉及判定、NPC、戰鬥或偏離時再載入對應模組。
- **內容庫按名稱查。** 需要某一內功、門派或高等絕活時，只讀其單一條目／分級檔，不要載入整個 catalogue。
- **世界知識按實際涉事範圍查。** 劇本涉及哪一道、哪個門派、哪個固定人物，才讀對應世界知識條目。
- **相容路由不是權威副本。** 標有「舊路徑相容」的檔案只負責轉向，不可與現行規則並讀後自行合併。

## 階段路由

### 新建角色

先讀 [`GM規則/README.md`](GM規則/README.md) 的建角路由，再按需要載入角色建立、武學與內容庫條目。不要讀遊戲存檔／結算模組。

### 開局環境

只讀 [`GM規則/開局環境.md`](GM規則/開局環境.md) 及宿主提供的 storage target 資料；此階段不預載劇本內主持正文。

### 角色與劇本開局檢查

讀 [`GM規則/開局檢查.md`](GM規則/開局檢查.md)、[`GM規則/角色卡格式.md`](GM規則/角色卡格式.md) 及劇本實際需要的世界／名譽／可重覆規則。只有角色卡需要改動時才加載 `角色卡更新.md`。

### 已開局主持／續跑

先讀 [`GM規則/遊戲流程.md`](GM規則/遊戲流程.md) 路由；正常主持常駐「基本主持」，依當前事件再讀：

- 玩家行動、調查、判定：`GM規則/遊戲流程/判定與調查.md`
- NPC、社交、名譽：`GM規則/遊戲流程/NPC社交與內容庫.md`，必要時再讀 `GM規則/社會互動.md`
- 戰鬥、休息、危機：`GM規則/遊戲流程/戰鬥資源與世界推進.md` + `遊玩規則/遊玩流程/README.md` 指定的當前迴圈
- 偏離、線索完全斷裂、GM 資訊界線：`GM規則/遊戲流程/偏離資訊邊界與即場生成.md`
- 保存／暫停／續跑：`GM規則/遊戲流程/遊戲狀態與存檔.md`

### 結算

讀 [`GM規則/結算.md`](GM規則/結算.md) 路由，並**依順序**完成三個結算模組。結算不再回頭載入整份遊戲流程正文，除非需要核對已凍結來源中的具體主持事實。

## Catalogue 路由

- 十六門派：[`世界知識庫/勢力/門派.md`](世界知識庫/勢力/門派.md) → 單一門派檔。
- 內功：[`內容庫/武學/內功.md`](內容庫/武學/內功.md) → 單一內功檔。
- 高等絕活：[`內容庫/高等絕活.md`](內容庫/高等絕活.md) → 對應等級檔。
- 其他武學、藥物、裝備、敵人：先讀 [`內容庫/README.md`](內容庫/README.md) 再只取需要的條目檔。

## 劇本設計 AI

劇本作者先讀 [`劇本設計規則/設計.md`](劇本設計規則/設計.md) 路由。完整創作時依序讀四個設計模組；只修特定問題時按章節範圍讀單一模組。完成後仍依 `劇本設計規則/README.md` 路由執行全部必要檢查。
''')


# ---------------------------------------------------------------------------
# Update entrypoints, keeping rules in authoritative modules rather than copies.
# ---------------------------------------------------------------------------
p = Path('README.md')
text = p.read_text(encoding='utf-8')
marker = '不同工作應先讀對應模組的 `README.md`，再按需要讀其子文件；不要把 GM 主持規則、劇本設計規則與玩家遊玩機制混成同一套文件。'
if marker in text and 'AI_GM讀取路由.md' not in text:
    text = text.replace(marker, marker + '\n\nAI／代理主持若需要控制上下文量，先讀 [`AI_GM讀取路由.md`](AI_GM讀取路由.md)，再進入各模組 README。', 1)
if '- [`AI GM 最小讀取路由`]' not in text:
    text = text.replace('- [`GM規則入口`](GM規則/README.md)\n', '- [`AI GM 最小讀取路由`](AI_GM讀取路由.md)\n- [`GM規則入口`](GM規則/README.md)\n', 1)
p.write_text(text, encoding='utf-8')

p = Path('GM規則/README.md')
text = p.read_text(encoding='utf-8')
text = text.replace('`遊戲流程.md`：已開局劇本內的主持總循環、存檔、暫停／續跑及終局凍結；具體遊玩機械階段由 `遊玩規則/遊玩流程/README.md` 路由；', '`遊戲流程.md`：已開局劇本的讀取路由；主持、存檔、判定、NPC、戰鬥與偏離已拆成 `GM規則/遊戲流程/` 小模組；具體遊玩機械階段由 `遊玩規則/遊玩流程/README.md` 路由；')
text = text.replace('`結算.md`：結局、參與、得失、歷練、社會名譽、長期特殊傷患、結算憑證、角色卡更新觸發、結算後待處理更新窗口及存檔關閉；', '`結算.md`：結算讀取路由；完整結算依序由 `GM規則/結算/` 三個小模組處理結局／參與／物質、歷練／名譽／履歷、憑證／角色卡更新／關閉；')
if '## AI GM 最小讀取' not in text:
    text = text.replace('## 讀取路由', '## AI GM 最小讀取\n\n若宿主需要限制上下文量，先讀 [`../AI_GM讀取路由.md`](../AI_GM讀取路由.md)。本 README 繼續負責工作階段權威路由。\n\n## 讀取路由', 1)
p.write_text(text, encoding='utf-8')

p = Path('劇本設計規則/README.md')
text = p.read_text(encoding='utf-8')
text = text.replace('完整讀取 `設計.md`', '先讀 `設計.md` 路由，再依路由完整讀取四個設計模組')
text = text.replace('完整讀 `設計.md`', '先讀 `設計.md` 路由，再依路由完整讀四個設計模組')
p.write_text(text, encoding='utf-8')

p = Path('Instruction模版.md')
text = p.read_text(encoding='utf-8')
text = text.replace('先讀取並遵守 Handbook repository 的「GM規則/README.md」', '先讀取 Handbook repository 的「AI_GM讀取路由.md」控制最小載入，再讀取並遵守「GM規則/README.md」')
text = text.replace('創作階段完整讀取「劇本設計規則/設計.md」', '創作階段先讀取「劇本設計規則/設計.md」路由，再依路由依序讀取四個設計模組')
p.write_text(text, encoding='utf-8')


# ---------------------------------------------------------------------------
# Curated audit report with post-refactor metrics.
# ---------------------------------------------------------------------------
md_files = sorted(p for p in ROOT.rglob('*.md') if '.git' not in p.parts)
sizes = sorted(((len(p.read_bytes()), len(p.read_text(encoding='utf-8').splitlines()), p.as_posix()) for p in md_files), reverse=True)
over25 = [x for x in sizes if x[0] >= 25000]
over20 = [x for x in sizes if x[0] >= 20000]

groups = {}
for p in md_files:
    for para in re.split(r'\n\s*\n', p.read_text(encoding='utf-8')):
        norm = re.sub(r'\s+', ' ', para).strip()
        if len(norm) < 120 or norm.startswith('#') or norm.startswith('|'):
            continue
        key = hashlib.sha1(norm.encode('utf-8')).hexdigest()
        groups.setdefault(key, [norm, set()])[1].add(p.as_posix())
dups = sorted(((len(v[0]), sorted(v[1]), v[0]) for v in groups.values() if len(v[1]) > 1), reverse=True)

largest = '\n'.join(f'- `{p}` — {b} bytes / {l} 行' for b, l, p in sizes[:10])
report = f'''# Handbook 完整性與 AI GM 審查

## 結論

**目前 Handbook 已達到「可以不依賴作者口頭補規則而完整開團」的完整可遊玩水平。** 核心判定、建角、戰鬥、探索／整備、傷害與異常、裝備、武學、成長、社會名譽、NPC／敵人、GM 開局／存檔／續跑／結算、安全工具與世界基準都有正式權威文件。

若以一般市售 TRPG 核心規則書的「出版完成度」而非純可玩性衡量，仍有三個主要差距：**新手教學／完整實例偏薄、玩家可直接使用的角色卡／速查成品不足、遭遇難度只有可用的層級與模板指引而沒有更細的隊伍預算表。** 這些不阻止實際遊玩，但會影響第一次接觸本系統的人類 GM／玩家自學速度。

## 完整性矩陣

| 項目 | 判定 | 備註 |
|---|---|---|
| 核心判定、能力、拿手、優劣勢、DC | 通過 | 有玩家規則與 GM 可行性／擲骰鎖定規則 |
| 角色建立、背景、衍生值 | 通過 | 建角流程完整；建角範例仍偏短 |
| 戰鬥、傷害、異常、死亡／恢復 | 通過 | 有獨立戰鬥與共同傷害／狀態子系統 |
| 探索、旅行、追逐、休息、整備 | 通過 | 已統一到主探索／安全空檔路由；舊路徑只保留相容入口 |
| 裝備、金錢、攜帶、製作、材料 | 通過 | 有通用規則與內容庫條目 |
| 武學、內外功、輕功、自創 | 通過 | 系統與內容庫分工清楚 |
| 歷練、升級、重跑、連續性 | 通過 | 本輪已拆成三個按需載入模組 |
| 社交、俠名／惡名／相對名譽 | 通過 | 機械、GM 使用、劇本設計三層均有規則 |
| NPC、敵人、首領／宗師 | 通過 | 有快速 NPC 與敵人模板；遭遇精準預算仍可加強 |
| GM 開局、存檔、續跑、資訊邊界 | 通過 | 對 AI GM 特別完整，本輪已拆分以降低上下文量 |
| 結算、角色卡更新、憑證 | 通過 | 有固定 transaction 與交付驗證；本輪改成三段式 |
| 世界觀、地理、勢力、固定人物 | 通過 | 可支撐現行劇本；門派改為索引 + 單派條目 |
| 安全工具、PvP／自主權 | 通過 | 有桌面共識與遊戲中停止／改寫流程 |
| 新手 quickstart／完整 play example | 部分 | 有建角範例，但缺一份從開局到結算的完整示例 |
| 玩家角色卡／一頁速查成品 | 部分 | 有資料格式，尚缺偏出版品形式的可填寫／速查成品 |
| 遭遇難度精細校準 | 部分 | 有「新手／好手／一流／宗師」與首領模板，缺隊伍規模化預算表 |

## 原結構的主要問題

基準掃描共有 86 份 Markdown；原本最大檔為 `劇本設計規則/設計.md` **60,689 bytes / 1,148 行**，其次 `GM規則/遊戲流程.md` **54,619 bytes / 703 行**、`GM規則/結算.md` **29,920 bytes / 305 行**、`遊玩規則/角色/升級與武學成長.md` **25,533 bytes / 274 行**。這些文件本身內容有用，但對 AI GM 而言會造成「只查一條規則卻必須載入整個工作階段」的上下文浪費。

另有三份退役的「可重覆小型副本」設計／檢查／主持文件仍保存完整舊規則，與現行「可重覆任務」重疊；這是最明顯的**可以用連結取代正文副本**之處。

## 本 branch 的 AI GM 分檔優化

- `劇本設計規則/設計.md` → 路由 + 4 個語義模組。
- `GM規則/遊戲流程.md` → 路由 + 6 個執行模組。
- `GM規則/結算.md` → 路由 + 3 個固定順序模組。
- `遊玩規則/角色/升級與武學成長.md` → 路由 + 3 個成長模組。
- `世界知識庫/勢力/門派.md` → 總索引 + 16 個單門派條目。
- `內容庫/武學/內功.md` → 總索引 + 單一內功條目。
- `內容庫/高等絕活.md` → 總索引 + 分級條目。
- 三份舊「可重覆小型副本」正文 → 縮成相容路由，不再維護第二套規則。
- 新增 `AI_GM讀取路由.md`，明定按階段、按行動、按條目最小載入。

拆檔後 **25 KB 以上 Markdown：{len(over25)} 份；20 KB 以上：{len(over20)} 份**。目前最大的 10 份正文為：

{largest}

## 重覆正文

自動精確段落比對（跨檔、至少 120 字）目前仍有 **{len(dups)} 群**。退役可重覆小型副本的整段規則重覆已移除。若剩餘重覆只是公式在「玩家規則」與「劇本設計」各自保留一段介面摘要，可視為刻意局部重述；其他長段應優先改成單一權威正文 + 路由／連結。

## AI GM 建議載入上限

- **< 15 KB**：適合單一操作／單一 catalogue 條目的常用正文。
- **15–25 KB**：可接受，但應有明確單一責任；若只是 catalogue，優先再拆索引。
- **> 25 KB**：原則上應是人類閱讀總覽、資料型大表或路由，不宜成為 AI GM 每回合必讀正文。
- 流程規則避免在多個檔完整複製；跨工作階段共用規則以權威檔 + 連結處理。

## 尚未在本輪重寫的改善項目

- 補一份從「開局環境 → 開局檢查 → 探索 → 戰鬥／非戰鬥 → 結算 → 更新角色卡」的完整實際遊玩示例。
- 補玩家可直接使用的一頁角色卡／一頁核心速查；目前已有資料格式，但不是出版成品介面。
- 若希望更接近戰術型市售 TRPG，補「隊伍人數 × 角色等級 × 敵人層級／數量」的遭遇預算或壓力級別表；目前規則足以主持，但依賴 GM 對模板的判斷較多。
- 後續可再把 `世界知識庫/勢力/商會鏢局與幫會.md` 這類 15–20 KB catalogue 依組織拆條目；本輪先處理最昂貴且使用頻率最高的門派／內功／高等絕活。
'''
write('審查/Handbook完整性與AI_GM審查.md', report)


# ---------------------------------------------------------------------------
# Validate local Markdown links. Ignore intentional filename templates.
# ---------------------------------------------------------------------------
broken = []
for p in sorted(ROOT.rglob('*.md')):
    text = p.read_text(encoding='utf-8')
    for _, raw in MD_LINK_RE.findall(text):
        raw = raw.strip()
        if not raw or '://' in raw or raw.startswith('#') or 'mailto:' in raw:
            continue
        target = raw.partition('#')[0]
        if not target or '<' in target or '>' in target:
            continue
        dest = (p.parent / target).resolve()
        if not dest.exists():
            broken.append((p.as_posix(), raw))
if broken:
    msg = '\n'.join(f'{src} -> {raw}' for src, raw in broken)
    raise RuntimeError('broken Markdown links after refactor:\n' + msg)

print('Largest markdown after refactor:')
for b, l, p in sizes[:15]:
    print(f'{b:6} {l:4} {p}')
print(f'exact duplicate long paragraph groups: {len(dups)}')
print('Markdown link validation: PASS')
