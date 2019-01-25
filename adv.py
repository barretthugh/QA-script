from QUANTAXIS.QAData import (
    QA_DataStruct_Index_day,
    QA_DataStruct_Index_min,
    QA_DataStruct_Future_day,
    QA_DataStruct_Future_min,
    QA_DataStruct_Stock_block,
    QA_DataStruct_Financial,
    QA_DataStruct_Stock_day,
    QA_DataStruct_Stock_min,
    QA_DataStruct_Stock_transaction
)

DataStruct_d = {
    'stock_day': QA_DataStruct_Stock_day,
    'stock_min': QA_DataStruct_Stock_min,
    'index_day': QA_DataStruct_Index_day,
    'index_min': QA_DataStruct_Index_min,
    'future_day': QA_DataStruct_Future_day,
    'future_min': QA_DataStruct_Future_min
}


def QA_data_fetch_adv(
        code='',
        start='all',
        end=None,
        data_type='stock_day',
        frequence='',
        if_drop_index=True
):
    """'fetch data from database'
    :param code: code list of stock, index, future, etf
    :param start: date of start, can be str/int of 2019, 201901, '2019-01', '2019-01-01'
    :param end: date of end, can be str/int of 2019, 201901, '2019-01', '2019-01-01'
    :param data_type: stock_day, stock_min etc
    :param frequence: minute freq of min data, can be standard min value of 15, 30min, or uncommon like 9, 17min
    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only
    """

    data_type = data_type.lower()

    if data_type in ['stock_list', 'index_list', 'future_list', 'etf_list']:
        return QA_list_fetch(data_type)

    # resample to given frequence
    resample = False
    if frequence:
        if str(frequence).split('m')[0] in ['1', '5', '15', '30', '60']:
            frequence = str(frequence).split('m')[0] + 'min'
        else:
            resample = str(frequence).split('m')[0] + 'min'
            frequence = '1min'

    res = QA_data_fetch(
        code=code,
        start=start,
        end=end,
        data_type=data_type,
        frequence=frequence,
        format='pd'
    )
    if res is None:
        # 🛠 todo 报告是代码不合法，还是日期不合法
        print(
            "QA Error QA_data_fetch_adv parameter code=%s , start=%s, end=%s call QA_data_fetch return None"
            % (code,
               start,
               end)
        )
        return None
    else:
        res_reset_index = res.set_index(
            ['datetime',
             'code'],
            drop=if_drop_index
        )
        if resample:
            ds = DataStruct_d[data_type](res_reset_index)
            ds = ds.resample(resample)
            return DataStruct_d[data_type](ds.assign(type=resample))

        return DataStruct_d[data_type](res_reset_index)
