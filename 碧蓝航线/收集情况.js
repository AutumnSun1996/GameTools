var buildNotOpen = `
绫波(柚) 莫里 威奇塔 莱比锡 多塞特郡 明石(茗)
`.replace(/[\s（）()]+/g, " ").trim().split(" ")

var shipOwnInfo = `
- 驱逐:
  - 常见:
    - [x]卡辛, [x]唐斯, [x]克雷文, [x]麦考尔, [x]奥利克, [x]富特, [x]斯彭斯, [x]小猎兔犬, [x]大斗犬, [x]彗星, [x]新月, [x]小天鹅, [x]狐提, [x]不知火(蒲), [x]Z20, [ ]Z21, [x]睦月(松), [ ]如月(樟), [x]卯月(楙), [ ]水无月(杌), [ ]三日月(檧)
  - 稀有:
    - [x]格里德利, [x]弗莱彻, [x]撒切尔, [ ]本森, [x]西姆斯, [x]哈曼, [x]女将, [ ]阿卡司塔, [ ]热心, [x]命运女神, [x]天后, [ ]晓(枫), [x]雷(梓), [ ]电(柏), [x]白露(梿), [x]阳炎(萩), [ ]初春(梅), [ ]若叶(楉), [ ]初霜(檨), [ ]有明(榎), [ ]夕暮(棭), [ ]黑潮(蓉), [ ]亲潮(藮), [ ]贝利, [ ]神风(榊), [x]松风(棡), [ ]文月(橗), [ ]拉德福特, [ ]杰金斯, [ ]丘比特, [ ]泽西, [ ]浦风(槆), [ ]矶风(柉), [ ]滨风(樇), [x]谷风(栭), [ ]朝潮(棹), [ ]大潮(荙), [ ]满潮(樠), [x]Z18, [x]Z19, [x]福尔班, [x]勒马尔
  - 精锐:
    - [x]泛用型布里, [ ]莫里, [x]查尔斯·奥斯本, [x]拉菲, [x]萤火虫, [x]标枪, [x]吸血鬼, [ ]吹雪(桐), [ ]绫波(柚), [x]时雨(栴), [ ]野分(苓), [x]Z1, [x]Z23, [x]Z25, [ ]鞍山, [ ]抚顺, [ ]长春, [ ]太原, [ ]新月JP(枥), [ ]春月(桸), [ ]宵月(楛), [ ]尼古拉斯, [ ]无敌, [ ]火枪手, [x]Z35, [ ]布兰, [ ]22, [ ]33
  - 超稀有:
    - [x]试作型布里MKII, [ ]埃尔德里奇, [ ]夕立(椿), [ ]雪风(莲), [x]Z46, [ ]江风(茳), [x]凯旋, [ ]群白之心
- 轻巡:
  - 常见:
    - [x]奥马哈, [x]罗利, [x]利安得, [x]长良(貊), [ ]阿武隈(貃), [x]柯尼斯堡, [x]卡尔斯鲁厄, [x]科隆, [ ]里士满
  - 稀有:
    - [x]布鲁克林, [x]菲尼克斯, [x]亚特兰大, [x]朱诺, [x]阿基里斯, [x]阿贾克斯, [x]阿瑞托莎, [x]加拉蒂亚, [ ]五十铃(貉), [ ]莱比锡, [ ]火奴鲁鲁, [ ]川内(貆), [ ]斐济, [ ]牙买加
  - 精锐:
    - [x]海伦娜, [x]克利夫兰, [ ]哥伦比亚, [ ]谢菲尔德, [ ]爱丁堡, [ ]欧若拉, [x]夕张(狐), [ ]最上(猨), [ ]三隈(狻), [ ]逸仙, [ ]宁海, [ ]平海, [ ]圣路易斯, [ ]神通(貎), [ ]阿贺野(豼), [ ]丹佛, [ ]小贝法, [x]埃米尔·贝尔汀, [ ]涅普顿
  - 超稀有:
    - [x]圣地亚哥, [ ]贝尔法斯特, [ ]阿芙乐尔, [x]蒙彼利埃, [ ]绀紫之心
  - 方案:
    - [ ]海王星
- 重巡:
  - 常见:
    - [x]彭萨科拉, [x]盐湖城, [x]古鹰(狼), [x]加古(狌), [x]青叶(犹), [x]衣笠(猅)
  - 稀有:
    - [x]北安普敦, [x]芝加哥, [x]波特兰, [x]什罗普郡, [x]肯特, [x]萨福克, [x]诺福克, [x]妙高(獌), [ ]那智(狏), [x]苏塞克斯
  - 精锐:
    - [x]休斯敦, [x]印第安纳波利斯, [x]阿斯托利亚, [x]昆西, [x]文森斯, [ ]威奇塔, [x]伦敦, [ ]多塞特郡, [x]约克, [x]埃克塞特, [x]希佩尔海军上将, [x]德意志, [ ]斯佩伯爵海军上将, [ ]诺瓦露
  - 超稀有:
    - [x]高雄(獒), [x]爱宕(犬), [ ]摩耶(犮), [ ]鸟海(猋), [x]欧根亲王, [ ]圣黑之心
  - 方案:
    - [ ]伊吹(峦), [ ]罗恩, [ ]路易九世
- 战巡:
  - 稀有:
    - [x]反击
  - 精锐:
    - [x]声望, [ ]金刚(鲤), [ ]比叡(鲟), [ ]榛名(鲑), [ ]雾岛(鳗), [ ]沙恩霍斯特, [ ]格奈森瑙, [x]敦刻尔克
  - 超稀有:
    - [x]胡德
- 战列:
  - 常见:
    - [x]内华达, [x]俄克拉荷马
  - 稀有:
    - [x]宾夕法尼亚, [x]田纳西, [x]加利福尼亚, [x]扶桑(魟), [x]山城(鲼), [ ]伊势(鳌), [ ]日向(螯)
  - 精锐:
    - [x]亚利桑那, [ ]科罗拉多, [ ]马里兰, [ ]西弗吉尼亚, [x]伊丽莎白女王, [x]纳尔逊, [x]罗德尼, [ ]陆奥(鲛)
  - 超稀有:
    - [ ]北卡罗来纳, [ ]华盛顿, [x]南达科他, [x]厌战, [ ]威尔士亲王, [ ]约克公爵, [ ]长门(鲨), [ ]提尔比茨, [ ]三笠(鲐), [ ]让·巴尔, [x]马萨诸塞
  - 方案:
    - [ ]君主, [ ]出云(侌)
- 航母:
  - 稀有:
    - [ ]胡蜂
  - 精锐:
    - [x]列克星敦, [x]萨拉托加, [x]约克城, [x]大黄蜂, [x]皇家方舟, [ ]光荣, [x]苍龙(蛟), [x]飞龙(龙), [ ]贝露
  - 超稀有:
    - [ ]企业, [x]光辉, [ ]胜利, [x]赤城(凰), [x]加贺(鸾), [ ]翔鹤(鹬), [ ]瑞鹤(鹤), [x]齐柏林伯爵, [ ]翡绿之心
- 轻航:
  - 常见:
    - [x]博格, [x]兰利, [x]突击者, [x]竞技神
  - 稀有:
    - [x]长岛, [ ]飞鹰(鸱), [ ]隼鹰(鸢), [x]祥凤(鹞)
  - 精锐:
    - [x]独角兽, [ ]凤翔(凤)
- 重炮:
  - 精锐:
    - [x]黑暗界, [x]恐怖, [ ]阿贝克隆比
- 维修:
  - 精锐:
    - [x]女灶神
  - 超稀有:
    - [ ]明石(茗)
- 潜艇:
  - 精锐:
    - [ ]伊26, [x]伊58, [ ]鲦鱼, [ ]U-557, [x]絮库夫
  - 超稀有:
    - [ ]伊19, [ ]U-81, [x]U-47
- 改造:
  - 驱逐:
    - [ ]卡辛.改, [ ]唐斯.改, [ ]拉菲.改, [ ]哈曼.改, [ ]阿卡司塔.改, [ ]热心.改, [ ]彗星.改, [ ]新月.改, [ ]小天鹅.改, [ ]狐提.改, [ ]命运女神.改, [ ]标枪.改, [ ]绫波.改, [ ]不知火.改, [x]Z23.改, [ ]贝利.改, [ ]神风.改, [ ]松风.改, [ ]睦月.改, [ ]尼古拉斯.改, [ ]滨风.改, [ ]谷风.改, [ ]福尔班.改, [ ]勒马尔.改
  - 重巡:
    - [ ]波特兰.改, [ ]萨福克.改, [ ]埃克塞特.改, [ ]古鹰.改, [ ]加古.改
  - 战列:
    - [ ]内华达.改, [ ]俄克拉荷马.改, [ ]扶桑.改, [ ]山城.改
  - 轻航:
    - [ ]长岛.改, [ ]博格.改, [ ]兰利.改, [ ]突击者.改, [ ]祥凤.改
  - 航母:
    - [ ]萨拉托加.改
  - 轻巡:
    - [ ]利安得.改, [ ]阿基里斯.改, [ ]阿贾克斯.改, [ ]阿武隈.改, [ ]最上.改, [ ]卡尔斯鲁厄.改, [ ]宁海.改, [ ]平海.改, [ ]川内.改, [ ]神通.改
`.trim()

