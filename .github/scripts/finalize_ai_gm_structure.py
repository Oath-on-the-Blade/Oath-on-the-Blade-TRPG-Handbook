from pathlib import Path
import hashlib
import os
import re
import subprocess

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


# Further split the two largest script-design modules. These are design-time,
# but smaller semantic units also improve authoring-agent retrieval.
path = '劇本設計規則/設計/基礎規格與能力.md'
text = read(path)
pos = find(text, '## 3. 角色能力必須能影響劇本')
head = text[:pos].strip()
tail = text[pos:].strip()
# Keep the existing module preface with the first half; give the second half its own preface.
write('劇本設計規則/設計/交付規格與引用.md', head)
write('劇本設計規則/設計/角色能力與開放結構.md', '# 劇本設計：角色能力與開放結構\n\n> 承接原 `設計.md` 第 3–4 節；處理角色能力如何實際影響劇本，以及避免固定流程圖。\n\n' + tail)
Path(path).unlink()

path = '劇本設計規則/設計/場景遭遇與獎勵.md'
text = read(path)
pos = find(text, '## 18. 冒險類型與獎勵設計')
head = text[:pos].strip()
tail = text[pos:].strip()
write('劇本設計規則/設計/場景與挑戰.md', head)
write('劇本設計規則/設計/獎勵危機與偏離.md', '# 劇本設計：獎勵、危機與偏離\n\n> 承接原 `設計.md` 第 18–23 節；處理獎勵、歷練、名譽、危機時間線、動態 NPC 與偏離測試。\n\n' + tail)
Path(path).unlink()

# Split the frequently loaded runtime adjudication module so ordinary action
# adjudication does not also require the investigation chapter every turn.
path = 'GM規則/遊戲流程/判定與調查.md'
text = read(path)
pos = find(text, '## 6. 關鍵線索與調查')
head = text[:pos].strip()
tail = text[pos:].strip()
write('GM規則/遊戲流程/判定與玩家行動.md', head.replace('# GM遊戲流程：判定與調查', '# GM遊戲流程：判定與玩家行動', 1))
write('GM規則/遊戲流程/調查與線索.md', '# GM遊戲流程：調查與線索\n\n> 承接原 `遊戲流程.md` 第 6 節；只在調查、關鍵線索與資訊層級需要時載入。\n\n' + tail)
Path(path).unlink()

# Update stable routers for the finer splits.
p = Path('劇本設計規則/設計.md')
text = p.read_text(encoding='utf-8')
text = '''# 劇本設計規則：設計（讀取路由）

本檔只負責**載入路由與舊章節定位**；具體設計規則已按工作性質拆成六個權威模組。這樣可避免 AI／作者為了查一條規則而一次載入整份六萬字元文件。

| 原章節 | 權威模組 | 主要用途 |
|---|---|---|
| 0–2 | [`設計/交付規格與引用.md`](設計/交付規格與引用.md) | 交付形式、規格頭、NPC／連續性、世界與內容庫引用 |
| 3–4 | [`設計/角色能力與開放結構.md`](設計/角色能力與開放結構.md) | 角色能力影響、行動可行性資料、非固定流程圖 |
| 5–14 | [`設計/因果與調查.md`](設計/因果與調查.md) | 世界真相、人物認知、因果痕跡、線索網、反轉、調查 |
| 15–17 | [`設計/場景與挑戰.md`](設計/場景與挑戰.md) | 場景、戰鬥遭遇、非戰鬥挑戰 |
| 18–23 | [`設計/獎勵危機與偏離.md`](設計/獎勵危機與偏離.md) | 獎勵、歷練、名譽、危機、動態 NPC、偏離 |
| 24–29、核心公式 | [`設計/模板與流程.md`](設計/模板與流程.md) | 正式模板、建議設計流程與公式 |

**完整創作一份新劇本時，六個模組都要讀；查核或修正單一問題時，只讀與該問題相符的模組。** 舊文件若寫「`設計.md` 第 18.8 節」，先讀本路由，再到「獎勵、危機與偏離」模組找同號章節；章節編號沒有因拆檔改變。
'''
p.write_text(text, encoding='utf-8')

