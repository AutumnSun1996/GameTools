import re

"""
十香 四糸乃 折纸 琴里 狂三 凛祢
村雨令音 神无月 三人组 殿町 小珠 日下部燎子
<p class="Map">
高台：；池周边：；天宫塔：；住宅街：；站前：；神社：；五河家：；
缓台：；物理准备室：；屋顶：；校舍后：；走廊：；教室：；学校前：；
</p>
<p class="Event ">
<span class="Option">()<br></span>
<span class="Option Choose">()<br></span>
</p>
"""
text = """
　　十香route：

　　6.25

　　正直、ちょっぴり期待しているかも……?(期待なんかしてない!)

　　6.26

　　存档01

　　高台

　　天宮タワー

　　学校前：十香

　　じゃあ、パン屋によってみるか(さ、さすがにもう食い物はちょっと……)

　　住宅街：十香

　　十香なら俺を探しに戻ってくる

　　(十香なら香りに釣られて食べ物屋に行ってる)

　　6.27

　　十香を応援する

　　高台

　　駅前

　　廊下：十香

　　存档03

　　十香の様子がおかしいのでやめる

　　五河家：十香

　　手加減して戦う(本気で勝負する)

　　6.28

　　学校に早めに登校する

　　存档04

　　十香の弁当を食べる(とりあえず逃げる)

　　五河家

　　天宮タワー

　　廊下：十香

　　十香を信じて待つ(やっぱり手伝いに行く)

　　住宅街：十香

　　ブランコに乗ろう(滑り台で遊ぼう)

　　よし!二人乗りしよう!(やっぱりよそう)

　　6.29

　　高台

　　五河家

　　学校前：十香

　　存档05

　　3D超大作!SFアドベンチャー(絶対泣ける!恋愛映画純情派!)

　　池周辺

　　何か話をしてみる(黙って傍にいる)

　　十香を連れて行く

　　6.30

　　新天宮タワー

　　神社

　　駅前：十香

　　うどん屋をのぞいてみる(買い物して早く帰る)

　　★十香アペタイト获得

　　存档06

　　ただの幼馴染

　　7.2

　　存档07

　　出ない

　　十香 END

　　★十香ウェディング 获得

　　读档03

　　気になるので、もう少し上がってみる

　　BAD END 1

　　读档04

　　凜祢の弁当を薦める

　　BAD END 2

　　读档05

　　暗闇で急接近!夏定番ホラー映画!

　　BAD END 3

　　读档06

　　気になる子

　　BAD END 4

　　读档07

　　出る

　　十香フラグEND

　　折纸route：

　　读取存档01

　　■6月26日

　　神社

　　駅前

　　校舎裏：折紙

　　お昼の話(琴里の話)(ASTの話)

　　校舎裏

　　教室

　　学校前：折紙

　　■6月27日

　　折紙を応援する

　　神社

　　校舎裏：折紙

　　一緒に片づけないか?(一緒にさぼらいないか?)

　　物理準備室

　　踊り場

　　廊下：折紙

　　■6月28日

　　学校に早めに登校

　　住宅街

　　神社

　　校舎裏：折紙

　　こえをかける(あとをつける)

　　やってみなよ(無理するな)

　　学校前

　　教室：折紙

　　■6月29日

　　神社

　　住宅街

　　駅前：折紙

　　ジョークを飛ばす(思いきり笑ってみる)

　　神社：折紙

　　折紙といく

　　■6月30日

　　高台

　　天宮タワー

　　住宅街：折紙

　　存档08

　　折紙を追う

　　存档09

　　折紙のこと

　　■7月2日

　　存档10

　　出ない

　　折紙 END

　　★折紙ファミリー获得

　　读取存档08

　　令音の分析を待つ

　　BAD END 5

　　★折紙アクシデント取得

　　读取存档10

　　出る

　　折紙フラグ END

　　读取存档09

　　適当にごまかす

　　BAD END 6

　　四系乃route：

　　■6月26日

　　读取存档01

　　廊下：四糸乃

　　まずはフォローを。素直にあやまっておく(男の子だもん、仕方ないよ。知らぬふりで貫き通す)

　　校舎裏

　　教室

　　五河家：四糸乃

　　失敗は仕方ない。ひたすらになぐさめる(ミスはミスだ。一言注意しておく)

　　■6月27日

　　折紙を応援する

　　五河家

　　住宅街

　　学校前：四糸乃

　　何事も経験が大事。四糸乃をはげまし送り出す(やっぱり心配。自分で買いに行く)

　　駅前：四糸乃

　　■6月28日

　　<フラクシナス>に四糸乃のお見舞い

　　ベッドの下を調べる

　　更衣室を調べる

　　医務官のデスクを調べる

　　教室：四糸乃

　　ストレス解放が大事。四糸乃のしたいことをさせてやる(外に出しておくのは危険。すぐ家に帰らせる)

　　学校前

　　五河家：四糸乃

　　何事も勉強が大事。このまま見せ続けてやる(四糸乃にはまだ早い。ビデオを取り上げる)

　　■6月29日

　　校舎裏

　　屋上

　　踊り場：四糸乃

　　ドキドキ作戦、お化け屋敷へGO!(ラブラブ空間、観覧車でふたりきりだ!)

　　五河家：四糸乃

　　存档12

　　もう少し、四糸乃と一緒に夕日を見よう(あんまり遅くなるといけない。家に連れて帰ろう)

　　四糸乃を連れて行く

　　■6月30日

　　天宮タワー

　　踊り場

　　学校前：四糸乃

　　存档11

　　四糸乃には俺がいるよ(一緒によしのんを待とう)

　　■7月2日

　　存档10

　　出ない

　　四糸乃 END

　　★四糸乃ロリータ

　　读取存档10

　　出る

　　四糸乃フラグ END

　　读取存档11

　　最初からいなかったと思えばいいさ

　　BAD END 7

　　读取存档12

　　あんまり遅くなるといけない。家に連れて帰ろう

　　一人で行く

　　■6月30日

　　踊り場

　　天宮タワー

　　池周辺：十香

　　黙って傍にいる

　　BAD

　　END 8

　　琴里route：

　　※2週目以降に最初から

　　プロローグをスキップする

　　■6月26日

　　高台

　　天宮タワー

　　踊り場：琴里

　　やはり放っておけない(琴里に従う)

　　踊り場：琴里

　　■6月27日

　　凜祢を応援する

　　高台

　　駅前

　　存档13

　　物理準備室：琴里

　　高台：琴里

　　■6月28日

　　学校に早めに登校する

　　五河家

　　天宮タワー

　　学校前：琴里

　　まだまだ子供だな。しばらくこのまま眺めてる(琴里も乙女だ。起こして、見えそうだと忠告する)

　　駅前：琴里

　　この熱い思いは止められない。いきなり抱きしめる!(俺の全てを見てくれ。いきなり服を脱ぎ始める!)

　　■6月29日

　　高台

　　五河家

　　廊下：琴里

　　駅前：琴里

　　ここは前向きに励まそう。「琴里らしくないぞ!」

　　(やっぱりいたわってやろう。「ゆっくり休めよ」)

　　琴里と行く

　　■6月30日

　　新天宮タワー

　　神社

　　廊下：琴里

　　このままにはしておけない。手を貸してやろう

　　(動くのもつらそうだ。しばらく様子をみよう。)

　　存档14

　　俺に手伝える事はないか?(大変だと思うけど、がんばれよ)

　　■7月2日

　　存档15

　　出ない

　　琴里

　　END

　　★琴里フォーチュン

　　读档15

　　出る

　　琴里フラグ END

　　读档14

　　忙しいみたいだな

　　BAD END 9

　　狂三route：

　　读档13

　　教室：狂三

　　敵対の意思はなさそうだ。狂三を信じる

　　(何か隠してるに違いない。狂三は信じられない)

　　住宅街：狂三

　　怖くないって言ったら嘘になる(怖くなんてない)

　　■6月28日

　　学校に早めに登校

　　屋上：狂三

　　新天宮タワー：狂三

　　……何か違和感を感じるんだ(天宮市の誇りだって思うよ)

　　行く(行かない)

　　■6月29日

　　教室：狂三

　　住宅街：狂三

　　一人で行く

　　■6月30日

　　教室：狂三

　　存档16

　　……分からない

　　■7月2日

　　存档17

　　出ない

　　狂三 END

　　★狂三リメイン

　　读档16

　　封印したい

　　BAD END 10

　　读档16

　　……『敵』、なんだろうな

　　BAD END 11

　　读档17

　　出る

　　狂三フラグ END

　　凛弥route：

　　■6月25日

　　期待なんかしてない!

　　■6月26日

　　教室：凜祢

　　駅前：凜祢

　　存档18

　　インターフォンを押さない

　　■6月27日

　　凜祢を応援する

　　踊り場：凜祢

　　天宮タワー

　　■6月28日

　　存档19

　　凜祢を心配する

　　■6月29日

　　■6月30日

　　存档20

　　みんなとのデート

　　■7月1日

　　存档21

　　こうしていちゃ、駄目だ

　　凜祢　END

　　★凜祢ユートピア

　　读取存档18

　　インターフォンを押す

　　BADEND12

　　读取存档19

　　凜祢を問い詰める

　　BADEND13

　　读取存档20

　　凜祢との日々

　　BADEND14

　　读取存档21

　　ずっと、こうしていたい

　　BADEND15
"""
place = "校舎裏|駅前|神社|学校前|高台|天宮タワー|住宅街|新天宮タワー|池周辺|五河家|廊下|踊り場"
regex = [
    (re.compile(r"^■?(\d+)[.月](\d+)日?$"), "{0}/{1}", 'Date'),
    (re.compile(r"^存档(\d+)$"), "存档{}", 'Save'),
    (re.compile(r"^读取?存?档(\d+)$"), "读档{}", 'Load'),
    (re.compile(r"^(.+)route", re.I), "{0}Route", "Route"),
    (re.compile(r"^(.+end.*)$", re.I), "{0}", "End"),
    (re.compile(r"^(★.+)$", re.I), "{0}", "End"),
    (re.compile(r"^(" + place + ")：?(.*)$"), "{0}:{1}", 'Place'),
    (re.compile(r"^(.+)\((.*)\)$"), "{0}<br>\n{1}", 'Options'),
    (re.compile(r"^\(?(.+)\)?$"), "{0}", 'Options'),
]