var equipmentOwnInfo = `
#驱逐主炮:
138.6mm单装炮Mle1929T3金(3): 2+0/15
138.6mm单装炮Mle1929T2紫(4): 6+71/10
双联装127mm高平两用炮MK12T3金(3): 0+12/15
双联装120mm主炮T3紫(6): 6+72/10
76mm火炮T3蓝(2): 2
双联100mm98式高射炮T3金(3): 0
127mm单装炮T3紫(3): 3+1/10

#副炮用驱逐主炮:
双联装128mmSKC41高平两用炮T3紫(4): 7+5/10

#轻巡主炮:
试作型三联装152mm主炮T0金(2): 0+0/25
双联装TbtsKC36式150mm主炮T3紫(6): 3+2/10
155mm三连装炮T3金(3): 0

#重巡主炮:
双联装203mmSKC主炮T3金(3): 2+2/15
试作型三联装203mm舰炮T0金(3): 0+15/25
203mm连装炮T3紫(0): 2

#战列主炮:
双联装381mm主炮.改T0金(2): 0+13/25
410mm连装炮T3紫(3): 3+1/10
三联装406mm主炮MK6T3紫(2): 1
三联283mmSKC34主炮T3紫(2): 1+4/10

#副炮用轻巡主炮:
双联装152mm主炮T3紫(3): 4+4/10
三联装152mm主炮T3紫(0): 6

#鱼雷:
四联装533mm磁性鱼雷T3金(3): 1
四联装610mm鱼雷T3金(3): 0+7/15
五联装533mm磁性鱼雷T3彩(3): 0
五联装533mm鱼雷T3金(3): 2+2/15
五联装533mm磁性鱼雷T2金(0): 1

#防空炮:
双联装113mm高射炮T3金(6): 0+4/15
双联装40mm博福斯STAAGT0金(3): 0+20/25
100mm连装高炮T0金(3): 0+13/25
双联105mmSKC高炮T3金(6): 0+2/15
四联40mm博福斯对空机炮T3金(3): 1+5/15
双联装113mm高射炮T2紫(3): 3
127mm连装高射炮T3紫(3): 0+4/10
四联40mm博福斯对空机炮T2紫(3): 4

#战斗机:
F6F地狱猫T3金(4): 0+4/15
F4U海盗T3紫(0): 3+8/10
XF5F天箭T0紫(1): 0
Me-155A舰载战斗机T3金(2): 2+1/15
零战五二型T3金(2): 1+2/15

#鱼雷机:
#平行雷
梭鱼T3金(4): 3+2/15
#集束雷
流星T3金(4): 0+3/15
天山T3紫(4): 3+4/10
#减速
剑鱼(818中队)T0金(1): 0

#轰炸机:
SB2C地狱俯冲者T3紫(7): 6+6/10
海燕T3紫(3): 4+1/10
彗星T3金(0): 1

#设备:
#通用肉装
高性能舵机T0金(6): 0+9/25
灭火器T3蓝(8): 11+3/5
维修工具T3紫(12): 6+1/10
维修工具T2蓝(0): 10
防鱼雷隔舱T3紫(3): 3+1/10
海军迷彩T3蓝(3): 7
液压舵机T3蓝(3): 6

#航母
液压弹射装置T3金(6): 3+1/15
航空副油箱T3紫(3): 4

#炮击
一式穿甲弹T3金(6): 1
超重弹T3金(6): 1
火控雷达T3紫(3): 1+9/10

#雷击
九三式纯氧鱼雷T3彩(6): 0
九三式纯氧鱼雷T2金(2): 1

#其他
高性能对空雷达T0金(4): 0+12/25
对空雷达T3紫(4): 4
SG雷达T3金(2): 1+1/15
链式装弹机T3紫(4): 3+3/10
改良锅炉T3紫(4): 8+5/10
`.trim()

