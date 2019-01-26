import save_tdx as custom
from QUANTAXIS.QASU import save_tdx as stdx
from QUANTAXIS.QASU import save_tdx_file as tdx_file
from QUANTAXIS.QASU import save_tushare as sts
from QUANTAXIS.QASU import save_financialfiles
from QUANTAXIS.QAUtil import DATABASE

def QA_SU_save_list(engine, type_='', client=DATABASE):
    """save data list like stock, index, etf, future

    Arguments:
        engine {[type]} -- [description]

    Keyword Arguments:
        client {[type]} -- [description] (default: {DATABASE})
    """

    engine = select_save_engine(engine)
    engine.QA_SU_save_list(type_=type_, client=client)


def QA_SU_save_short_freq(engine, type_='', min_list=[], client=DATABASE):
    """save short freq of data: given list of minute freq

    Arguments:
        engine {[type]} -- [description]

    Keyword Arguments:
        client {[type]} -- [description] (default: {DATABASE})
    """

    engine = select_save_engine(engine)
    engine.QA_SU_save_short_freq(type_=type_, min_list=min_list, client=client)


def QA_SU_save_long_freq(engine, type_='', client=DATABASE):
    """save long freq of data: like day, week etc

    Arguments:
        engine {[type]} -- [description]

    Keyword Arguments:
        client {[type]} -- [description] (default: {DATABASE})
    """

    engine = select_save_engine(engine)
    engine.QA_SU_save_long_freq(type_=type_, client=client)



def select_save_engine(engine):
    '''
    select save_engine , tushare ts Tushare 使用 Tushare 免费数据接口， tdx 使用通达信数据接口
    :param engine: 字符串Str
    :return: sts means save_tushare_py  or stdx means save_tdx_py
    '''
    if engine in ['tushare', 'ts', 'Tushare']:
        return sts
    elif engine in ['tdx']:
        return stdx
    elif engine in ['custom']:
        return custom
    else:
        print('QA Error QASU.main.py call select_save_engine with parameter %s is None of  thshare, ts, Thshare, or tdx', engine)
