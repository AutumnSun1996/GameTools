/**
 * Created by q1996 on 2017/08/25.
 */

// log = console.log;
function log() {
}
function output(obj) {
    if (obj.Character) {
        console.log(obj.Place + ": " + obj.Character);
    } else if (obj.ch) {
        console.log(obj.ch);
    } else {
        console.log(obj);
    }
}
Array.prototype.has = function (item) {
    return this.indexOf(item) >= 0;
};
Array.prototype.last = function () {
    return this[this.length - 1];
};
var MainCharacters = new Array("十香 四糸乃 折纸 琴里 狂三 凛祢".split(' '));
var cond = {};
var target = {Name: '十香', Date: '6/21'};
var 二周目 = {
    Checker: 'cond.十香 || cond.四糸乃 || cond.折纸',
    Describe: "开始二周目",
    Update: {十香: 1}
};
var 攻略其他角色 = {
    Checker: "cond.十香 && cond.四糸乃 && cond.折纸 && cond.琴里 && cond.狂三",
    Describe: "攻略其他所有角色",
    Update: {十香: 1, 四糸乃: 1, 折纸: 1, 琴里: 1, 狂三: 1}
};
var routes = [
    {Character: "十香", Result: "十香GoodEnd", Enabled: 1},
    {Character: "十香", Result: "十香BadEnd", Start: "Save 03"},
    {Character: "十香", Result: "十香BadEnd", Start: "Save 04"},
    {Character: "十香", Result: "十香BadEnd", Start: "Save 05"},
    {Character: "十香", Result: "十香BadEnd", Start: "Save 06"},
    {Character: "十香", Result: "十香FlagEnd", Start: "Save 07"},
    {Character: "折纸", Result: "折纸GoodEnd", Enabled: 1},
    {Character: "折纸", Result: "折纸BadEnd", Start: "Save 08"},
    {Character: "折纸", Result: "折纸BadEnd", Start: "Save 09"},
    {Character: "折纸", Result: "折纸BadEnd", Start: "Save 10"},
    {Character: "折纸", Result: "折纸BadEnd", Start: "Save 11"},
    {Character: "折纸", Result: "折纸BadEnd", Start: "Save 12"},
    {Character: "四糸乃", Result: "四糸乃GoodEnd", Enabled: 1},
    {Character: "四糸乃", Result: "四糸乃BadEnd", Start: "Save 03"},
    {Character: "琴里", Condition: 二周目, Result: "琴里GoodEnd", Enabled: 1},
    {Character: "狂三", Condition: 二周目, Result: "狂三GoodEnd", Enabled: 1, Start: "Save 13"},
    {Character: "凛祢", Condition: 攻略其他角色, Result: "凛祢GoodEnd", Enabled: 1},
    {Character: "凛祢", Result: "凛祢IfEnd", Enabled: 1, Start: ""}
];
var choices = [
    {
        Name: 'Start',
        Date: "6/22",
        Condition: 'cond.十香 || cond.四糸乃 || cond.折纸',
        Choices: [{
            Type: 'Choice',
            Condition: 'cond.十香 || cond.四糸乃 || cond.折纸',
            Options: [{
                ch: "序言",
                routes: ["十香", "四糸乃", "折纸", "凛祢"]
            }, {
                ch: "跳过序言",
                jp: "プロローグをスキップする",
                routes: ["琴里", "狂三"]
            }]
        }]
    }, {
        Date: "6/25",
        Choices: [{
            Type: 'Choice',
            Save: "Save 01",
            Options: [{
                ch: "才没有期待呢!",
                jp: "期待なんかしてない!",
                routes: ["凛祢"]
            }, {
                ch: "说实话，其实有点期待",
                jp: "正直、ちょっぴり期待しているかも……?",
                routes: ["十香", "四糸乃", "折纸"]
            }]
        }]
    }, {
        Date: "6/26",
        Choices: [
            {
                Type: "Map",
                Options: [
                    {Place: '高台', Character: '村雨令音', routes: ["十香"], Memory: "村雨令音01"},
                    {Place: '天宫塔', Character: '神无月', routes: ["十香"], Memory: "神无月01"},
                    {Place: '站前', Character: '三人组', Memory: "三人组01"},
                    {Place: '神社', Character: '日下部燎子', Memory: "日下部燎子01"},
                    {Place: '缓台', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '走廊', Character: '四糸乃'},
                    {
                        Place: '校舍后',
                        Character: '折纸',
                        EventChoices: [{
                            Options: [{
                                ch: "琴里的事",
                                jp: "琴里の話"
                            }, {
                                ch: "中午的事",
                                jp: "お昼の話",
                                routes: ['折纸']
                            }, {
                                ch: "AST的事",
                                jp: "ASTの話"
                            }]
                        }]
                    },
                    {
                        Place: '学校前',
                        Character: '十香',
                        EventChoices: [{
                            Options: [{
                                ch: "那好，去面包店吧",
                                jp: "じゃあ、パン屋によってみるか",
                                routes: ["十香"]
                            }, {
                                ch: "吃、吃的东西还是算了吧……",
                                jp: "さ、さすがにもう食い物はちょっと……"
                            }]
                        }]
                    }
                ]
            }, {
                Type: "Map",
                Options: [
                    {
                        Place: '住宅街',
                        Character: '十香',
                        EventChoices: [{
                            Options: [{
                                ch: "十香会被香味吸引到卖吃的的地方去",
                                jp: "十香なら香りに釣られて食べ物屋に行ってる"
                            }, {
                                ch: "十香会回来找我",
                                jp: "十香なら俺を探しに戻ってくる",
                                routes: ["十香"]
                            }]
                        }]
                    },
                    {
                        Place: '学校前',
                        Character: '折纸'
                    }
                ]
            }
        ]
    }, {
        Date: "6/27",
        Choices: [
            {
                Type: 'Choice',
                Options: [{
                    ch: '给十香加油',
                    jp: '十香を応援する',
                    routes: ["十香"]
                }, {
                    ch: '给折纸加油',
                    jp: '折紙を応援する',
                    routes: ["折纸"]
                }, {
                    ch: '给凛祢加油',
                    jp: '凛祢を応援する',
                    routes: ["凛祢"]
                }]
            }, {
                Type: "Map",
                Options: [
                    {Place: '高台', Character: '村雨令音', routes: ["十香"]},
                    {Place: '住宅街', Character: '小珠'},
                    {Place: '站前', Character: '神无月', routes: ["十香"]},
                    {Place: '神社', Character: '三人组'},
                    {Place: '物理准备室', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '校舍后', Character: '折纸'},
                    {
                        Place: '教室',
                        Character: '十香',
                        EventChoices: [{
                            Save: 'Save 03',
                            Options: [{
                                ch: "太令人在意了，继续向上走走看",
                                jp: "気になるので、もう少し上がってみる",
                                result: "十香BadEnd"
                            }, {
                                ch: "十香的样子有点怪，还是回去吧",
                                jp: "十香の様子がおかしいのでやめる",
                                routes: ["十香"]
                            }]
                        }]
                    },
                    {Place: '学校前', Character: '四糸乃'}
                ]
            }, {
                Type: "Map",
                Options: [
                    {Place: '站前', Character: '四糸乃'},
                    {Place: '神社', Character: '三人组'},
                    {Place: '缓台', Character: '小珠'},
                    {Place: '物理准备室', Character: '村雨令音'},
                    {
                        Place: '五河家',
                        Character: '十香',
                        EventChoices: [{
                            Options: [{
                                ch: "使出全力决胜负",
                                jp: "本気で勝負する"
                            }, {
                                ch: "稍有保留的决胜负",
                                jp: "手加減して戦う",
                                routes: ["十香"]
                            }]
                        }]
                    },
                    {Place: '走廊', Character: '折纸'},
                    {Place: '学校前', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '住宅街', Character: '狂三', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'}
                ]
            }
        ]
    }, {
        Date: "6/28",
        Choices: [
            {
                Type: 'Choice',
                Options: [{
                    ch: '去 世界树 探望',
                    jp: 'フラクシナス',
                    routes: ["四糸乃"]
                }, {
                    ch: '早点去学校',
                    jp: '学校に早めに登校する',
                    routes: ["十香", "折纸"]
                }]
            }, {
                Type: 'Choice',
                Condition: "target.Name == '十香'",
                Save: "Save 04",
                Options: [
                    {
                        ch: '领十香的便当',
                        jp: '十香の弁当を食べる',
                        routes: ["十香"]
                    }, {
                        ch: '推荐凜祢的便当',
                        jp: '凜祢の弁当を薦める',
                        result: "十香BadEnd"
                    }, {
                        ch: '大事不好赶快逃跑',
                        jp: 'とりあえず逃げる'
                    }
                ]
            }, {
                Type: 'Choice',
                Condition: "target.Name == '四糸乃'",
                Options: []
            }, {
                Type: "Map",
                Options: [
                    {Place: '天宫塔', Character: '神无月', routes: ["十香"]},
                    {Place: '住宅街', Character: '日下部燎子'},
                    {Place: '神社', Character: '三人组'},
                    {Place: '五河家', Character: '村雨令音', routes: ["十香"]},
                    {Place: '校舍后', Character: '折纸'},
                    {
                        Place: '走廊',
                        Character: '十香',
                        EventChoices: [{
                            Options: [{
                                ch: '果然还是去帮忙吧',
                                jp: 'やっぱり手伝いに行く'
                            }, {
                                ch: '相信十香，在这里等',
                                jp: '十香を信じて待つ',
                                routes: ["十香"]
                            }]
                        }]
                    },
                    {Place: '教室', Character: '四糸乃'},
                    {Place: '学校前', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '屋顶', Character: '狂三', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'}
                ]
            }, {
                Type: "Map",
                Options: [
                    {Place: '高台', Character: '日下部燎子'},
                    {
                        Place: '住宅街', Character: '十香', EventChoices: [{
                        Options: [{
                            ch: "来坐秋千吧",
                            jp: "ブランコに乗ろう",
                            routes: ['十香'],
                            EventChoices: [{
                                Options: [{
                                    ch: "好！两个人一起来！",
                                    jp: "よし!二人乗りしよう!",
                                    routes: ['十香']
                                }, {
                                    ch: "还是算了吧",
                                    jp: "やっぱりよそう"
                                }]
                            }]
                        }, {
                            ch: "来玩滑梯吧 ",
                            jp: "滑り台で遊ぼう",
                            trophy: "十香スライド"
                        }]
                    }]
                    },
                    {Place: '站前', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '新天宫塔', Character: '狂三', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '神社', Character: '三人组'},
                    {Place: '五河家', Character: '四糸乃'},
                    {Place: '缓台', Character: '小珠'},
                    {Place: '教室', Character: '折纸'},
                    {Place: '学校前', Character: '殿町'}
                ]
            }
        ]
    }, {
        Date: "6/29",
        Choices: [
            {
                Type: "Map",
                Options: [
                    {Place: '高台', Character: '村雨令音', routes: ["十香"]},
                    {Place: '住宅街', Character: '三人组'},
                    {Place: '站前', Character: '折纸'},
                    {Place: '五河家', Character: '神无月', routes: ["十香"]},
                    {Place: '屋顶', Character: '殿町'},
                    {Place: '校舍后', Character: '小珠'},
                    {Place: '走廊', Character: '琴里', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {Place: '教室', Character: '狂三', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'},
                    {
                        Place: '学校前', Character: '十香',
                        EventChoices: [{
                            Save: "Save 05",
                            Options: [{
                                ch: "3D超大作！SF冒险类影片！",
                                jp: "3D超大作!SFアドベンチャー!",
                                routes: ['十香']
                            }, {
                                ch: "绝对让你流泪！纯情派恋爱电影！",
                                jp: "絶対泣ける!恋愛映画純情派!"
                            }, {
                                ch: "疾行于黑暗中！夏天必看的恐怖片！",
                                jp: "暗闇で急接近!夏定番ホラー映画!",
                                result: "十香BadEnd"
                            }]
                        }]
                    }
                ]
            },
            {
                Type: "Map",
                Options: [
                    {Place: '高台', Character: '村雨令音'},
                    {Place: '天宫塔', Character: '三人组'},
                    {Place: '屋顶', Character: '殿町'},
                    {Place: '校舍后', Character: '小珠'},
                    {Place: '池周边', Character: '十香'},
                    {Place: '神社', Character: '折纸'},
                    {Place: '住宅街', Character: '狂三', Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'}
                ]
            },
            {
                Type: "Choice",
                Options: [{
                    ch: "带十香一起去",
                    jp: "十香を連れて行く",
                    routes: ["十香"]
                }, {
                    ch: "和折纸一起去",
                    jp: "折紙といく",
                    routes: ["折纸"]
                }, {
                    Condition: "cond.十香 || cond.四糸乃 || cond.折纸",
                    ch: "一个人去",
                    jp: "",
                    routes: [""]
                }]
            }
        ]
    }, {
        Date: "6/30",
        Choices: [
            {
                Type: "Map",
                Options: []
            }
        ]
    }, {
        Date: "7/1",
        Condition: 'target.Name == "凛祢"',
        Choices: []
    }, {
        Date: "7/2",
        Choices: []
    }
];

function isTarget(option) {
    if (option.routes) {

        output('ExtraChoice', option);
    } else {
        output('ExtraChoice', option);
    }
}

function checkChoice(choice) {
    log("checkChoice", choice);
    if (choice.Condition && !eval(choice.Condition)) {
        log("Skip For Condition:", choice.Condition);
        return null;
    }
    if (choice.Save) {
        output(choice.Save);
        target.routes.forEach(function (route) {
            if (route.Start == choice.Save) {
                console.log("Start", route);
                route.Enabled = true;
                route.steps.push(choice.Save);
            }
        });
    }
    target.routes.forEach(function (route) {
        if (route.Enabled) {
            var tmp = JSON.parse(JSON.stringify(choice));
            route.steps.push(tmp);
        }
    });
    for (var idx=0;idx < choice.Options.length;idx++){
        var option = choice.Options[idx];
    // }
    // choice.Options.forEach(function (option, idx) {
        log("option for checkChoice", option);
        if (option.result) {
            target.routes.forEach(function (route) {
                if (route.Enabled && route.Result == option.result) {
                    route.steps.last().Choose = idx;
                    route.Enabled = 0;
                    break;
                }
            });
        }
        if ((option.routes && option.routes.has(target.Name)) || option.Character == target.Name) {
            output(option);
            target.routes.forEach(function (route) {
                if (route.Enabled) {
                    route.steps.last().Choose = idx;
                }
            });
            if (option.EventChoices) {
                option.EventChoices.forEach(checkChoice);
            }
        }
    }
    // );
}

function getRoute() {
    target.routes = [];
    routes.forEach(function (obj) {
        if (obj.Character == target.Name) {
            log(obj);
            obj.steps = [];
            target.routes.push(obj);
            if (obj.Condition && !eval(obj.Condition.Checker)) {
                log('需要' + obj.Condition.Describe);
                Object.assign(cond, obj.Condition.Update);
                log('Updated Condition:', cond);
            }
        }
    });
    if (!target.routes) return null;
    log(cond);
    choices.forEach(function (day) {
        log("Check Day:", day.Name || day.Date);
        if (day.routes && !(target.Name in day.routes)) {
            log("Skip For Routes:", target.Name, day.routes);
            return null;
        }
        if (day.Condition && !eval(day.Condition)) {
            log("Skip For Condition:", day.Condition);
            return null;
        }
        if (target.Date && day.Date < target.Date) {
            log("Skip For :", day.Date, target.Date);
            return null;
        }
        output(day.Name || day.Date);
        day.Choices.forEach(checkChoice);
    });
}
cond = {'十香': 1};
// target = {Name: '琴里', Date: '6/21'};
target = {Name: '十香', Date: '6/21', DecideSubCharacters: 1};
getRoute();
target.routes.forEach(function (route) {
    console.log(route);
});

// console.log(JSON.stringify(二周目));
// console.log(JSON.stringify(攻略其他角色));
// console.log(JSON.stringify(routes));
