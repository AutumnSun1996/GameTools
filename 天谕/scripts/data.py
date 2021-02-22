recipe_data = """
# 消耗 获得
# 采集.钓鱼
10活力=3沙丁鱼肉
10活力=3鲈鱼肉
# 采集
3活力=1星茸花+0.0099百花露
3活力=1迷梦木+0.0126古木髓
4活力=1椰木+0.0163古木髓
5活力=1桦木+0.0179古木髓
3活力=1铁矿石+0.0126玄晶石
4活力=1铜矿石+0.0163玄晶石
5活力=1银矿石+0.0179玄晶石
# 制造
3活力+1迷梦木+1铁矿石=1新手制药台
3活力+1迷梦木+1铁矿石=1新手烹饪台
3活力+1迷梦木+1铁矿石=1新手工艺台
4活力+1椰木+1铜矿石+0.05学徒工艺台=1学徒制药台
4活力+1椰木+1铜矿石+0.05学徒工艺台=1学徒烹饪台
4活力+1椰木+1铜矿石=1学徒工艺台
6活力+2椰木+2铜矿石+0.05学徒工艺台=1.0345娃娃
6活力+2迷梦木+2铁矿石+1精炼矿石=1.0347玩偶
10活力+6迷梦木+6铁矿石+2精炼矿石+0.05学徒工艺台=1铁钥匙
10活力+8椰木+8铜矿石+2精炼矿石+0.05学徒工艺台=1铜钥匙
7活力+2迷梦木+2铁矿石+2精炼矿石+0.05学徒工艺台=1伪装器-袁嵩
10活力+4椰木+4铜矿石+3精炼矿石+0.05学徒工艺台=1伪装器-司空望月
20活力+3古木髓+3玄晶石+0.05学徒工艺台=1.0069鎏金宝匣
100活力+4古木髓+4玄晶石+60迷梦木+0.05学徒工艺台=圣音钢琴
100活力+4古木髓+4玄晶石+60迷梦木+0.05学徒工艺台=1天丝舞鞋
100活力+4古木髓+4玄晶石+60迷梦木+0.05学徒工艺台=1盘龙竿
100活力+4古木髓+4玄晶石+60迷梦木+0.05学徒工艺台=1永灵勺
100活力+4古木髓+4玄晶石+60铁矿石+0.05学徒工艺台=1劈天斧
# 制造.炼药
3活力+2星茸花+1朱砂=2.7435青络饮+0.2565青络饮·珍
3活力+2星茸花+1朱砂=2.7435玉露丹+0.2565玉露丹·珍
10活力+2百花露+12星茸花=1.0303下品致命药剂
10活力+2百花露+12星茸花=1.0303下品致命抵抗药剂
10活力+2百花露+12星茸花=1.0303下品命中药剂
10活力+2百花露+12星茸花=1.0303下品闪避药剂
10活力+2百花露+12星茸花=1.0303下品穿透药剂
10活力+2百花露+12星茸花=1.0303下品格挡药剂
# 商会购买
3000云币=1精炼矿石
500云币=1朱砂
80000云券=1白雾石
80000云券=1青金石
16000云券=1灵犀角·小


# 妙手
30活力+80妙手价值=1灵犀角·小
30活力+80妙手价值=20000云券
30活力+100妙手价值=40000云券
30活力+100妙手价值=10回蓝食物·70级
30活力+100妙手价值=10回血食物·70级
30活力+140妙手价值=1铜宝箱
30活力=4沙丁鱼肉

# 交换
1黑暗料理=1.75水晶鱼羹+1.75苏澜炒饭
5帝社积分=1炼器骰·紫
10帝社积分=1炼器骰·金
10帝社积分=1灵犀角·小
60帝社积分=1玉龙角·碎片
750帝社积分=1玉龙角
600帝社积分=1轮回之章
500帝社积分=1魄之晶·精华
40帝社积分=1白雾石
50帝社积分=1青金石
215帝社积分=1御灵石·精宝箱
# 合成
10玉龙角·碎片=1玉龙角
"""

trade_data = """
# 物品 价格
玉露丹=725
青络饮=725
玉露丹·珍=11250
青络饮·珍=8625

玉龙角=3867312

忘川石·紫=3000
忘川石·金=96000

新手制药台=7150
学徒制药台=10800
新手烹饪台=7150
学徒烹饪台=12150
新手工艺台=7800
学徒工艺台=10800

蒙面小精怪·召唤器=120000
沙丁鱼肉=1620
鲈鱼肉=2268

水晶鱼羹=2640
苏澜炒饭=2530
黑暗料理=5600

星茸花=1296
百花露=48000
迷梦木=1728
椰木=3024
古木髓=48000
铁矿石=1404
铜矿石=4320
玄晶石=48000

铁钥匙=30000
铜钥匙=60000
伪装器-司空望月=60000
普通染料=49000
油彩=58000
玩偶=12800
娃娃=20000

下品致命药剂=124000
下品致命抵抗药剂=144000
下品命中药剂=144000
下品闪避药剂=144000
下品穿透药剂=144000
下品格挡药剂=140000

天丝舞鞋=720000
盘龙竿=720000
永灵勺=720000
劈天斧=720000
圣音钢琴=720000
# 鎏金宝匣=240000
"""
