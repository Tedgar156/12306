import requests
import urllib.parse
import urllib.request
from json import loads
import time
import re
from PIL import Image
from stationCode import code

#禁用安全协议
requests.packages.urllib3.disable_warnings()

#如果接收数据是这样的格式
getData1 = {'from_station':'成都','to_station':'上海','train_date':'2019-03-08','back_traib_date':'2019-03-02',}
getData2 = {'train_station':'D2208'}
getData3 = {'passengerInfo':[{'passengerName':'唐亿','IDCard':'51090219970815****','seatType':'二等座','pasType':'学生票'}]} #,{'passengerName':'周常青','IDCard':'51090219970114****','seatType':'一等座','pasType':'成人票'}]}


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.3'}

def changeTrainDate(data):
    a = time.mktime(time.strptime(data,"%Y-%m-%d"))
    return time.strftime("%a %b %d %Y 00:00:00 GMT+0800 ",time.localtime(a)) + '(中国标准时间)'
def getSeatType(type):
    seatType = {'特等座': '9', '一等座': 'M', '二等座': 'O', '高级动卧': 'A', '软卧': '4', '动卧': 'F', '硬卧': '3', '无座': '1', '硬座': '1'}
    return seatType[type]

def changeTicket(data):
    #进行转码
    pasType = {'成人票':'1','儿童票':'2','学生票':'3'}
    #存储改变后的信息
    conversion = {}
    passengerTicketStr = ''
    oldPassengerStr = ''
    #这里如果是选择多个人将信息分别添加
    for passenger in data['passengerInfo']:
        #数据拼接
        if passengerTicketStr != '':
            passengerTicketStr += '_'
        passengerTicketStr += getSeatType(passenger['seatType']) + ',0,' + pasType[passenger['pasType']] + ',' + passenger['passengerName'] + ',1,' + passenger['IDCard'] + ',,N'
        oldPassengerStr += passenger['passengerName'] + ',1,' + passenger['IDCard'] + ',' + pasType[passenger['pasType']] + '_'
    #将需要返回的值赋值
    conversion['passengerTicketStr'] = passengerTicketStr
    conversion['oldPassengerStr'] = oldPassengerStr
    return conversion

