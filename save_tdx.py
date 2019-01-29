import concurrent
import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json
import pandas as pd
import pymongo

from QUANTAXIS.QAFetch.QATdx import (
    QA_fetch_get_option_day,
    QA_fetch_get_option_min,
    QA_fetch_get_index_day,
    QA_fetch_get_index_min,
    QA_fetch_get_stock_day,
    QA_fetch_get_stock_info,
    QA_fetch_get_stock_list,
    QA_fetch_get_future_list,
    QA_fetch_get_index_list,
    QA_fetch_get_future_day,
    QA_fetch_get_future_min,
    QA_fetch_get_stock_min,
    QA_fetch_get_stock_transaction,
    QA_fetch_get_stock_xdxr,
    select_best_ip
)

# from QUANTAXIS.QAFetch import QA_fetch_get_stock_block
# from QUANTAXIS.QAFetch.QATdx import (
#     QA_fetch_get_50etf_option_contract_time_to_market,
#     QA_fetch_get_commodity_option_CU_contract_time_to_market,
#     QA_fetch_get_commodity_option_SR_contract_time_to_market,
#     QA_fetch_get_commodity_option_M_contract_time_to_market,
#     QA_fetch_get_50etf_option_contract_time_to_market,
# )
from QUANTAXIS.QAUtil import (
    DATABASE,
    QA_util_get_next_day,
    QA_util_get_real_date,
    QA_util_log_info,
    QA_util_to_json_from_pandas,
    trade_date_sse
)

def now_time():
    return str(QA_util_get_real_date(str(datetime.date.today() - datetime.timedelta(days=1)), trade_date_sse, -1)) + \
        ' 17:00:00' if datetime.datetime.now().hour < 15 else str(QA_util_get_real_date(
            str(datetime.date.today()), trade_date_sse, -1)) + ' 15:00:00'

# dict of database collection configuration
def _type_config(client, type_):

    type_list_d = {
        'stock_day': {
            'collection': client.stock_day,
            'job_id': 'JOB01',
            'fetch': QA_fetch_get_stock_day
        },
        'stock_week': {
            'collection': client.stock_week,
            'job_id': 'JOB01',
            'fetch': QA_fetch_get_stock_day
        },
        'stock_month': {
            'collection': client.stock_month,
            'job_id': 'JOB01',
            'fetch': QA_fetch_get_stock_day
        },
        'stock_year': {
            'collection': client.stock_year,
            'job_id': 'JOB01',
            'fetch': QA_fetch_get_stock_day
        },
        'stock_min': {
            'collection': client.stock_min,
            'job_id': 'JOB03',
            'fetch': QA_fetch_get_stock_min
        },
        'index_day': {
            'collection': client.index_day,
            'job_id': 'JOB04',
            'fetch': QA_fetch_get_index_day
        },
        'index_min': {
            'collection': client.index_min,
            'job_id': 'JOB05',
            'fetch': QA_fetch_get_index_min
        },
        'etf_day': {
            'collection': client.index_day,
            'job_id': 'JOB06',
            'fetch': QA_fetch_get_index_day
        },
        'etf_min': {
            'collection': client.index_min,
            'job_id': 'JOB07',
            'fetch': QA_fetch_get_index_min
        },
        'future_day': {
            'collection': client.future_day,
            'job_id': 'JOB12',
            'fetch': QA_fetch_get_future_day
        },
        'future_day_all': {
            'collection': client.future_day,
            'job_id': 'JOB12',
            'fetch': QA_fetch_get_future_day
        },
        'future_min': {
            'collection': client.future_min,
            'job_id': 'JOB13',
            'fetch': QA_fetch_get_future_min
        },
        'future_min_all': {
            'collection': client.future_min,
            'job_id': 'JOB13',
            'fetch': QA_fetch_get_future_min
        },
        'stock_list': {
            'collection': client.stock_list,
            'job_id': 'JOB08'
        },
        'index_list': {
            'collection': client.index_list,
            'job_id': 'JOB08'
        },
        'future_list': {
            'collection': client.future_list,
            'job_id': 'JOB08'
        },
        'etf_list': {
            'collection': client.etf_list,
            'job_id': 'JOB08'
        },
    }
    return type_list_d[type_]

# dict of database query string
db_index_d = {
    'short_freq': [('code', pymongo.ASCENDING), ('time_stamp', pymongo.ASCENDING), ('date_stamp', pymongo.ASCENDING)],
    'long_freq': [("code", pymongo.ASCENDING), ("date_stamp", pymongo.ASCENDING)]
}

