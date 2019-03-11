# 12306
用 python 购买 12306 火车票
practice文件夹里面有
      account.py 保存登录时用户信息
      auto12306.py 将需要登录的用户写在 account.py 里面，在前面有需要购买的火车票列车车次，购票用户
      manual12306.py 手动输入登录时的验证码，手动输入登录 用户名，密码 ，手动输入 列车车次，购票用户 。 手动输入最大的问题在于输入时格式问题，所以建议就在前面的 getData 写死，就会避免格式问题
      stationCode.py 站台的代号
      YDMHTTPDemo3.py 登录时验证码自动识别接入 yundama.com 平台
