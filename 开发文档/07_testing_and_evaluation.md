# 07 测试与评估文档

## 1. 为什么需要测试

AIGC 项目不只是“能生成就行”。本项目尤其需要测试以下问题：

- 剧情是否连贯？
- 人物是否一致？
- 世界状态是否正确更新？
- 场景是否可视化？
- Prompt 是否适合图像生成？
- 输出 JSON 是否稳定？

---

## 2. 测试分类

建议分成四类：

```text
结构测试
一致性测试
剧情质量测试
场景可视化测试
```

---

## 3. 结构测试

### 3.1 JSON 合法性测试

每个模块输出都应能被 `json.loads()` 解析。

测试点：

- 是否缺少大括号。
- 是否多了 Markdown 代码块。
- 是否有中文引号。
- 是否有尾逗号。
- 字段是否缺失。

### 3.2 字段完整性测试

例如 `EventCard` 必须包含：

```text
event_id
step
summary
stage
cause
effect
involved_characters
location
tension_change
new_clues
new_conflicts
state_changes
```

---

## 4. 一致性测试

### 4.1 人物一致性

检查：

- 人物姓名是否突然改变。
- 人物身份是否突然改变。
- 人物视觉特征是否突然改变。
- 人物目标变化是否有原因。

错误示例：

```text
前文主角叫林夏，后文突然叫苏晴。
```

### 4.2 地点一致性

检查：

- 地点变化是否有事件解释。
- 当前地点是否存在于可用地点中。
- 场景卡地点是否与事件地点一致。

错误示例：

```text
当前地点是宿舍，但场景卡突然变成废弃工厂，没有任何过渡。
```

### 4.3 事实一致性

检查：

- 已发生事件是否被推翻。
- 已知事实是否被无原因删除。
- 世界规则是否被破坏。

---

## 5. 剧情质量测试

### 5.1 因果性

每个事件应该有原因和结果。

评分：

| 分数 | 标准 |
|---|---|
| 1 | 事件随机出现，无因果 |
| 2 | 有弱因果，但不明显 |
| 3 | 因果关系清楚 |
| 4 | 因果自然，推动主线 |
| 5 | 因果强，且制造悬念 |

### 5.2 张力变化

剧情应该逐步升级，而不是一直平淡。

检查：

- 是否出现新线索？
- 是否出现新问题？
- 主角压力是否增加？
- 冲突是否逐步逼近核心？

---

## 6. 场景可视化测试

### 6.1 场景是否能被画出来

检查场景卡是否包含：

- 地点
- 时间
- 人物
- 动作
- 关键物体
- 光照
- 镜头
- 氛围

不可视化示例：

```text
林夏意识到命运的残酷。
```

可视化示例：

```text
林夏坐在昏暗宿舍的书桌前，电脑屏幕上的倒计时映在她苍白的脸上。
```

### 6.2 图像 Prompt 是否具体

好的 Prompt 应包含：

- 风格：pixel art RPG game CG
- 画幅：16:9
- 地点：college dormitory
- 时间：midnight
- 人物：young Chinese female computer science student
- 动作：sitting at desk, staring at laptop screen
- 光照：cold blue laptop glow
- 氛围：tense, eerie

---

## 7. 自动测试建议

### 字段检查函数

```python
def check_required_fields(data: dict, required_fields: list[str]) -> list[str]:
    missing = []
    for field in required_fields:
        if field not in data:
            missing.append(field)
    return missing
```

### 角色姓名一致性检查

```python
def check_character_name_consistency(world_states: list[dict]) -> bool:
    first_names = set(world_states[0]["characters"].keys())
    for state in world_states[1:]:
        current_names = set(state["characters"].keys())
        if not first_names.issubset(current_names):
            return False
    return True
```

### 地点检查

```python
def check_location_valid(world_state: dict) -> bool:
    return world_state["current_location"] in world_state["available_locations"]
```

---

## 8. 人工评估表

| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| 连贯性 | 前后矛盾明显 | 基本连贯 | 非常自然 |
| 人物一致性 | 人物设定混乱 | 基本一致 | 设定稳定 |
| 因果性 | 事件随机 | 有基本因果 | 因果很强 |
| 悬念感 | 无吸引力 | 有一定悬念 | 很想继续看 |
| 可视化程度 | 难以画出 | 可以画 | 画面感强 |
| Prompt 质量 | 泛泛而谈 | 基本可用 | 很适合出图 |

---

## 9. Debug 记录模板

```markdown
# Debug 记录

## 时间

2026-xx-xx

## 输入

xxx

## 问题现象

例如：第三个事件中主角名字改变。

## 可能原因

例如：Prompt 没有强调人物姓名必须保持一致。

## 修改方案

在 generate_event Prompt 中加入：
“不得改变已有角色姓名和身份。”

## 修改后效果

xxx
```