p = Path('GM規則/遊戲流程.md')
text = '''# GM規則：遊戲流程（讀取路由）

本檔是已開局／續跑劇本的**AI GM 執行路由**。具體主持規則已拆成小模組；不要在每個回合一次載入全部模組。

| 原章節 | 模組 | 何時讀 |
|---|---|---|
| 1、2（不含 2.1） | [`遊戲流程/基本主持.md`](遊戲流程/基本主持.md) | 進入劇本內循環、一般回合主持 |
| 2.1 | [`遊戲流程/遊戲狀態與存檔.md`](遊戲流程/遊戲狀態與存檔.md) | 開始／續跑、保存、暫停、恢復、存檔衝突 |
| 3–5 | [`遊戲流程/判定與玩家行動.md`](遊戲流程/判定與玩家行動.md) | 玩家行動、可行性、擲骰、重試、資源／角色知識、PvP／裁定異議 |
| 6 | [`遊戲流程/調查與線索.md`](遊戲流程/調查與線索.md) | 關鍵線索、三層資訊、調查與推理 |
| 7–9 | [`遊戲流程/NPC社交與內容庫.md`](遊戲流程/NPC社交與內容庫.md) | NPC、社交、名譽、內容庫引用 |
| 10–13 | [`遊戲流程/戰鬥資源與世界推進.md`](遊戲流程/戰鬥資源與世界推進.md) | 戰鬥主持、資源／休息、失敗向前、時間與危機 |
| 14–16、核心原則 | [`遊戲流程/偏離資訊邊界與即場生成.md`](遊戲流程/偏離資訊邊界與即場生成.md) | 偏離任務、不可回復線索斷裂、GM 資訊邊界、即場 NPC／物件 |

開始或續跑時至少讀「基本主持」及「遊戲狀態與存檔」。之後依當前行動載入對應模組；戰鬥／探索／整備的具體玩家機械仍由 [`../遊玩規則/遊玩流程/README.md`](../遊玩規則/遊玩流程/README.md) 路由。

舊引用如「`GM規則/遊戲流程.md` 第 3.3 節」仍有效：先由本表定位「判定與玩家行動」，再讀同號章節。章節號沒有因拆檔改變。
'''
p.write_text(text, encoding='utf-8')

p = Path('AI_GM讀取路由.md')
text = p.read_text(encoding='utf-8')
text = text.replace('玩家行動、調查、判定：`GM規則/遊戲流程/判定與調查.md`', '玩家行動、判定：`GM規則/遊戲流程/判定與玩家行動.md`\n- 調查、關鍵線索：`GM規則/遊戲流程/調查與線索.md`')
text = text.replace('完整創作時依序讀四個設計模組', '完整創作時依序讀六個設計模組')
p.write_text(text, encoding='utf-8')

p = Path('GM規則/README.md')
text = p.read_text(encoding='utf-8').replace('主持、存檔、判定、NPC、戰鬥與偏離已拆成 `GM規則/遊戲流程/` 小模組', '主持、存檔、判定、調查、NPC、戰鬥與偏離已拆成 `GM規則/遊戲流程/` 小模組')
p.write_text(text, encoding='utf-8')

p = Path('劇本設計規則/README.md')
text = p.read_text(encoding='utf-8').replace('四個設計模組', '六個設計模組').replace('四個設計模組', '六個設計模組')
p.write_text(text, encoding='utf-8')

p = Path('Instruction模版.md')
text = p.read_text(encoding='utf-8').replace('四個設計模組', '六個設計模組')
p.write_text(text, encoding='utf-8')

