import numpy as np
import re
import xlrd


short_dict = {
    '航': {'正航', '轻航'},
    '战': {'战列', '战巡', '航战'},
    '驱': {'驱逐'},
    '巡': {'轻雷巡', '重雷巡', '炮巡'},
    '潜': {'潜艇'}
}


def parsed(value):
    if isinstance(value, str):
        return value.strip()
    return value


def get_cell(sheet, i, j):
    for x0, x1, y0, y1 in sheet.merged_cells:
        if x0 == i and y0 == j:
            break
        if x0 <= i < x1 and y0 <= j < y1:
            return parsed(sheet.cell(x0, y0).value)
    return parsed(sheet.cell(i, j).value)


def load_talents(path='天赋.xlsx', name_row=2, split_idx=None):
    if split_idx is None:
        split_idx = [4, 16]

    doc = xlrd.open_workbook(path)
    sheet = doc.sheet_by_index(0)
    print("{}: {}x{}".format(sheet.name, sheet.ncols, sheet.nrows))

    data = []
    for i in range(sheet.nrows):
        row = []
        for j in range(sheet.ncols):
            row.append(get_cell(sheet, i, j))
        data.append(row)

    names = data[name_row]
    a, b = split_idx
    desc = names[:a]
    score = names[a:b]
    chance = names[b:]

    info = {}
    for line in data[3:]:
        if not any(line):
            continue
        item = {
            'name': line[0],
            'desc': dict(zip(names, line[:a])),
            'scores': dict(zip(score, line[a:b])),
            'chance': dict(zip(chance, line[b:])),
        }
        name = item['name']
        if name not in info:
            info[name] = item
        else:
            info[name]['desc'].append(item['desc'])
            for key in score:
                if item['scores'][key]:
                    info[name]['scores'][key] = item['scores'][key]
        if name == '':
            print(line)

    for item in info.values():
        for key in score:
            if item['scores'][key] == '':
                del item['scores'][key]
    return info


talents_info = load_talents()


def sort_talents(fleet, talents=None):
    if talents is None:
        talents = talents_info

    def key(item):
        item['ScoreInfo'] = []
        score = 0
        for key in fleet:
            score_add = item['scores'].get(key, 0) * fleet[key]
            if score_add:
                item['ScoreInfo'].append(
                    (key, fleet[key], item['scores'][key],))
                score += score_add
        item['Score'] = score
        return -score

    ship_count = sum(fleet.values())
    items = list(talents.values())
    items.sort(key=key)
    items = [{
        'score': item['Score'],
        'name': item['name'],
        'scoreInfo': item['ScoreInfo']}
        for item in items if item['Score'] > 0]
    return items


def show_scores(scores):
    for i, item in enumerate(scores):
        print(
            '{1:2d}: {0[score]:5.3f}, {0[name]:}  {0[scoreInfo]}'.format(item, i+1))
    print()


def show_talents(fleet, talents=None, limit=None):
    print(fleet)
    items = sort_talents(fleet, talents)
    if limit:
        items = items[:limit]
    show_scores(items)


def search_talent(ship_types, talent_short, info=None):
    if info is None:
        info = talents_info
    candidates = []
    for talent in info.values():
        if talent_short == talent['desc']['简称']:
            candidates.append(talent)
    if len(candidates) == 1:
        return candidates[0]['name']
    for talent in candidates:
        for ship_type in ship_types:
            if talent['scores'].get(ship_type, 0) > 0:
                return talent['name']
    return {"Error": {'ship_types': ship_types, 'talent_short': talent_short}, 'candidates': candidates}


def get_talents(cat):
    if isinstance(cat, str):
        cat = re.search("(?i)^(.)([ac ])(.+)$", cat).groups()
    s_type, s_cmd, s_talents = cat
    ship_types = short_dict[s_type]

    talents = []
    for s in s_talents:
        talents.append(search_talent(ship_types, s))
    return talents


def cat_score(fleet, cat, show_scores=False, info=None):
    if info is None:
        info = talents_info

    talents = {key: info[key] for key in get_talents(cat)}
    scores = sort_talents(fleet, talents)
    total_score = sum([item['score'] for item in scores])
    if show_scores:
        print('{:5.3f}: {} for {}'.format(total_score, cat, fleet, ))
        show_scores(scores)
    return {"Score": total_score, "Info": scores}


if __name__ == "__main__":
    print("Load {} talents".format(len(talents_info)))
