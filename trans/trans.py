from bdt import bd_trans


def _parse_zh(datas):
    '''
    解析zh_CN文件
    :param data:
    :return:
    '''
    pass


def _parse_ot(datas):
    '''
    解析非zh_CN文件
    :param data:
    :return:
    '''
    pass


def _parse(datas):
    '''
    解析zh_CN文件及一个其他语种lang文件
    :return:
    '''
    ot_lang = ""
    for lang in datas:
        if lang != 'zh_CN':
            ot_lang = lang
    ot_data = datas[ot_lang]
    zh_data = datas['zh_CN']

    tr_data = bd_trans(ot_data, ot_lang)

    res = []
    bd_res = []
    ot_res = []
    for key in zh_data:
        if key in ot_data:
            res.append({
                'key': key,
                'ot': ot_data[key],
                'ck': tr_data[ot_data[key]],
                'zh': zh_data[key]
            })
        else:
            bd_res.append({
                'key': key,
                'zh': zh_data[key]
            })
    for key in ot_data:
        if key not in zh_data:
            ot_res.append({
                'key': key,
                'ot': ot_data[key],
                'ck': tr_data[ot_data[key]],
            })

    return res


# {key: '1', us: '333', ck: '555', zh: 'fef'},




def _load(datas):
    '''
    从文本中提取键值对
    :param datas:
    :return:
    '''
    res = {}
    for lang in datas:
        res[lang] = {}
        lines = datas[lang].replace('\r', '').split('\n')
        for line in lines:
            if line.startswith('#'):
                continue
            elif line == "":
                continue
            else:
                ir = line.find('=')
                if line[ir + 1:].strip():
                    res[lang][line[:ir].strip().lower()] = line[ir + 1:].strip()
        if '' in res[lang]:
            del res[lang]['']

    return res


def parse(datas):
    '''
    :param datas:
    :return:
    '''
    data = _load(datas)
    if len(datas) == 1:
        if 'zh_CN' in datas:
            return _parse_zh(data)
        else:
            return _parse_ot(data)
    elif len(datas) == 2:
        if 'zh_CN' in datas:
            return _parse(data)

    return False


if __name__ == "__main__":
    print(bd_trans('watch\napple\nmaybe'))
