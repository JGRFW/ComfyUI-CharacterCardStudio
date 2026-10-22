# ComfyUI Character Card Studio

![version](https://img.shields.io/badge/version-1.2.0-blue)

> 面向 **Qwen-Image 2.1** 的 ComfyUI 角色卡与场景多视图自动生成插件。
> 一张角色图或任意场景图 → 自动补全多视图 / 表情 / 环境细节 → 按卡版精确切片与排版。

![one-click](docs/oneclick_preview.png)

## 它解决什么问题

手工做一张角色设定卡，要分别生成正面、侧面、背面、头像、动作、六宫格表情、九宫格细节，再手动把每张贴进对应格子、对齐、防止裁头裁脚。本插件把这条流水线收进 ComfyUI：

```text
一张角色参考图  或  一段人物提示词
            ↓
   Qwen-Image 2.1 自动生成多视图 / 表情 / 细节
            ↓
   按选定卡版自动切片（每格统一 768×768）
            ↓
   按 panel_order 重排、全身完整不裁切，输出最终角色卡
```

## 核心特性

- **两种入口**：上传一张参考图做身份锚点，或纯提示词文生角色。
- **一键节点**：卡版、排序、全身显示、输出尺寸全部集中在一个节点，切片节点免配置。
- **自动切片重排**：`panel_order` 支持 `1,3,2,4,5-9` 这类写法；`fit_mode` 默认"完整显示"保证全身从头顶到鞋底不裁切。
- **8 套角色卡版 + 1 套通用场景卡版**：从 4 格到 14 格覆盖偏立、双帧、三视图、主视觉、表情谱、设定集和全图鉴；场景卡可用任意一张场景图作为锚点补出左向、右向、反向、俯视和环境细节；编辑器、引导图和拼图共用同一份布局数据。
- **右侧面自动镜像**：拼图时右侧面格自动水平翻转，保证左右侧面一左一右，不依赖模型方向指令。
- **分项生成 + 专业排版**：可分别产出正面/侧面/背面全身、头像、动作 A/B、表情组、细节组，再按卡版自动归位。
- **排版一致性**：一次整卡生成仍会受模型随机性影响；需要逐格位置和数量稳定时，优先使用“3 角色/场景逐格生成与排版 · 一键完成”。
- **零额外依赖**：只用 ComfyUI 自带的 Pillow / NumPy / torch / aiohttp。
- **可视化工作台**：`web/` 前端提供卡片状态编辑（HTTP 路由 `/aicg3d/character-card/templates`）。

## 节点一览

| 节点 ID | 显示名 | 作用 |
|---|---|---|
| `AICG3D_CharacterCardOneClick` | 一键角色/场景卡提示词 · Qwen Image 2.1 | 选卡版、填人物设定，编译提示词+负面词+空白版式引导图+卡版 JSON |
| `AICG3D_CharacterSheetSplitter` | 角色/场景卡自动切片 · 无需设置 | 读首节点配置，自动切片、全身完整显示、重排 |
| `AICG3D_CharacterCardStudio` | 角色/场景卡工作台 · Qwen Image 2.1 | 手动逐格替换素材、微调裁切的高级模式 |
| `AICG3D_CharacterCardAssetPrompt` | 角色卡分项提示词 | 分别输出全身/头像/动作/表情/细节资产提示词 |
| `AICG3D_CharacterCardAssetComposer` | 角色卡专业排版 | 把独立资产按卡版组合成最终角色卡 |
| `AICG3D_CardSettingsFive` | 1 角色/场景卡型设置 · 9种卡版 | 单线流程第一步（节点 ID 为兼容旧工作流保留） |
| `AICG3D_Qwen21ModelLoader` | 2 千问 Image 2.1 模型选择 | 选 UNET / CLIP / VAE，输出 MODEL/CLIP/VAE |
| `AICG3D_CharacterCardGeneratorSingle` | 3 角色/场景逐格生成与排版 · 一键完成 | 每个启用画格独立生成并按模板坐标精确拼回 |

## 内置卡版

| ID | 名称 | 格数 |
|---|---|---|
| `bighead_body3` | 四格·偏立 | 4 |
| `dualfour_ref` | 四格·双帧 | 4 |
| `fiveref` | 五格·正反 | 5 |
| `head_body_6` | 六格·三视图 | 6 |
| `sixtilt_ref` | 六格·主视觉 | 6 |
| `expr_body_8` | 八格·表情谱 | 8 |
| `school_ref` | 十格·设定集 | 10 |
| `xianxia_ref` | 十四格·全图鉴 | 14 |
| `scene_six_view` | 场景·六面图 | 6 |

## 快速开始

标准方案：打开 `workflows/角色卡_五种卡版_单线工作流.json`。

- **图生卡**：打开 `workflows/一键角色卡_QwenImage21.json`，在 `LoadImage` 上传参考图，在"一键角色卡提示词"里选卡版、补充人物描述，队列执行。
- **文生卡**：打开 `workflows/一键角色卡_提示词版_QwenImage21.json`，在 `character_prompt` 填人物设定即可。
- **纯提示词单线**：`workflows/角色卡_五种卡版_文生图单线工作流.json`。
- **场景补面**：在卡型中选择 `scene_six_view`，把任意场景照片接到 `reference_image`；第一格保留正面原图，其余五格自动生成左向、右向、反向、俯视和环境细节。

## 安装

把整个文件夹放到：

```text
ComfyUI/custom_nodes/ComfyUI-CharacterCardStudio
```

重启 ComfyUI。

## 推荐模型文件

工作流默认选择（本机文件名不同就在加载器里重选）：

- UNET：`qwen_image_2.1_bf16.safetensors`（显存紧张用 `qwen_image_2.1_int8_convrot.safetensors`）
- CLIP：`qwen3vl_8b_int8_convrot.safetensors`，类型 `qwen_image`
- VAE：`qwen_image_2.1_vae_bf16.safetensors`
- 编码器：`TextEncodeQwenImage21`

## 验证

```powershell
python -m py_compile __init__.py nodes.py templates.py renderer.py splitter.py
node --check web\character_card_studio.js
python tests\layout_contract.py
python tests\smoke_renderer.py
python tests\workflow_smoke.py
```

已校验：9 套卡版坐标无重叠、逐格提示词数量一致、节点下拉返回 9 个卡型，工作流加载无缺失节点。

## License

MIT