# Root role index was missing the existing sect-system router.
p = Path('README.md')
text = p.read_text(encoding='utf-8')
old_role = '[`社會名譽與門派`](遊玩規則/角色/社會名譽與門派.md)｜[`升級與武學成長`]'
new_role = '[`社會名譽與門派`](遊玩規則/角色/社會名譽與門派.md)｜[`門派系統`](遊玩規則/角色/門派系統.md)｜[`升級與武學成長`]'
if old_role in text:
    text = text.replace(old_role, new_role, 1)
p.write_text(text, encoding='utf-8')

# Remove stale automated scan before recomputing final metrics.
for doomed in ['審查/AI_GM手冊結構自動掃描.md']:
    q = Path(doomed)
    if q.exists():
        q.unlink()


# Verify all substantive paragraphs from main's original monolith/catalogue files
# still exist somewhere in the new routed structure. Link destinations are ignored
# for this conservation check because relocation intentionally changes them.
def git_show(path: str) -> str:
    return subprocess.check_output(['git', 'show', f'origin/main:{path}']).decode('utf-8')


def norm_paragraph(para: str) -> str:
    # Ignore headings and link destinations; preserve visible wording/code.
    para = re.sub(r'(!?\[[^\]]*\])\([^)]+\)', r'\1', para)
    return re.sub(r'\s+', ' ', para).strip()


def paragraphs(text: str):
    for para in re.split(r'\n\s*\n', text):
        n = norm_paragraph(para)
        if not n or n.startswith('#') or n.startswith('> 承接原') or n.startswith('> 本檔'):
            continue
        yield n

conservation_sets = {
    '劇本設計規則/設計.md': list(Path('劇本設計規則/設計').glob('*.md')),
    'GM規則/遊戲流程.md': list(Path('GM規則/遊戲流程').glob('*.md')),
    'GM規則/結算.md': list(Path('GM規則/結算').glob('*.md')),
    '遊玩規則/角色/升級與武學成長.md': list(Path('遊玩規則/角色/升級與武學成長').glob('*.md')),
    '世界知識庫/勢力/門派.md': [Path('世界知識庫/勢力/門派.md'), *Path('世界知識庫/勢力/門派').glob('*.md')],
    '內容庫/武學/內功.md': [Path('內容庫/武學/內功.md'), *Path('內容庫/武學/內功').glob('*.md')],
    '內容庫/高等絕活.md': [Path('內容庫/高等絕活.md'), *Path('內容庫/高等絕活').glob('*.md')],
}
for original_path, current_paths in conservation_sets.items():
    current_paras = set()
    for cp in current_paths:
        current_paras.update(paragraphs(cp.read_text(encoding='utf-8')))
    missing = [p for p in paragraphs(git_show(original_path)) if p not in current_paras]
    if missing:
        sample = '\n---\n'.join(missing[:5])
        raise RuntimeError(f'content conservation failed for {original_path}: {len(missing)} paragraphs missing\n{sample}')

# Validate every local Markdown link in final docs.
link_re = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
broken = []
for p in sorted(ROOT.rglob('*.md')):
    for _, raw in link_re.findall(p.read_text(encoding='utf-8')):
        raw = raw.strip()
        if not raw or '://' in raw or raw.startswith('#') or raw.startswith('mailto:'):
            continue
        target = raw.partition('#')[0]
        if not target or '<' in target or '>' in target:
            continue
        if not (p.parent / target).resolve().exists():
            broken.append((p.as_posix(), raw))
if broken:
    raise RuntimeError('broken Markdown links:\n' + '\n'.join(f'{a} -> {b}' for a, b in broken))

# Stale paths from the finer split must not survive in docs.
for stale in ['GM規則/遊戲流程/判定與調查.md', '劇本設計規則/設計/基礎規格與能力.md', '劇本設計規則/設計/場景遭遇與獎勵.md']:
    hits = []
    for p in ROOT.rglob('*.md'):
        if stale in p.read_text(encoding='utf-8'):
            hits.append(p.as_posix())
    if hits:
        raise RuntimeError(f'stale routed path {stale}: {hits}')