# list of freq, not used yet
frequence_list = ['day', 'day_all', 'min', 'min_all', 'week', 'month', 'year']

beginning_date = '1990-01-01'


def get_list(type_=''):
    """
    return data list or dataframe depends on given type_
    """
    type_list = ['stock', 'index', 'etf', 'future']
    '''todo: option list'''

    type_ = type_.split('_')
    frequence = type_[1]

    if type_[0] in type_list:
        if type_[0] == 'future':
            lst = QA_fetch_get_future_list()
            lst = lst if frequence == 'list' else lst.code.unique().tolist()
            if 'all' not in type_ and frequence != 'list':
                lst = [item for item in lst if str(item)[-2:] in ['L8', 'L9']]
        else:
            lst = QA_fetch_get_stock_list(type_=type_[0])
            lst = lst if frequence == 'list' else lst.code.unique().tolist()
        if len(lst) > 0:
            return lst, frequence
        else:
            return None, None

    return None, None


def QA_SU_save_list(
        client=DATABASE,
        ui_log=None,
        ui_progress=None,
        type_='stock_list'
):
    """save list to data depends on given type_,

    Keyword Arguments:
        client {[type]} -- [description] (default: {DATABASE})
    """
    standard_list = ['stock_list', 'index_list', 'future_list', 'etf_list']
    type_ = str(type_)
    if type_ in standard_list:
        config = _type_config(client=client, type_=type_)
        coll = config['collection']
        job_id = config['job_id']
        try:
            QA_util_log_info(
                '##{} Now Saving {} ===='.format(job_id,
                                                 type_),
                ui_log=ui_log,
                ui_progress=ui_progress,
                ui_progress_int_value=5000
            )
            lst, _ = get_list(type_=type_)
            if lst is not None:
                client.drop_collection(type_)

                coll.create_index('code', unique=True)

                coll.insert_many(QA_util_to_json_from_pandas(lst))
                QA_util_log_info(
                    "完成{}获取".format(type_),
                    ui_log=ui_log,
                    ui_progress=ui_progress,
                    ui_progress_int_value=10000
                )
            else:
                print(" Error save_tdx.QA_SU_save_{} exception!".format(type_))
        except Exception as e:
            QA_util_log_info(e, ui_log=ui_log)
            print(" Error save_tdx.QA_SU_save_stock_list exception!")

    pass


def QA_SU_save_short_freq(
        client=DATABASE,
        ui_log=None,
        ui_progress=None,
        type_='stock_min',
        min_list=[]
):
    """save short freq data depends given min_list

    Keyword Arguments:
        client {[type]} -- [description] (default: {DATABASE})
    """
    standard_list = ['1min', '5min', '15min', '30min', '60min']

    type_ = str(type_)
    # make sure type_ is correct, if min_list is empty, add '1min' to to it
    # if type_ in type_list_d.keys():
    lst, frequence = get_list(type_)
    if frequence == 'min':
        db_index = db_index_d['short_freq']
        min_list = min_list if len(min_list) else ['1min']
    else:
        db_index = db_index_d['long_freq']
    # else:
    #     QA_util_log_info('ERROR CODE \n ', ui_log)
    #     return None
    if lst is None:
        QA_util_log_info('ERROR CODE \n ', ui_log)
        return None

    config = _type_config(client=client, type_=type_)
    coll = config['collection']
    job_id = config['job_id']
    coll.create_index(db_index)
    err = []

    def __saving_work(code, coll):
        QA_util_log_info(
            logs='##{} Now Saving {}==== {}'.format(job_id,
                                                    type_,
                                                    str(code)),
            ui_log=ui_log
        )
        try:
            for type in min_list:
                if type in standard_list:
                    ref_ = coll.find({'code': str(code)[0:6], 'type': type})
                    end_time = str(now_time())[0:19]
                    if ref_.count() > 0:
                        start_time = ref_[ref_.count() - 1]['datetime']
                        keep_row = 1
                    else:
                        start_time = beginning_date
                        keep_row = 0

                    QA_util_log_info(
                        logs='##{}.{} Now Saving {} from {} to {} =={} '.format(
                            job_id,
                            min_list.index(type),
                            str(code),
                            start_time,
                            end_time,
                            type
                        ),
                        ui_log=ui_log
                    )
                    if start_time != end_time:
                        __data = config['fetch'](
                            str(code),
                            start_time,
                            end_time,
                            type
                        )
                        if len(__data) > 1:
                            coll.insert_many(
                                QA_util_to_json_from_pandas(__data)[keep_row::]
                            )

        except Exception as e:
            QA_util_log_info(e, ui_log=ui_log)
            err.append(code)
            QA_util_log_info(err, ui_log=ui_log)

    executor = ThreadPoolExecutor(max_workers=4)
    #executor.map((__saving_work,  stock_list[i_], coll),URLS)
    res = {
        executor.submit(__saving_work,
                        lst[i_],
                        coll)
        for i_ in range(len(lst))
    }
    count = 0
    for i_ in concurrent.futures.as_completed(res):
        QA_util_log_info(
            'The {} of Total {}'.format(count,
                                        len(lst)),
            ui_log=ui_log
        )

        strProgress = 'DOWNLOAD PROGRESS {} '.format(
            str(float(count / len(lst) * 100))[0:4] + '%'
        )
        intProgress = int(count / len(lst) * 10000.0)
        QA_util_log_info(
            strProgress,
            ui_log,
            ui_progress=ui_progress,
            ui_progress_int_value=intProgress
        )
        count = count + 1
    if len(err) < 1:
        QA_util_log_info('SUCCESS', ui_log=ui_log)
    else:
        QA_util_log_info(' ERROR CODE \n ', ui_log=ui_log)
        QA_util_log_info(err, ui_log=ui_log)


