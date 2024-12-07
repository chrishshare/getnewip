import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import MySQLdb
import MySQLdb.cursors

# db config
HOST = '127.0.0.1'
PORT = 3306
USER = 'root'
PASSWORD = '@*'
DB = 'chkip'
QUERY_SQL = 'SELECT ip, address, operator FROM chkip.iphistory order by createtime desc limit 1'


# def get_trackip_ip():
#     """
#     从trackip获取ip信息
#     :return:
#     """
#     trackip_url = 'http://www.trackip.net/ip?json'
#     content = requests.get(trackip_url).content
#     content_string = bytes.decode(content, encoding='utf-8')
#     dict_ip = eval(content_string)
#     return dict_ip
#
#
# def get_ip138_ipinfo_byip(real_ip):
#     """
#     从ip138网站根据查询到的ip地址，查询对应的地址信息
#     :param real_ip:
#     :return:
#     """
#     token = 'a8771d33dc95284707528d75df8eff45'
#     api_url = 'http://api.ip138.com/query/'
#     c_api = requests.get(api_url, params={'ip': real_ip, 'token': token})
#     c_api = c_api.json()
#     return c_api


def get_ip138_ip_info():
    """
    从ip138获取当前ip地址信息
    :return:
    """
    token = 'a8771d33dc95284707528d75df8eff45'
    api_url = 'http://api.ip138.com/query/'
    c_api = requests.get(api_url, params={'token': token})
    c_api = c_api.json()
    return c_api


def update_ip_to_mysql():
    """
    将ip地址变更插入数据库，如果当前ip较上一次ip没有变更，不更新数据，如果有变更则在数据库中插入一条行新数据，并发送邮件
    :return:
    """
    ip_info = get_ip138_ip_info()
    current_ip = ip_info.get('ip')
    try:
        db_last_ip = execute_mysql_query(QUERY_SQL)[0].get('ip')
    except:
        db_last_ip = None
    if db_last_ip != current_ip:
        data_list = [ip_info.get('data')[0], ip_info.get('data')[1], ip_info.get('data')[2]]
        address = ''.join(data_list)
        operator =ip_info.get('data')[3]
        insert_sql = 'INSERT INTO iphistory (ip, address, operator) VALUES (%s, %s, %s)'
        params = [current_ip, address, operator]
        execute_mysql_insert(sql=insert_sql, params=params)
        send_email_after_ip_changed(current_ip)


def send_email_after_ip_changed(ip):
    """
    ip地址变更时，给收件人发送邮件通知
    :return:
    """
    smtp_server = 'smtp.163.com'
    from_mail = 'siyzhou@163.com'
    mail_pass = '#zhsy08241128!'
    to_mail = ['siyzhou@163.com', ]
    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['To'] = ','.join(to_mail)
    msg['Subject'] = Header(u'IP地址变更通知', 'utf-8').encode()
    body = '<h1 style="color:blue">IP地址已变更为：' + ip + """</h1>"""
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server, "25")
        s.login(from_mail, mail_pass)
        print(msg)
        s.sendmail(from_mail, to_mail, msg.as_string())
        s.quit()
    except smtplib.SMTPException as e:
        print("Error: %s" % e)


def execute_mysql_query(sql):
    conn = MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB, charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def execute_mysql_insert(sql, params):
    conn = MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB, charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute(sql, params)
    cur.close()
    conn.commit()
    conn.close()
    return None


if __name__ == '__main__':
    ip = get_ip138_ip_info()
    # send_email_after_ip_changed('183.48.31.160')
    update_ip_to_mysql()
    print(ip)