class buyTickets():
    def __init__(self):
        self.train_no = {}
        self.secretStr = {}
        self.leftTicket = {}
        self.passenger = {}
        self.train_location = {}
        self.session = requests.session()
    def login(self):
        #在登录时 需要获取验证码正确时返回的cookie，所以这里需要获取验证码
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
        #已保存cookie的方式打开页面
        response = self.session.get(url=url, headers=headers, verify=False)
        #将获取的图片保存在电脑中
        with open('img.jpg', 'wb') as f:
            f.write(response.content)
        #显示图片
        img = Image.open('img.jpg')
        img.show()
        #获取验证码的正确值  手动输入
        result = input('请输入验证码(1-8)如 1,5 ')
        #处理成提交的正确格式
        rand = []
        answer = ['40,50', '110,50', '190,50', '260,50', '40,110', '110,120', '190,120', '260,120']
        for a in result.split(','):
            rand.append(answer[int(a) - 1])
        rand = ','.join(rand)
        #验证 验证码 是否正确
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        data = {
            'answer': rand,
            'login_site': 'E',
            'rand': 'sjrand'
        }
        # 已保存cookie的方式打开页面
        response = self.session.post(url=url, data=data, headers=headers, verify=False)
        #返回的数据是Json数据，处理成字典形
        content = loads(response.content)
        #查看是否正确如果错误需要从头再来
        if int(content['result_code']) == 4:
            print('验证成功')
        else:
            #递归方式，再来一次
            print('验证失败')
            buyTickets.login(self)
            return
        #输入账号和密码登录，如果不想每次都输入我们就在 account 事先将所需要的账户名和密码填入
        name = input('请输入账号')
        password = input('请输入密码')
        #用户名、密码登录
        url = 'https://kyfw.12306.cn/passport/web/login'
        data = {
            'username': name,
            'password': password,
            'appid': 'otn'
        }
        #将用户名 密码 一同提交登录
        response = self.session.post(url=url,data=data,headers=headers,verify=False)
        content = loads(response.content)
        if int(content['result_code']) == 0:
            # 如果账号没有问题了
            print(content['result_message'])
            # 我们不要被 12306 骗了，这里他说已经登录成功了。如果我们访问个人中心会发现根本就访问不了，其实还没有登录成功

            # 获取一系列的cookie值才能真正的登录成功
            url = 'https://kyfw.12306.cn/otn/login/userLogin'
            response = self.session.get(url, headers=headers)
            url = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
            response = self.session.get(url, headers=headers)
            url = 'https://kyfw.12306.cn/otn/resources/merged/12306_index/iconfont.ttf?t=1532688360724'
            response = self.session.get(url, headers=headers)
            # 获取 tk 下一个请求需要提交 tk 值，这也是一种反爬的手段
            url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
            data = {'appid': 'otn'}
            response = self.session.post(url=url, data=data, headers=headers, verify=False)
            content = loads(response.content)
            tk = content['newapptk']
            url = 'https://kyfw.12306.cn/otn/uamauthclient'
            data = {'tk': tk}
            response = self.session.post(url=url, data=data, headers=headers, verify=False)
            url = 'https://kyfw.12306.cn/otn/login/conf'
            response = self.session.post(url=url, data=None, headers=headers, verify=False)
            url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
            response = self.session.post(url=url, data=None, headers=headers, verify=False)
            url = 'https://kyfw.12306.cn/passport/web/auth/uamtk-static'
            data = {
                'appid': 'otn'
            }
            response = self.session.post(url=url, data=data, headers=headers, verify=False)
            content = loads(response.content)
            if int(content['result_code']) == 0:
                print(content['result_message'])
                # 这里返回值为 验证成功 了就可以访问个人中心了，意味着真正的登陆成功了
            else:
                print('登录错误')
        else:
            #需要重新输入用户名和密码，账号错误
            print('用户名或密码错误,请修改 account.py 中的用户名或密码再次运行')
            exit(1)
    def query(self):
        # #获取站台的前的代号
        # url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9094'
        # response = self.session.get(url=url, headers=headers)
        # #以字典方式来存储站台
        # content = response.text.split('@')
        # for info in content[1:]:
        #     context = info.split('|')
        #     self.code[context[1]] = context[2]
        # 获取出发时间，出发站台，到达站台。为了方便也可以将所需要的信息卸载前面的 getData1 中。
        getData1['train_date'] = input('请输入出发时间[2019-03-01]')
        # 查询出发时间格式为 2019-3-10
        getData1['from_station'] = input('请输入出发站台')
        getData1['to_station'] = input('请输入到达站台')
        print(getData1['train_date'])
        #查询列车信息。因为是 get 请求，所以我们将请求的 data 格式化加入到 url 中。
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryX?'
        #将出发时间 出发站台 到达站台 数据发送查找火车票
        data = {'leftTicketDTO.train_date': getData1['train_date'],#出发时间
                'leftTicketDTO.from_station': code[getData1['from_station']],#获取出发站台的代码
                'leftTicketDTO.to_station': code[getData1['to_station']],#获取到达站台的代码
                'purpose_codes': 'ADULT'}#purpose_codes  ADULT -- 普通  0X00 -- 学生
        #将 data 格式化
        data = urllib.parse.urlencode(data)
        #数据拼接
        url = url + data
        response = self.session.get(url=url, headers= headers)
        #将请求到的列车信息为 Json 格式，所以解析返回的信息
        content = loads(response.content)
        if content['data']['result'] == '':
            print('未查找到该车次')
            return
        #将信息打印出来
        print('|车次|出发时间|到达时间|历时|出发日|特等座|一等座|二等座|高级动卧|软卧|动卧|硬卧|硬座|无座|')
        for str in content['data']['result']:
            str = str.split('|预订|')
            string = str[1].split('|')
            #获取列车的型号
            c = string[33]
            #将后面需要使用的 secretStr 存储起来。按照 车次:secretStr 字典形式存储
            self.secretStr[string[1]] = str[0]
            # 将后面需要使用的 train_no 存储起来。按照 车次:train_no 字典形式存储
            self.train_no[string[1]] = string[0]
            # 将后面需要使用的 leftTicket 存储起来。按照 车次:leftTicket 字典形式存储
            self.leftTicket[string[1]] = string[10]
            # 将后面需要使用的 train_location 存储起来。按照 车次:train_location 字典形式存储
            self.train_location[string[1]] = string[13]
            # K  T  Z  列车信息
            if  c == '1413':
                #print('|软卧|硬卧|硬座|无座|')
                print('|%s| %s  | %s |%s|%s|     |     |      |        | %s |    | %s | %s | %s |'%(string[1],string[6],string[7],string[8],string[11],string[21],string[26],string[27],string[24]))
            # D  列车信息
            elif c == 'OMO' or c == 'OOM':
                #print('|一等座|二等座|无座|')
                print('|%s| %s  | %s |%s|%s|    |  %s |  %s  |        |    |    |    |    | %s |'%(string[1],string[6],string[7],string[8],string[11],string[29],string[28],string[24]))
            # D  特殊列车信息
            elif c == 'OFAO':
                #print('高级动卧|动卧|二等座|无座|)
                print('|%s| %s  | %s |%s|%s|    |     |  %s  |   %s    |    | %s |    |    | %s |'%(string[1],string[6],string[7],string[8],string[11],string[28],string[19],string[31],string[24]))
            # G 列车信息
            elif c == 'OM9':
                #print('|特等座|一等座|二等座|')
                print('|%s| %s  | %s |%s|%s| %s |  %s | %s  |        |    |     |    |   |    |'%(string[1],string[6],string[7],string[8],string[11],string[30],string[29],string[28]))
        # getData2['train_station'] 为需购买的列车号，如不想麻烦可以注释掉只需要在前面的 getData3 修改即可
        getData2['train_station'] = input('请输入需要购买的列车号')

        #  # 查看列车经过的站台
        # url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?'
        # data = {
        #     'train_no': self.train_no[string[1]],#拿到在刚刚查询列车时拿到的列车号
        #     'from_station_telecode': string[2],#事发地代号
        #     'to_station_telecode': string[3],#到达地代号
        #     'depart_date': string[11][:4] + "-" + string[11][4:6] + "-" + string[11][6:8]#出发时间
        # }
        # # 将data转码
        # data = urllib.parse.urlencode(data)
        # # 拼接 url
        # url = url + data
        # response = self.session.get(url=url, headers=headers)
        # content = loads(response.content)
        # context = content['data']['data']
        # print('|站序| 站名 |到站时间|出发时间|停留时间|')
        # for info in context:
        #     print('| %s |%s| %s | %s |%s|'%(info['station_no'], info['station_name'], info['arrive_time'], info['start_time'],info['stopover_time']))
    def buy(self):
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        data = {
            '_json_att': ''
        }
        response = self.session.post(url=url, data=data,headers=headers,verify=False)
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr': urllib.parse.unquote(self.secretStr[getData2['train_station']]),#注意这里需要转码不然第二次请求会失败
            'train_date':getData1['train_date'],
            'back_train_date': getData1['back_traib_date'],
            'tour_flag': 'dc',#特殊动车为  'wc'
            'purpose_codes': 'ADULT',
            'query_from_station_name': getData1['from_station'],
            'query_to_station_name': getData1['to_station'],
            'undefined': ''
        }
        response = self.session.post(url=url, data=data,headers=headers,verify=False)
        #获取后面需要 globalRepeatSubmitToken，key_check_isChange 请求的参数
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {
            '_json_att':''
        }
        response = self.session.post(url=url, data=data, headers=headers,verify=False)
        r = r"globalRepeatSubmitToken = '(.*?)';"
        compile = re.compile(r)
        self.repeat_Token = re.findall(compile,str(response.text))[0]
        r = r"'key_check_isChange':'(.*?)'"
        compile = re.compile(r)
        self.key_check_isChange = re.findall(compile,str(response.text))[0]
        # 获取可以购买的火车票常用联系人
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_Token  # 刚才获取的 repeat_Token
        }
        response = self.session.post(url=url, data=data, headers=headers, verify=False)
        content = loads(response.content)
        for passenger in content['data']['normal_passengers']:
            self.passenger[passenger['passenger_name']] = passenger['passenger_id_no']
            print(passenger['passenger_name'])
            print(passenger['passenger_id_no'])
            print(passenger['mobile_no'])
            print(passenger['email'])
        #获取购买车票的信息 也可以购买多张车票。如果嫌麻烦可以直接在 getData3 中写死
        name = input('请输入需要购买车票的名字')
        seatType = input('请输入购买火车票的座次')
        pasType = input('请输入购买车票的类型')
        getData3['passengerInfo'][0]['passengerName'] = name
        getData3['passengerInfo'][0]['IDCard'] = self.passenger[name]
        getData3['passengerInfo'][0]['seatType'] = seatType
        getData3['passengerInfo'][0]['pasType'] = pasType
        #将需要购买的车票信息转化格式
        ticketStr = changeTicket(getData3)
        # 提交订单第一步
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': ticketStr['passengerTicketStr'],  # 转化格式后的数据
            'oldPassengerStr': ticketStr['oldPassengerStr'],  # 转化格式后的数据
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_Token  # 第一步获取的 repeat_Token
        }
        response = self.session.post(url=url, data=data, headers=headers, verify=False)
        # 提交订单第二步
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data = {
            'train_date': changeTrainDate(getData1['train_date']),  # 转变出发时间格式
            'train_no': self.train_no[getData2['train_station']],  # 列车的 no
            'stationTrainCode': getData2['train_station'],  # 需要购买的车票车次
            'seatType': getSeatType(getData3['passengerInfo'][0]['seatType']),  # 座次代号
            'fromStationTelecode': code[getData1['from_station']],  # 发出地代号
            'toStationTelecode': code[getData1['to_station']],  # 到达地代号
            'leftTicket': self.leftTicket[getData2['train_station']],
            'purpose_codes': '00',
            'train_location': self.train_location[getData2['train_station']],
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_Token  # 第一步获取的 repeat_Token
        }
        response = self.session.post(url=url, data=data, headers=headers, verify=False)
        # 提交订单第三步
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            'passengerTicketStr': ticketStr['passengerTicketStr'],
            'oldPassengerStr': ticketStr['oldPassengerStr'],
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': self.key_check_isChange,  ## 第一步获取的 key_check_isChange
            'leftTicketStr': self.leftTicket[getData2['train_station']],
            'train_location': self.train_location[getData2['train_station']],
            'choose_seats': '',
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self.repeat_Token  # 第一步获取的 repeat_Token
        }
        response = self.session.post(url=url, data=data, headers=headers, verify=False)
        print('confirmSingleForQueue', response.text)


if __name__ == '__main__':
    land = buyTickets()
    land.login()
    land.query()
    land.buy()