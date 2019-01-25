import datetime

import numpy
import pandas as pd
from pandas import DataFrame

from QUANTAXIS.QAUtil import (
    DATABASE,
    QA_Setting,
    QA_util_date_stamp,
    QA_util_date_valid,
    QA_util_dict_remove_key,
    QA_util_log_info,
    QA_util_code_tolist,
    QA_util_date_str2int,
    QA_util_date_int2str,
    QA_util_sql_mongo_sort_DESCENDING,
    QA_util_time_stamp,
    QA_util_to_json_from_pandas,
    trade_date_sse
)
from QUANTAXIS.QAData.financial_mean import financial_dict

def filter_dates(start, end):
    '''
    filter dates method
    :param start, end: can be str/int of 2019, 201901, '2019-01', '2019-01-01'
    :return: string eg： '2019-01-01'
    '''
    begining_date = '1990-01-01'
    start_day = '-01'
    start_month = '-01-01'
    end_day = '-31'
    end_month = '-12-31'

    if start == 'all':
        start = begining_date
        end = str(datetime.date.today())
        return start, end

    start = str(start)
    end = start if end is None else str(end)

    if len(start) == 4:
        start += start_month
    elif len(start) == 6:
        start = start[:4] + '-' + start[-2:] + start_day
    elif len(start) == 7:
        start += start_day
    if not QA_util_date_valid(start):
        start = begining_date

    if len(end) == 4:
        end += end_month
    elif len(end) == 6:
        end = end[:4] + '-' + end[-2:] + end_day
    elif len(end) == 7:
        end += end_day

    if QA_util_date_valid(end):
        return start, end
    else:
        return None, None


def _database_query_dict(code, start, end, frequence=''):
    '''
    database query string method
    :param code: stock/future/index code list
    :param start, end: date string
    :param frequence: minute frequence, default is empty string
    :return: dict of database query depends on frequence
    '''
    if frequence:
        return {
            'code': {
                '$in': code
            },
            "time_stamp": {
                "$gte": QA_util_time_stamp(start),
                "$lte": QA_util_time_stamp(end)
            },
            'type': frequence
        }
    else:
        return {
            'code': {
                '$in': code
            },
            "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)
            }
        }


def _database_collections(data_type, code, start, end, frequence=''):
    '''
    database collection method
    :param data_type: stock_day, stock_min etc
    :param code: stock/future/index code list
    :param start, end: date string
    :param frequence: minute frequence, default is empty string
    :return: dict of database collection configuration
    '''
    query = _database_query_dict(
        code=code,
        start=start,
        end=end,
        frequence=frequence
    )
    database_d = {
        'stock_day': {
            'collection':
            DATABASE.stock_day,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'volume',
                'amount',
                'datetime'
            ]
        },
        'stock_min': {
            'collection':
            DATABASE.stock_min,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'volume',
                'amount',
                'datetime',
                'type'
            ]
        },
        'index_day': {
            'collection':
            DATABASE.index_day,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'up_count',
                'down_count',
                'volume',
                'amount',
                'datetime'
            ]
        },
        'index_min': {
            'collection':
            DATABASE.index_min,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'up_count',
                'down_count',
                'volume',
                'amount',
                'datetime',
                'time_stamp',
                'date',
                'type'
            ]
        },
        'future_day': {
            'collection':
            DATABASE.future_day,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'position',
                'price',
                'trade',
                'datetime'
            ]
        },
        'future_min': {
            'collection':
            DATABASE.future_min,
            'query':
            query,
            'columns': [
                'code',
                'open',
                'high',
                'low',
                'close',
                'position',
                'price',
                'trade',
                'datetime',
                'tradetime',
                'time_stamp',
                'date',
                'type'
            ]
        }
    }
    if data_type in database_d.keys():
        return database_d[data_type]
    else:
        return 'please provide the correct data type: {}'.format(
            ', '.join(database_d.keys())
        )


