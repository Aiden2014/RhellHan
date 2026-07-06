# RhellHan

> [English Documentation](README.md)

游戏《Rhell》的完整中文本地化模组，通过运行时 TextMeshPro 拦截、回退字体注入以及逐帧字形渲染修复，解决了游戏原生不支持 CJK 字符的问题。

## 项目概述

RhellHan 为游戏《Rhell》提供完整的简体中文本地化支持。游戏使用 Unity 的 TextMeshPro 渲染所有游戏内文本，但并未内置 CJK 字符覆盖。为了在不修改原始游戏资源的情况下添加中文支持，本模组在每个加载的 TMP 字体上注入中文字体作为回退（fallback），并通过 Harmony 运行时补丁覆盖所有主要的文本显示系统。

核心组件：

1. **运行时翻译** — 基于 BepInEx + Harmony 的插件，拦截对话、UI 文本、物品栏、地图提示、剧情点、对话选项、作弊菜单、挑战菜单、世界/区域名称和技能选择，然后用 CSV 字典中的中文翻译替换英文字符串。
2. **回退字体注入** — 钩取 `TMP_FontAsset.ReadFontAssetDefinition`，在游戏加载的每个 TMP 字体上注册中文字体作为回退。
3. **UI 字体替换** — 对于旧版的 `UnityEngine.UI.Text` 组件，从同一个 AssetBundle 中加载中文字体变体进行整体替换。
4. **字形厚度修复器** — 翻译后挂载到对话框上的 `MonoBehaviour`，每帧调整 `TMP_SubMeshUI` 材质的 `FaceDilate` 属性，修复动态生成回退字形的渲染伪影。
5. **TextMeshPro 文本翻译** — 补丁 `TextMeshPro.Awake` 和 `UIBehaviour.Start`，在启动时翻译 TextMeshPro UGUI 文本。
6. **作弊菜单翻译** — 翻译 `CheatRuneBook.SetupCheatMenu` 中的作弊符文标题和描述。
7. **挑战菜单翻译** — 翻译 `ChallengeMenu.SetupValues` 中的挑战名称。
8. **技能选择翻译** — 翻译 `UISelectableSpell.GetTitle` 中的技能名称和描述。
9. **世界/区域名称翻译** — 补丁 `MainMenuUi.Start` 和 `MapHandle.SelectLocation` 以替换世界区域名称。
10. **排序文本本地化** — 将 `UiItemsHandle` 中的排序标签替换为中文。

## 技术亮点

- **回退字体策略**：不修改游戏原有的 TMP 字体，而是通过钩取 `TMP_FontAsset.ReadFontAssetDefinition`，将预构建的中文 SDF 字体作为回退追加。TextMeshPro 会自动对主字体中缺失的字符使用回退字体——无需逐字体资产修改。
- **TMP SubMesh 字形修复**：当 TextMeshPro 渲染回退字形时，会创建 `TMP_SubMeshUI` 对象，其材质中的 `FaceDilate` 值可能不正确，导致显示伪影。`FallbackFontThicknessFixer` 每帧运行，调整对话框中所有子网格上的该 shader 属性。
- **使用 `|||` 进行 CSV 键批处理**：多段文本（对话、总结、对话选项）使用 `|||` 作为分隔符拼接成复合查找键，在翻译过程中保留段落结构。
- **对话选项宽度自适应**：翻译对话选项后，插件使用 `TMP_Text.GetPreferredValues()` 测量每个选项的宽度，并动态调整选项按钮大小，CJK 文本使用更宽的上限（550px vs 英文 485px）。

## 涉及技术与库

