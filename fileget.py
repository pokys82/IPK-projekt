import argparse
import sys
import re
from os import path
import socket


def checkData(data):
    if re.search(b"[S][u][c][c][e][s][s]", data[0]):
        return

    else:
        print("Error - data not found!", file=sys.stderr)
        exit(2)


def checkError(data_to_check):
    status = data_to_check.split(" ")

    if status[0] != "OK":
        print("Error - while getting file address", file=sys.stderr)
        exit(2)

    else:
        return

"""       UDP         """  
def getIP(UDP_IP, UDP_PORT, MESSAGE):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if sock == -1:
            print("Error - while creating socket!", file=sys.stderr)
            exit(2)

        sock.bind((UDP_IP, 0))
        sock.sendto(MESSAGE, (UDP_IP, int(UDP_PORT)))
        sock.settimeout(30)
        data, addr = sock.recvfrom(1024)
        data = str(data,'utf-8')
        return(data)

    except socket.error as exc:
        print("Error - UDP-socket exception : %s" %exc, file=sys.stderr)
        exit(2)

"""       TCP         """  
def getData(data, file_name, file_server_name):
    MESSAGE = bytes("GET "+file_name+" FSP/1.0\r\n\rAgent: xpokor82\r\n\rHostname: "+file_server_name+"\r\n\r", "utf-8")
    outputUDP = data.split(" ")
    address = outputUDP[1]
    address = address.split(":")
    TCP_IP = address[0]
    TCP_PORT = address[1]

    try:
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.connect((TCP_IP, int(TCP_PORT)))
        tcpSocket.send(MESSAGE)

        data_out = []
        loop = True
        while loop:

            tcpSocket.settimeout(30)
            data, addr = tcpSocket.recvfrom(1024)
            data = bytearray(data)

            if len(data):
                data_out.append(data)

            else:
                loop = False
                tcpSocket.close()

        checkData(data_out)

        # remove header
        if len(data_out) > 1:
            data_out.pop(0)

        else:
            position = data_out[0].find(b"\r\n\r\n")
            data_out[0] = data_out[0][position+4:]

        return(data_out)

    except socket.error as exc:
        print("Error - socket exception raised : %s" % exc, file=sys.stderr)
        exit(2)

"""       PARSING ARGUMENTS         """  
def parseArguments(args):
    parser = argparse.ArgumentParser(add_help=False) 
    parser.add_argument("-n", action="store", dest="server_name", required=True)
    parser.add_argument("-f", action="store", dest="file_path", required=True)
    args = parser.parse_args()

    server_name = args.server_name
    file_path = args.file_path

    #   VALIDATE ARGUMENTS
    if re.search("[^a-zA-Z0-9._-]:", server_name):
        print("Error - while checking ip!", file=sys.stderr)
        exit(3)

    #   GET SERVER IP AND PORT 
    split_server_name = server_name.split(":")
    UDP_IP = split_server_name[0]
    UDP_PORT = split_server_name[1]

    return UDP_IP, UDP_PORT, file_path

"""         GET NAMES OF FILE AND SERVER            """
def fileServerName(file_path):
    file_server_name = "empty"
    file_name = "empty"
    array = file_path.split("/")

    for x in range(len(array)):
        if x == 0:

            if array[x] == "fsp:":
                continue

            else:
                print("Error - wrong surl!", file=sys.stderr)

        elif x == 2:
            file_server_name = array[x]

        elif x == len(array)-1:
            file_name = array[x]

        else:
            continue

    return file_name, file_server_name, array

"""         CREATE FILE         """
def createFile(file_name, output):
    counter = 1
    path_name = file_name.split("/")

    if len(path_name) > 1:
        file_name = path_name[len(path_name)-1]

    while path.isfile(file_name):
        file_name = file_name+"("+str(counter)+")"
        counter += 1

    try:
        file = open(file_name, "bw")
        for x in output:
            file.write(x)

        file.close
        return
        
    except Exception as exc:
        print("Error - writing to file : %s" %exc, file=sys.stderr)
        exit(2)

"""         MAIN FUNCTION           """
def main():
    index = False

    UDP_IP, UDP_PORT, file_path = parseArguments(sys.argv)
    file_name, file_server_name, full_path = fileServerName(file_path)

    full_path.pop(0)
    full_path.pop(0)

    if file_name == "*":
        file_name = "index"
        index = True

    MESSAGE = bytes("WHEREIS "+file_server_name, "utf-8")

    if index:
        file_server_ip = getIP(UDP_IP, UDP_PORT, MESSAGE)
        checkError(file_server_ip)
        output = getData(file_server_ip, file_name, file_server_name)
        output = output[0].split(b"\r\n")

        for x in output:
            x = x.decode()
            if(x != ""):
                x = x.rstrip()
                output = getData(file_server_ip, x, file_server_name)
                createFile(x, output)

    else:
        file_server_ip = getIP(UDP_IP, UDP_PORT, MESSAGE)
        checkError(file_server_ip)
        output = getData(file_server_ip, file_name, file_server_name)
        createFile(file_name, output)

if __name__ == '__main__':
    main()