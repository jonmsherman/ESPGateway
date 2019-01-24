import nrfAPI
import time
import network
import ubinascii
import socket
import urequests
import json

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        # sta_if.connectn('Jon\'s Internet', 'dextermorgan')
        sta_if.connect('NU-Connect')
    while not sta_if.isconnected():
        pass
    print('network config:', sta_if.ifconfig()) 

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

do_connect()
nrfAPI.nrf_setup()
nrfAPI.RX_mode()
http_get('http://micropython.org/ks/test.html')
while 1:
    if nrfAPI.can_read_data() == True:
        print("Got something...")
        # int_values = [x for x in frame]
        # value = int.from_bytes(nrfAPI.receive_dynamic_data(),'big')
        # print(hex(value))
        # print("\n")
        byte_array = nrfAPI.receive_dynamic_data()
        int_values = [x for x in byte_array]
        string_values = ','.join(str(s) for s in int_values)
        data = '{"data": "' + string_values + '"}'
        headers = {'content-type': 'application/json'}
        response = urequests.post("http://espgatewayapi.azurewebsites.net/api/ESPGateway", data = data,headers=headers)

        # print(response.text)
        




# do_connect()
# mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
# print(mac)

# data = '{"data": "15,16,17"}'


# # convert into JSON:
# y = json.dumps(x)

# # the result is a JSON string:
# print(y)
# headers = {'content-type': 'application/json'}

# response = urequests.post("http://espgatewayapi.azurewebsites.net/api/ESPGateway", data = data,headers=headers)

# print(response.text)
