from pylab import *
import os
import time
import pymysql
from socket import *
import datetime

image_file = 'Figure_2.png'

from select import *


# y = Ax^2 + Bx + C
x_time = [7,8,9,10,11,12,13,14,15,16,17,18] # time

kaist_avr = [7.485666667,17.33933333,29.71733333,
     37.776,42.34766667,45.51433333,
     45.58137931,40.766875,32.52344828,
     24.19172414,12.51689655,3.265862069] # kaist 1달 데이터의 시간별 평균값

kaist_day_val = [2.27,4.96,9.02,
      11.91,14.95,18.32,
      25.62,15.46,17.86,
      19.16,6.63,0.45] # kaist 데이터 중 임의의 1일 값


HOST = ''
PORT = 3001
BUF_SIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(ADDR)

print('listen')
serverSocket.listen(100)

clientSocket, addr_info = serverSocket.accept()

# 독립변수 배열 x의 각 인덱스의 총 합
S_xi = 0
for row in x_time:
    S_xi += row
#print(S_xi)

# 종속변수 배열 y의 각 인덱스의 총 합
S_yi = 0
for row in kaist_avr:
    S_yi += row
#print(S_yi)

# 독립변수 배열 x의 각 인덱스의 제곱의 총 합
S_xi2 = 0
for row in x_time:
   S_xi2+=pow(row,2)
#print(S_xi2)

# 종속변수 배열 y의 각 인덱스의 제곱의 총 합
S_yi2 = 0
for row in kaist_avr:
    S_yi2 += pow(row,2)
#print(S_yi2)

# 독립변수 배열 x와 종속변수 배열 y의 각각의 인덱스의 곱의 합
S_xiyi = 0
for row in range(len(x_time)):
    S_xiyi += x_time[row] * kaist_avr[row]
#print(S_xiyi)

# 독립변수 배열 x의 각 인덱스의 세제곱의 합
S_xi3 = 0
for row in x_time:
    S_xi3+= pow(row,3)
#print(S_xi3)

# 독립변수 배열 x의 각 인덱스의 제곱과, 종속변수 배열 y의 각 인덱스 간의 곱의 합
S_xi2yi = 0
for row in range(len(x_time)):
    S_xi2yi += pow(x_time[row],2)*kaist_avr[row]
#print(S_xi2yi)

# 독립변수 배열 x의 각 인덱스의 네제곱의 합
S_xi4 = 0
for row in x_time:
    S_xi4 += pow(row,4)
#print(S_xi4)

#
S_xx = S_xi2 - pow(S_xi,2)/len(x_time)
S_xy = S_xiyi -(S_xi*S_yi/len(x_time))
S_xx2 = S_xi3 - (S_xi*S_xi2/len(x_time))
S_x2y = S_xi2yi - (S_xi2*S_yi/len(x_time))
S_x2x2 = S_xi4 - (pow(S_xi2,2)/len(x_time))

a = ((S_x2y *S_xx) - (S_xy*S_xx2)) / (S_xx*S_x2x2 -pow(S_xx2,2))
b = ((S_xy*S_x2x2)-(S_x2y*S_xx2)) / (S_xx*S_x2x2-pow(S_xx2,2))
c = (S_yi/len(x_time)) -(b*(S_xi/len(x_time))) -(a*S_xi2/len(x_time))

print(a, b, c)

z = [] # 예측값이 들어갈 배열
z1 = []

for i in range(len(x_time)):
    z.append(a*pow(x_time[i],2) + b*x_time[i] + c) # a,b,c를 이용한 예측값
    z1.append(z[i])


#plot(x_time, kaist_avr, 'bs') # 시간대별 평균값
#plot(x_time, z, 'r') # 예측값
#plot(x_time, kaist_day_val, 'g') # 임의의 날짜의 시간대별 데이터

S_avr = S_yi / len(x_time)
S_avr2 = 0
for i in range(len(x_time)):
    S_avr2 += kaist_day_val[i]
S_avr2 /= len(x_time)
# S_avr


