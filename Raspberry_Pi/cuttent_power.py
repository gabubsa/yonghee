import socket as sock
import struct
from ina219 import INA219
from ina219 import DeviceRangeError
import time
SHUNT_OHMS = 0.1

a = 0

def make_response(request,resp_Data):
    resp_Transactionid = (request[0] << 8)+request[1]  # 2Bytes
    resp_Protocolid = (request[2]<<8)+request[3]  # 2Bytes
    resp_Unitid = request[6]  # 1Byte
    resp_Functioncode = request[7]  # 1Byte
    resp_Bytecount = request[11]<<1  # 1Byte
    resp_Length = resp_Bytecount+3  # 2Bytes
    #resp_Data = 1  # 2Bytes

    response = struct.pack("!hhhbbbh", resp_Transactionid, resp_Protocolid,
                           resp_Length, resp_Unitid, resp_Functioncode,
                           resp_Bytecount, resp_Data)
    return response

def read():
   #ina = INA219(SHUNT_OHMS,max_expected_amps = 0.6, address = 0x40)
    ina = INA219(SHUNT_OHMS,max_expected_amps = 0.2, address = 0x40)
    ina.configure(voltage_range = ina.RANGE_16V, gain= ina.GAIN_AUTO,
                  bus_adc = ina.ADC_128SAMP,shunt_adc = ina.ADC_128SAMP)
    print ("Bus Voltage: %.3f V" % ina.voltage())
    a = ina.power()
    try:
        print ("Bus Current: %.3f mA" % ina.current())
        print ("Power: %.3f mW" % ina.power())
        print ("Shunt voltage: %.3f mV" % ina.shunt_voltage())
        a = ina.power()
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print (e)
        a = ina.power()
    return a

if __name__ == '__main__':
    #host = '192.168.0.19'
    host = '169.254.69.231'
    port = 2999

    server_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    conn, addr = server_sock.accept()

    request = bytearray(12)

    with conn:
        print('connected addr : ', addr)

        while True:
            conn.recv_into(request, 12)
            print('request : ', request)
            b = int(read()*1000)
            print(b)
            resp_Data = b
            response = make_response(request,resp_Data)

            print('response : ',response)
            conn.send(response)