# Exact duplicate paragraphs >=120 chars across distinct files should be reduced
# to the one deliberate social-reputation interface formula duplication.
md_files = sorted(p for p in ROOT.rglob('*.md'))
groups = {}
for p in md_files:
    for para in re.split(r'\n\s*\n', p.read_text(encoding='utf-8')):
        n = re.sub(r'\s+', ' ', para).strip()
        if len(n) < 120 or n.startswith('#') or n.startswith('|'):
            continue
        key = hashlib.sha1(n.encode('utf-8')).hexdigest()
        groups.setdefault(key, [n, set()])[1].add(p.as_posix())
dups = sorted(((len(v[0]), sorted(v[1]), v[0]) for v in groups.values() if len(v[1]) > 1), reverse=True)
if len(dups) > 1:
    raise RuntimeError(f'unexpected duplicate paragraph groups remain: {len(dups)}')

# Final metrics after removing the stale machine report.
sizes = sorted(((len(p.read_bytes()), len(p.read_text(encoding='utf-8').splitlines()), p.as_posix()) for p in md_files), reverse=True)
over25 = [x for x in sizes if x[0] >= 25000]
over20 = [x for x in sizes if x[0] >= 20000]
if over25:
    raise RuntimeError('Markdown >=25KB remains:\n' + '\n'.join(f'{p}: {b}' for b, _, p in over25))
largest = '\n'.join(f'- `{p}` — {b} bytes / {l} 行' for b, l, p in sizes[:10])

dup_note = '- 無跨檔 120 字以上完全重覆段落。'
if dups:
    _, paths, _ = dups[0]
    dup_note = '- 僅餘 1 群長段完全重覆：' + '、'.join(f'`{p}`' for p in paths) + '；內容是社會名譽倍率公式在玩家規則與劇本設計介面各保留一次。'

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
| 歷練、升級、重跑、連續性 | 通過 | 已拆成按需載入的成長模組 |
| 社交、俠名／惡名／相對名譽 | 通過 | 機械、GM 使用、劇本設計三層均有規則 |
| NPC、敵人、首領／宗師 | 通過 | 有快速 NPC 與敵人模板；遭遇精準預算仍可加強 |
| GM 開局、存檔、續跑、資訊邊界 | 通過 | 對 AI GM 特別完整；主持流程已按行動類型拆分 |
| 結算、角色卡更新、憑證 | 通過 | 有固定 transaction 與交付驗證；結算改成三段式 |
| 世界觀、地理、勢力、固定人物 | 通過 | 可支撐現行劇本；門派為索引 + 單派條目 |
| 安全工具、PvP／自主權 | 通過 | 有桌面共識與遊戲中停止／改寫流程 |
| 新手 quickstart／完整 play example | 部分 | 有建角範例，但缺一份從開局到結算的完整示例 |
| 玩家角色卡／一頁速查成品 | 部分 | 有資料格式，尚缺偏出版品形式的可填寫／速查成品 |
| 遭遇難度精細校準 | 部分 | 有「新手／好手／一流／宗師」與首領模板，缺隊伍規模化預算表 |

## 原結構的主要問題

基準掃描共有 86 份 Markdown；原本最大檔為 `劇本設計規則/設計.md` **60,689 bytes / 1,148 行**，其次 `GM規則/遊戲流程.md` **54,619 bytes / 703 行**、`GM規則/結算.md` **29,920 bytes / 305 行**、`遊玩規則/角色/升級與武學成長.md` **25,533 bytes / 274 行**。這些文件內容本身有用，但對 AI GM／設計代理而言會造成「只查一條規則卻必須載入整個工作階段」的上下文浪費。

另有三份退役的「可重覆小型副本」設計／檢查／主持文件仍保存完整舊規則，與現行「可重覆任務」重疊；這是最明顯的**應使用連結而不應維護正文副本**之處。