#plot(x_time, z1, 'm')

sum = 0
for i in range(len(x_time)):
    sum += abs((kaist_day_val[i] - z[i]) / z[i])
#print('err = ', sum/len(x_time)*100)

S_t = S_chu = 0
for i in range(len(x_time)):
    S_t += pow(kaist_avr[i] - S_avr, 2)
    S_chu += pow(kaist_avr[i]-z[i],2)

CoD = (S_t - S_chu) / S_t # Coefficient of Determination 결정 계수
print('r^2 = ', CoD)

# 표준 편차를 구하자.
std_deviation = sqrt(S_chu/(len(x_time)-(2+1)))
print(std_deviation)

legent_count = 0

while 1:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='capstone')
    curs = conn.cursor()
    now_date = datetime.datetime.now()
    s_date = "'" + str(now_date.year) + '-' + str(now_date.month) + '-' + str(now_date.day) + "'"
    sql = 'select * from pv where cnlnum = 1001 and stat =1 and datetime > ' + s_date + ';'
    curs.execute(sql)
    rows = curs.fetchall()
    val_count = []
    values = []
    hour = []
    res = []

    XZ1 = 0
    XZ2 = 0
    XZ_count = 0
    day_count = 0
    for i in range(0,12): #0 = 7, 12 = 18
        val_count.append(0)
        values.append(0)
        res.append(0)
        hour.append(i+7)
    for row in rows: #row[1] = date, row[3] = values
        arr_val = row[1].hour - 7
        if(arr_val >= 0):
            if(arr_val < 12):
                val_count[arr_val] += 1
                values[arr_val] += row[3]

    for i in range(0,12):
        if(val_count[i] != 0):
            values[i] = values[i] / val_count[i]
            XZ1 += values[i]
            XZ2 += kaist_avr[i]
            XZ_count += 1
            day_count = i
    if(day_count>0):
        XZ1 /= XZ_count
        XZ2 /= XZ_count
        diff_rate = XZ1 / XZ2
    else:
        diff_rate = 1
    current_time = []
    current_value = []

    for i in range(0,12):
        res[i] = z[i] * diff_rate

    for i in range(0, day_count + 1):
        current_time.append(7 + i)
        current_value.append(values[i])
    label_string = 'Current value' + '\n = ' + str(int(values[day_count])) + ' mW'
    plot(current_time, current_value, 'bs', label=label_string)
    label_string = 'Predicted value' + '\n = ' + str(int(res[day_count])) + ' mW'
    plot(hour, res, 'r--', label = label_string)

    title('PV ')
    xlabel('Time (hour)')
    ylabel('Production (mW)')

    legend(loc='upper left')

    grid(True)

    #show()
    image_path = os.path.abspath('C:\SCADA\ScadaWeb\plugins\Scheme')
    savefig(os.path.join(image_path, image_file))
    plt.close()

    time.sleep(2)

    recv_msg = []
    for i in range(12):
        recv_msg.append(0)
    send_msg = []
    send = []

    data = clientSocket.recv(65535)
    temp_msg = data.decode()

    for i in range(12):
        recv_msg[i] = ord(temp_msg[i])

    print('recv message = ', recv_msg)

    length = recv_msg[11] * 2 + 3

    for i in range(length + 6):
        send_msg.append(0)
        send.append(0)
    for i in range(8):
        send_msg[i] = recv_msg[i]
    send_msg[4] = int(length / 256)
    send_msg[5] = length % 256
    send_msg[8] = recv_msg[11] * 2

    print(res)
    if(day_count > 0):
        if(day_count <11):
            result = int(res[day_count + 1] * 1000)
        else:
            result = int(res[day_count] * 1000)
    else:
        result = 0
    send_msg[9] = int(result / 256)
    send_msg[10] = result % 256

    for i in range(length + 6):
        send[i] = chr(send_msg[i])
    s = ''.join(send)
    print('send message = ', send_msg)
    clientSocket.send(s.encode('utf-8'))

clientSocket.close()
serverSocket.close()
conn.close()