def QA_SU_save_long_freq(
        client=DATABASE,
        ui_log=None,
        ui_progress=None,
        type_='stock_day'
):                        #, min_list=[]):
    '''
     save long freq data
    保存日线数据
    :param client:
    :param ui_log:  给GUI qt 界面使用
    :param ui_progress: 给GUI qt 界面使用
    :param ui_progress_int_value: 给GUI qt 界面使用
    '''
    type_ = str(type_)
                          # make sure type_ is correct, if min_list is empty, add '1min' to to it
    # if type_ in type_list_d.keys():
    lst, frequence = get_list(type_)

    if lst is None:
        QA_util_log_info('ERROR CODE \n ', ui_log)
        return None

    if 'min' in frequence:
        db_index = db_index_d['short_freq']
        min_list = min_list if len(min_list) else ['1min']
    else:
        db_index = db_index_d['long_freq']
    # else:
    #     QA_util_log_info('ERROR CODE \n ', ui_log)
    #     return None

    config = _type_config(client=client, type_=type_)
    coll = config['collection']
    job_id = config['job_id']

    coll.create_index(db_index)
    err = []

    def __saving_work(code, coll):
        try:
            QA_util_log_info(
                logs='##{} Now Saving {}==== {}'.format(
                    job_id,
                    type_,
                    str(code)
                ),
                ui_log=ui_log
            )

            # 首选查找数据库 是否 有 这个代码的数据
            ref = coll.find({'code': str(code)[0:6]})
            end_date = str(now_time())[0:10]

            # 当前数据库已经包含了这个代码的数据， 继续增量更新
            # 加入这个判断的原因是因为如果股票是刚上市的 数据库会没有数据 所以会有负索引问题出现
            if ref.count() > 0:
                # 接着上次获取的日期继续更新
                start_date = ref[ref.count() - 1]['date']
            else:
                # 当前数据库中没有这个代码的股票数据， 从1990-01-01 开始下载所有的数据
                start_date = beginning_date
            QA_util_log_info(
                logs='UPDATE_{} \n Trying updating {} from {} to {}'.format(
                    type_,
                    code,
                    start_date,
                    end_date
                ),
                ui_log=ui_log
            )
            if start_date != end_date:
                start_date = QA_util_get_next_day(
                    start_date
                ) if start_date != beginning_date else beginning_date
                coll.insert_many(
                    QA_util_to_json_from_pandas(
                        config['fetch'](
                            code=str(code),
                            start_date=start_date,
                            end_date=end_date,
                            frequence=frequence
                        )
                    )
                )
        except Exception as error0:
            print(error0)
            err.append(str(code))

    for item in range(len(lst)):
        QA_util_log_info('The {} of Total {}'.format(item, len(lst)))

        strProgressToLog = 'DOWNLOAD PROGRESS {} {}'.format(
            str(float(item / len(lst) * 100))[0:4] + '%',
            ui_log
        )
        intProgressToLog = int(float(item / len(lst) * 100))
        QA_util_log_info(
            strProgressToLog,
            ui_log=ui_log,
            ui_progress=ui_progress,
            ui_progress_int_value=intProgressToLog
        )

        __saving_work(lst[item], coll)

    if len(err) < 1:
        QA_util_log_info(
            'SUCCESS save {} ^_^'.format(' '.join(type_.split('_'))),
            ui_log=ui_log
        )
    else:
        QA_util_log_info('ERROR CODE \n ', ui_log)
        QA_util_log_info(err, ui_log)
