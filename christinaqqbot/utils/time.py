import datetime,requests

def get_beijing_time():
    try:
        intime = str(requests.get("http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp").text)
        one = intime[:intime.rfind('"')]
        times = datetime.datetime.fromtimestamp(int(one[one.rfind('"')+1:-3]))
    except Exception:
        raise Exception('获取北京时间错误！')
    finally:
        return times