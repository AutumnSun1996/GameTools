# FGO各场景信息提取总结:
助战选择:
- 从者: 全范围搜索, 寻找多个匹配
    - 从者礼装种类: 固定区域内检测模板是否存在
    - 礼装是否满破: 固定区域内检测模板是否存在
    - 从者姓名: 固定区域比较/文字识别(可不检测)
    - 从者等级: 文字识别(可不检测)
    - 技能等级: 文字识别(可不检测)
    - 技能等级: 文字识别(可不检测)

战斗场景-选择技能:
- 战斗轮次信息: 文字识别/战斗历史计算
- 已战斗回合数: 文字识别/战斗历史计算
- 敌人充能情况: 固定区域图片分析
- 是否有危险敌人: 固定区域比较
- 当前轮次剩余敌人数: 文字识别
- 敌人HP: 文字识别
- 己方HP: 文字识别
- 己方NP: 文字识别
- 敌人职阶: 固定区域比较
- 从者职阶: 固定区域比较
- 从者技能是否CD: 固定区域比较
- 御主技能是否CD: 固定区域比较

战斗场景-指令卡选择:
- 指令卡所属从者: 固定区域内搜索最佳匹配的模板
- 指令卡种类: 固定区域内搜索最佳匹配的模板
- 指令卡克制/抵挡关系: 固定区域内检测模板是否存在
- 宝具卡是否可使用: 通过上一场景NP信息获得
- 宝具卡克制/抵挡关系: 固定区域内检测模板是否存在


# 助战选择流程和可配置项
1. 优先职阶
   1. 根据配置好的优先职阶表得到助战选择职阶范围
      如：优先职阶为["Altergo", "Caster"]: 搜索"特殊", "术", "全部"
      只需保存特殊职阶的对应关系
   2. 无优先职阶时依次搜索所有职阶
2. 优先礼装
   1. 对每一个可选职阶, 