- **[BepInEx 5.x](https://github.com/BepInEx/BepInEx)** — Unity 游戏模组框架，提供插件加载和日志系统。
- **[HarmonyLib 2.x](https://github.com/pardeike/Harmony)** — 运行时方法补丁库，实现无侵入式代码注入。
- **[Unity Editor 2020.3.49f1c1](https://unity.com/)** — 通过 TextMeshPro 的 Font Asset Creator，从 `KNMaiyuan-Regular` 生成中文 `TMP_FontAsset`，并将字体打包为 AssetBundle。
- **[UABEANext](https://github.com/nesrak1/UABEANext)** — Unity Asset Bundle Extractor，用于从游戏的资产包中提取 MonoBehaviour 文本数据，为构建翻译源 CSV 文件提供原始字符串。
- **[DnSpy-MCPserver-Extension](https://github.com/AgentSmithers/DnSpy-MCPserver-Extension)** — dnSpyEx 的 MCP 服务器扩展，支持程序化 IL 检查和补丁。开发过程中用于探索游戏程序集方法、识别注入点并验证 Harmony 补丁目标。
- **[ParaTranz](https://paratranz.cn/)** — 协作翻译管理平台，用于众包本地化。

## 自定义字体工作流

由于《Rhell》仅提供拉丁字符的 TMP 字体，我们需要生成中文回退字体：

1. **提取所需字符** — 运行 `scripts/extract_unique_non_ascii_chars.py`，从已翻译的 CSV 文件中收集所有唯一的非 ASCII 字符。默认输出为 `resources/unique_non_ascii_chars.txt`。
2. **创建 TMP 字体资产** — 在 Unity Editor 2020.3.49f1c1 中导入 `KNMaiyuan-Regular` 字体和生成的 `unique_non_ascii_chars.txt`，然后打开 TextMeshPro 的 Font Asset Creator。
3. **使用字体生成配置** — Source Font File 选择 `KNMaiyuan-Regular`，Sampling Point Size 设为 `Auto Sizing`，Padding 设为 `5`，Packing Method 设为 `Fast`，Atlas Resolution 设为 `2048 x 2048`，Character Set 设为 `Characters from File`，Character File 选择 `unique_non_ascii_chars`，Render Mode 设为 `SDFAA`，并勾选 `Get Kerning Pairs`。生成并保存 TMP 字体资产为 `KNMaiyuan-Regular SDF`。
4. **打包为 AssetBundle** — 使用 Unity 的 AssetBundle 工具，将 TMP 字体资产和 `KNMaiyuan-Regular` 字体一起打包为 `chinese_font.bundle`。
5. **安装 bundle** — 将 `chinese_font.bundle` 放入 `Rhell\BepInEx\plugins\resources`（或你实际安装目录下的 `BepInEx/plugins/resources/`）。插件会通过 `AssetBundle.LoadFromFile()` 加载。

## 项目结构

```text
RhellHan/
├── resources/                           # 翻译数据和字体 bundle
│   ├── challenge_menu.csv               # 挑战菜单翻译
│   ├── cheat_description.csv            # 作弊符文描述翻译
│   ├── cheat_title.csv                  # 作弊符文标题翻译
│   ├── dialogue.csv                     # 原始对话提取（未过滤）
│   ├── dialogue_filtered.csv            # 对话翻译（使用 ||| 批量键）
│   ├── dialogue_option.csv              # 对话选项翻译
│   ├── endpoint.csv                     # 终点文本翻译
│   ├── hint.csv                         # 暂停菜单提示翻译
│   ├── item_description.csv             # 物品描述翻译
│   ├── item_name.csv                    # 物品名称翻译
│   ├── item_tab_description.csv         # 物品栏标签描述翻译
│   ├── json_diff.txt                    # JSON 对比输出，用于翻译 QA
│   ├── map_location_hightlight.csv      # 地图位置高亮翻译
│   ├── room_hint.csv                    # 房间提示翻译
│   ├── rune_description.csv             # 符文描述翻译
│   ├── rune_name.csv                    # 符文名称翻译
│   ├── selectable_spell_description.csv # 技能描述翻译
│   ├── selectable_spell_name.csv        # 技能名称翻译
│   ├── storypoint.csv                   # 剧情点文本翻译
│   ├── storypoint_mapping.csv           # 剧情点 ID 到文本的映射
│   ├── storypoint_missing.csv           # 缺失/未翻译的剧情点
│   ├── summary.csv                      # 局末总结翻译
│   ├── summarypoint.csv                 # 总结点文本翻译
│   ├── text.csv                         # 旧版 UI 文本翻译
│   ├── text_mesh_pro.csv                # TextMeshPro 文本翻译
│   ├── text_mesh_pro_ugui.csv           # TextMeshPro UGUI 文本翻译
│   ├── world_name.csv                   # 世界/区域名称翻译
│   └── unique_non_ascii_chars.txt       # 用于字体生成的字符列表
├── scripts/                             # Python 自动化工具
│   ├── compare_hints_arrays.py          # 跨版本对比提示数组
│   ├── compare_json_files.py            # 对比 JSON 导出用于翻译 QA
│   ├── extract_and_merge_texts_v2.py    # 提取并合并文本资源
│   ├── extract_challenge_menu_to_csv.py # 提取挑战菜单文本
│   ├── extract_cheat_to_csv.py          # 提取作弊菜单标题和描述
│   ├── extract_dialogues_from_monobehaviour.py
│   ├── extract_dialogues_options_from_monobehaviour.py
│   ├── extract_endpoint_summarypoint.py # 提取终点和总结点文本
│   ├── extract_hints_from_monobehaviour.py
│   ├── extract_inventory_to_csv.py      # 提取符文/物品名称和描述
│   ├── extract_map_location_highlights.py
│   ├── extract_room_hints.py
│   ├── extract_storypoints_from_monobehaviour.py
│   ├── extract_summaries_from_monobehaviour.py
│   ├── extract_text_mesh_pro.py         # 从资源中提取 TextMeshPro 文本
│   ├── extract_text_mesh_pro_ugui.py    # 提取 TextMeshPro UGUI 文本
│   ├── extract_texts_from_monobehaviour.py
│   ├── extract_ui_item_tab_descriptions.py
│   ├── extract_ui_selectable_spell_level3_to_csv.py
│   ├── extract_unique_non_ascii_chars.py # 收集非 ASCII 字符用于字体生成
│   ├── extract_world_names.py
│   └── filter_and_deduplicate_dialogues.py
├── FontManager.cs                       # TMP_FontAsset 加载时的回退字体注册
├── Plugin.cs                            # BepInEx 入口点及所有 Harmony 补丁
├── ResourceLoader.cs                    # AssetBundle 加载和 CSV 解析
├── TranslationManager.cs                # CSV 字典初始化和查询
├── RhellHan.csproj                      # .NET Standard 2.1 构建配置
└── RhellHan.sln                         # 解决方案文件
```

## 开源协议

### 本项目代码

采用 **[GNU LGPL v2.1](LICENSE)** 协议发布。

### 第三方组件

- **BepInEx**: [LGPL-2.1](https://github.com/BepInEx/BepInEx/blob/master/LICENSE)
- **HarmonyLib**: [MIT](https://github.com/pardeike/Harmony/blob/master/LICENSE)

### 翻译内容

翻译内容来自 [ParaTranz 平台](https://paratranz.cn/projects/18570)，采用 **CC BY-NC 4.0** 协议。

---

**注意**：本项目仅供学习交流使用。请支持正版游戏。