class Builder:
    def __init__(self):
        self.date = ""
        self.route = ""
        self.text = ""
        self.map = ""
        self.last = ""

    def set_map(self):
        if self.map:
            self.text += self.map
            self.text += "</p>"
            self.map = ""

    def output(self, formatter, kind, args):
        if not isinstance(args, tuple):
            args = [args, '']
        # print(formatter.format(*args))
        if kind == "Place":
            if not self.map:
                self.map = '<div class="MapChoice">\n<p class="Map">\n'
            self.map += "{}：{}；".format(*args)
            self.last = kind
        else:
            self.set_map()
        if kind == "Date":
            if self.text:
                self.text += "\n</div>\n"
            self.date = "{}/{}".format(*args)
            self.text += '<div date="{}/{}">\n'.format(*args)
            self.last = kind
        elif kind == "Save":
            self.text += '<mark class="Save">Save {}</mark>'.format(*args)
        elif kind == "Load":
            self.text += '<mark class="Load">Load {}</mark>'.format(*args)
        elif kind == "Route":
            self.route = args[0]
        elif kind == "End":
            self.text += '<mark class="End">{}</mark>'.format(*args)
        elif kind == "Options":
            # print("Options", self.last)
            if self.last == 'Place':
                self.text += '''
                <p class="Event {}">
                    <span class="Option Choose">({})<br></span>
                    <span class="Option">({})<br></span>
                </p>
                </div>
                '''.format(self.route, *args)
            else:
                self.text += '''
                <p class="Choice">
                    <span class="Option {}">({})<br></span>
                    <span class="Option">({})<br></span>
                </p>
                '''.format(self.route, *args)
            self.last = kind