## 本 branch 的 AI GM 分檔優化

- `劇本設計規則/設計.md` → 路由 + 6 個語義模組。
- `GM規則/遊戲流程.md` → 路由 + 7 個執行模組；常用「判定」與條件式「調查」再分開。
- `GM規則/結算.md` → 路由 + 3 個固定順序模組。
- `遊玩規則/角色/升級與武學成長.md` → 路由 + 3 個成長模組。
- `世界知識庫/勢力/門派.md` → 保留原標題錨點的索引 + 16 個單門派條目。
- `內容庫/武學/內功.md` → 保留原標題錨點的索引 + 單一內功條目。
- `內容庫/高等絕活.md` → 保留原絕活標題錨點的索引 + 分級條目。
- 三份舊「可重覆小型副本」正文 → 縮成相容路由，不再維護第二套規則。
- 新增 `AI_GM讀取路由.md`，明定按階段、按行動、按條目最小載入。

拆檔及清理後 **25 KB 以上 Markdown：{len(over25)} 份；20 KB 以上：{len(over20)} 份**。目前最大的 10 份正文為：

{largest}

## 重覆正文

{dup_note}

退役可重覆小型副本原本的整段規則重覆已移除。這表示現行主要規則已基本採「單一權威正文 + 路由／連結」而不是多檔複製。

## AI GM 建議載入上限

- **< 15 KB**：適合單一操作／單一 catalogue 條目的常用正文。
- **15–25 KB**：可接受，但應有明確單一責任；若只是 catalogue，優先再拆索引。
- **> 25 KB**：不應成為 AI GM 每回合必讀正文；本 branch 最終已沒有這類 Markdown。
- 流程規則避免在多個檔完整複製；跨工作階段共用規則以權威檔 + 連結處理。

## 驗收

- 最終所有可解析的本地 Markdown 連結均指向實際存在目標。
- 針對原 `設計.md`、`遊戲流程.md`、`結算.md`、`升級與武學成長.md`、門派 catalogue、內功 catalogue、高等絕活 catalogue，逐段比對可見正文；搬檔只改路由／連結位置，沒有遺失原規則段落。
- 舊章節號仍保留在對應子模組，舊文字引用可由路由表定位。

## 尚未在本輪重寫的改善項目

- 補一份從「開局環境 → 開局檢查 → 探索 → 戰鬥／非戰鬥 → 結算 → 更新角色卡」的完整實際遊玩示例。
- 補玩家可直接使用的一頁角色卡／一頁核心速查；目前已有資料格式，但不是出版成品介面。
- 若希望更接近戰術型市售 TRPG，補「隊伍人數 × 角色等級 × 敵人層級／數量」的遭遇預算或壓力級別表；目前規則足以主持，但依賴 GM 對模板的判斷較多。
- 後續可再把 `世界知識庫/勢力/商會鏢局與幫會.md` 這類 15–20 KB catalogue 依組織拆條目；本輪先處理最昂貴且使用頻率最高的門派／內功／高等絕活。
'''
write('審查/Handbook完整性與AI_GM審查.md', report)

# Remove every temporary audit/refactor helper before the final commit.
for doomed in [
    '.github/workflows/audit-ai-gm-structure.yml',
    '.github/workflows/refactor-ai-gm-structure.yml',
    '.github/scripts/refactor_ai_gm_structure.py',
    '.github/scripts/finalize_ai_gm_structure.py',
]:
    q = Path(doomed)
    if q.exists():
        q.unlink()

print('FINAL STRUCTURE VALIDATION PASS')
print(f'Markdown >=25KB: {len(over25)}')
print(f'Markdown >=20KB: {len(over20)}')
print(f'Exact long duplicate groups: {len(dups)}')
for b, l, p in sizes[:12]:
    print(f'{b:6} {l:4} {p}')
