# 百妖夜市 · Hundred Spirits Night Market

A Chinese-fantasy property-trading board game featuring a bustling spirit night market, unique merchant roles, magical encounters, and a complete set of printable cards, currency, and maps.

一款以百妖夜市为舞台的原创地产经营桌游，融合商主技能、地产升级与奇遇道具，包含完整的可打印卡牌、灵钱、地图及游戏规则。

![百妖夜市地图预览](assets/preview/board.png)

## 游戏内容

- 2–6人；目标时长90–150分钟，尚待实桌验证。
- 八条街区、32处地产，购买、竞拍、三级建筑和街区技能。
- 24种奇缘签、24种夜巡签、24种百宝令，以及六位商主。
- 140张实体卡牌；七种面额灵钱，建议印134张。
- 48格地图，成品420×420毫米；原生拼图5016×5016像素，另提供12000×12000像素放大稿。
- 固定轮数按总资产结算，不设抵押与淘汰。

所有卡片与灵钱均整面生成，名称、规则、数字、图案和边框属于同一原图；没有后期覆盖卡面文字。地图由16块带格名与编号的完整生成分区拼接。PDF只将整张原图排到印制纸张上。

## 下载与打印

前往 [v1.0.0-playtest 下载页](https://github.com/penglory/hundred-spirits-night-market/releases/tag/v1.0.0-playtest)。

|下载项|用途|
|---|---|
|`hundred-spirits-night-market-print-kit.zip`|全部成对PNG、两种分辨率地图、七份分项PDF、本地图鉴和规则。解压后打开“成品图鉴.html”可翻面查看。|
|`hundred-spirits-night-market-a4-complete.pdf`|164页A4印制合集，集合规则、图鉴、卡牌、灵钱、地图拼接和辅助组件。|
|`SHA256SUMS.txt`|下载文件的SHA-256校验值。|

印制包与A4合集分别下载，避免单个附件超过GitHub大小限制；合集内容与分项PDF重合，无须重复打印。

卡牌63×88毫米，灵钱140×70毫米。合集选择**实际大小100%、长边双面**，地图与辅助组件已插入空白背页。先试印卡牌正反面确认对位。另备三枚六面骰、裁切工具与粘贴材料。

## 规则与说明

- [规则手册](docs/规则手册.md)
- [地产与卡牌完整图鉴](docs/地产卡牌图鉴.md)
- [印制尺寸、印数与背面复用](docs/印制与复用说明.md)
- [A4合集页码](docs/合集页码.md)
- [交付检查范围](docs/交付验收.md)
- [实桌试玩记录与验收](docs/试玩验收.md)

## 仓库结构

|目录／文件|内容|
|---|---|
|`assets/final/`|154张独立生成成品原图，包含全部正反面和地图分区。复用背面只存一份。|
|`assets/preview/`|地图预览。|
|`data/game.json`|规则、地产、卡牌、商主与货币数据。|
|`data/image-jobs.json`|每张原图的生成提示词、背面关联和印数。|
|`data/asset-manifest.json`|252个成对图片／地图分区导出项的规格与哈希。|
|`data/final-check.json`、`data/visual-review.json`|文件检查与视觉校对范围。|
|`docs/`|规则、图鉴、印制与试玩文档。|
|`scripts/`|内容生成、原图整理、地图组装、PDF印制和验收脚本。|
|`index.html`|仓库版图鉴，克隆或下载源码后可在本地打开，直接读取原图。|

`output/`、临时检查图、未采用生成图和大型压缩包不进入Git历史，完整成品在Releases提供。生成原图本身已经包含在仓库，无须重新调用图像模型即可组装印制文件。

## 本地组装

当前PDF脚本使用Windows自带微软雅黑字体。需要Node.js与Python，Python依赖见`requirements.txt`。在项目根目录运行：

```powershell
python -m pip install -r requirements.txt
node scripts/validate.mjs
node scripts/package.mjs
python scripts/assemble-map.py
python scripts/print.py all
python scripts/finish.py merge
python scripts/check-combined.py
python scripts/finish.py check
```

以上命令生成`output/`及可翻面的`成品图鉴.html`。`assemble-map.py`只拼接完整地图分区、缩放整图，不修改格名或覆盖文字。

若修改内容，按`build-content.mjs`、`build-jobs.mjs`、`map-jobs.mjs`、`reference-jobs.mjs`的顺序更新数据与提示词；然后需要重新生成受影响的完整卡面，旧图不会随JSON自动改字。普通印制无需执行这组内容重建命令。

## 版本状态

当前为原创可打印试玩版。已完成内容结构检查、原图视觉核对和PDF印制布局检查；尚未进行实体打印对位及实桌经济平衡测试。12000像素地图为放大输出，不代表新增原生细节。