def out01(text=text):
    b = Builder()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for item in regex:
            data = item[0].findall(line)
            if data:
                b.output(item[1], item[2], data[0])
                break

    print(b.text)
    print("</div>")


places = "高台 池周边 天宫塔 住宅街 站前 新天宫塔 神社 五河家".split(' ') + "缓台 物理准备室 屋顶 校舍后 走廊 教室 学校前".split(' ')
names = set("十香 折纸 四糸乃 琴里 狂三 凛祢".split(' '))


def get_map(text):
    text = re.sub("</?span[^<>]*>", '\n', text)
    text = re.sub("\s+", '\n', text)
    d = {}
    for item in text.split('\n'):
        if not item:
            continue
        place, name = item.split('：')
        if name:
            d[place] = name
            print('item', item)
    html = ''
    # html += '<p class="Map">\n'
    for place in places:
        name = d.get(place, '')
        if name in names:
            chara = ' ' + name
        elif name:
            chara = " ExtraCharacter"
        else:
            chara = ''
            continue
        if name in ['琴里', "狂三"]:
            chara = ", Condition: 'cond.十香 || cond.四糸乃 || cond.折纸'"
        elif name in ['凛祢']:
            chara = ", Condition: 'cond.十香 && cond.四糸乃 && cond.折纸 && cond.琴里 && cond.狂三'"
        else:
            chara = ''
        # html += '<span class="Place{}">{}：{}</span>\n'.format(chara, place, name)
        html += """,\n{l} Place: '{1}', Character: '{2}'{0} {r}""".format(chara, place, name, l='{', r='}')
    # html += "</p>"
    print('\n')
    print(html.strip())


if __name__ == '__main__':
    """
十香 四糸乃 折纸 琴里 狂三 凛祢
村雨令音 神无月 三人组 殿町 小珠 日下部燎子
# """
    #     get_map("""
    # 高台：
    # 池周边：
    # 天宫塔：
    # 住宅街：
    # 站前：
    # 新天宫塔：
    # 神社：
    # 五河家：
    #
    # 缓台：
    # 物理准备室：
    # 屋顶：
    # 校舍后：
    # 走廊：
    # 教室：
    # 学校前：
    #
    # 高台：村雨令音
    # 池周边：十香
    # 天宫塔：三人组
    # 住宅街：狂三
    # 神社：折纸
    # 屋顶：殿町
    # 校舍后：小珠
    #     """)
    for name in "十香 折纸 四糸乃 琴里 狂三 凛祢".split(' '):
        print("""<label for="Check{0}">{0}</label>
<input id="Check{0}" type="radio" name="target" value="{0}" onchange="toggleTarget()">""".format(name))