Array.prototype.contains = function (obj) {
  var i = this.length;
  while (i--) {
    if (this[i] === obj) {
      return true;
    }
  }
  return false;
}

function getShipOwned(setItem) {
  var items = [];
  var count = 0;
  var total = 0;
  var regShip = /\[([x ])\]([^\s(),]+)(?:\(([^\s]+)\))?/g;
  var setText = shipOwnInfo.replace(regShip, function (text, own, name, name2) {
    // console.log(own, name, name2 || "");
    total++;
    if (own == "x") {
      count++;
      console.log(count, own, name, name2 || "");
      items.push(name);
      if (name2) items.push(name2);
      text = '<a class="del" href="http://wiki.joyme.com/blhx/' + name + '" target="_blank">' + text + "</a>";
    } else {
      text = '<a href="http://wiki.joyme.com/blhx/' + name + '" target="_blank">' + text + "</a>";
    }
    return text;
  });
  var describe = "已获得:" + count + "/" + total;
  console.log(describe);
  if (setItem && document.getElementById(setItem)) {
    document.getElementById(setItem).innerHTML = describe + "\n" + setText;
  }
  return items;
}

function getEquipmentWanted(setItem) {
  var items = [];
  var regEquipment = /^(.+?)(T\d)(.)\((\d+)\):\s*(\d+)([+/\d]+)?/gm;
  var setText = equipmentOwnInfo.replace(regEquipment, function (text, name, t, color, want, own, build) {
    console.log(name, t, color, want, own, build || "");
    want = parseInt(want);
    own = parseInt(own)
    if (want > own) {
      items.push(name + t);
      text = '<a href="http://wiki.joyme.com/blhx/' + name + t + '" target="_blank">' + text + "</a>";
    } else {
      text = '<a class="del" href="http://wiki.joyme.com/blhx/' + name + t + '" target="_blank">' + text + "</a>";
    }
    return text;
  });
  if (setItem && document.getElementById(setItem)) {
    document.getElementById(setItem).innerHTML = setText;
  }
  return items;
}
function getEquipmentInfo(setItem) {
  var items = {};
  var bp_default = { "蓝": 5, "紫": 10, "金": 15 };
  var regEquipment = /^(.+?)(T\d)(.)\((\d+)\):\s*(\d+)(\+(\d+)\/(\d+))?/gm;
  var setText = equipmentOwnInfo.replace(regEquipment, function (text, name, t, color, want, own, build, bp_now, bp_each) {
    console.log(name, t, color, want, own, bp_now || "", bp_each || "");
    want = parseInt(want);
    own = parseInt(own);
    bp_now = parseInt(bp_now || 0);
    bp_each = parseInt(bp_each || bp_default[color]);
    if (own + bp_now / bp_each < want) {
      items[name + t] = {"want": want, "own": own, "bp_now": bp_now, "bp_each": bp_each, "own_text": want + ":" + own + "+" + bp_now + "/" + bp_each};
      text = '<a href="http://wiki.joyme.com/blhx/' + name + t + '" target="_blank">' + text + "</a>";
    } else {
      text = '<a class="del" href="http://wiki.joyme.com/blhx/' + name + t + '" target="_blank">' + text + "</a>";
    }
    return text;
  });
  if (setItem && document.getElementById(setItem)) {
    document.getElementById(setItem).innerHTML = setText;
  }
  return items;
}

if (typeof (document) == 'undefined') {
  getShipOwned();
}