def QA_list_fetch(data_type):
    '''
    database collection method
    :param data_type: stock_day, stock_min etc
    :return: dataframe of given data_type
    '''
    list_collections = {
        'stock_list': {
            'collection': DATABASE.stock_list
        },
        'index_list': {
            'collection': DATABASE.index_list
        },
        'future_list': {
            'collection': DATABASE.future_list
        },
        'etf_list': {
            'collection': DATABASE.etf_list
        },
    }
    if data_type in list_collections.keys():
        collections = list_collections[data_type]['collection']
        res = pd.DataFrame([item for item in collections.find()]).drop(
            '_id',
            axis=1,
            inplace=False
        ).set_index(
            'code',
            drop=False
        )
        if len(res) == 0:
            print(
                "QA Error QA_data_fetch_adv call item for item in collections.find() return 0 item, maybe the DATABASE.{} is empty!"
                .format(data_type)
            )
            return None
        else:
            return res
    else:
        return None


def QA_data_fetch(
        code='',
        start='all',
        end=None,
        data_type='stock_day',
        frequence='',
        format='numpy'
):
    """'fetch data from database'
    :param code: code list of stock, index, future, etf
    :param start: date of start, can be str/int of 2019, 201901, '2019-01', '2019-01-01'
    :param end: date of end, can be str/int of 2019, 201901, '2019-01', '2019-01-01'
    :param data_type: stock_day, stock_min etc
    :param frequence: minute freq of min data like 15, 30min
    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start, end = filter_dates(start, end)
    if end is None:
        QA_util_log_info(
            'QA Error QA_fetch_stock_day data parameter start=%s end=%s is not right'
            % (start,
               end)
        )
        return None

    if frequence:
        if str(frequence).split('m')[0] in ['1', '5', '15', '30', '60']:
            frequence = str(frequence).split('m')[0] + 'min'
            start = '{} 09:30:00'.format(start)
            end = '{} 15:00:00'.format(end)
        else:
            print(
                "QA Error QA_fetch_stock_min_adv parameter frequence=%s is none of 1min 1m 5min 5m 15min 15m 30min 30m 60min 60m"
                % frequence
            )
            return None

    db_collection = _database_collections(
        data_type=data_type,
        code=code,
        start=start,
        end=end,
        frequence=frequence
    )

    # code checking
    # only fot stock currenting
    # todo: check future code
    code = QA_util_code_tolist(code)

    __data = []

    # return None if db_collection is an error message
    if isinstance(db_collection, str):
        print(db_collection)
        return None

    collections = db_collection['collection']

    try:
        cursor = collections.find(
            db_collection['query'],
            {"_id": 0},
            batch_size=10000
        )
        res = pd.DataFrame([item for item in cursor])
        if 'datetime' not in res.columns:
            try:
                res.rename({'date': 'datetime'}, axis=1, inplace=True)
            except:
                pass
        else:
            res = res.assign(type=frequence)
        if 'vol' in res.columns:
            res = res.assign(
                volume=res.vol,
                datetime=pd.to_datetime(res.datetime)
            ).query('volume>1').drop_duplicates(['datetime',
                                                 'code']).set_index(
                                                     'datetime',
                                                     drop=False
                                                 )
        else:
            res = res.assign(datetime=pd.to_datetime(res.datetime)
                            ).drop_duplicates(['datetime',
                                               'code']).set_index(
                                                   'datetime',
                                                   drop=False
                                               )
        res = round(res[db_collection['columns']], 2)
    except:
        res = None
    if format in ['P', 'p', 'pandas', 'pd']:
        return res
    elif format in ['json', 'dict']:
        return QA_util_to_json_from_pandas(res)
    # 多种数据格式
    elif format in ['n', 'N', 'numpy']:
        return numpy.asarray(res)
    elif format in ['list', 'l', 'L']:
        return numpy.asarray(res).tolist()
    else:
        print(
            "QA Error QA_fetch_stock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
            % format
        )
        return None
