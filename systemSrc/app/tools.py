from django.db import connection


def query_all_dict(sql, params=None):
    '''
    查询所有结果返回字典类型数据
    :param sql:
    :param params:
    :return:
    '''
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params=params)
        else:
            cursor.execute(sql)
        col_names = [desc[0] for desc in cursor.description]
        row = cursor.fetchall()
        rowList = []
        for list in row:
            tMap = dict(zip(col_names, list))
            rowList.append(tMap)
        return rowList

def query_one_dict(sql, params=None):
    """
    查询一个结果返回字典类型数据
    :param sql:
    :param params:
    :return:
    """
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params=params)
        else:
            cursor.execute(sql)
        col_names = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        tMap = dict(zip(col_names, row))
        return tMap