#!/usr/bin/env python3
# encoding: utf-8
import socket
import threading
import select
import sys
import time
from os import system

system("clear")

#conexao
IP = '0.0.0.0'
try:
   PORT = int(sys.argv[1])
except:
   PORT = 80
PASS = ''
BUFLEN = 8196 * 8
TIMEOUT = 60
MSG = '@VSAIOSSH'
COR = '<font color="null">'
FTAG = '</font>'
DEFAULT_HOST = '0.0.0.0:22'
RESPONSE = "HTTP/1.1 200 " + str(COR) + str(MSG) + str(FTAG) + "\r\n\r\n"

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.running = False
        self.host = host
        self.port = port
        self.threads = []
        self.threadsLock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        self.soc.bind((self.host, self.port))
        self.soc.listen(5)
        self.running = True

        try:
            while self.running:
                try:
                    c, addr = self.soc.accept()
                    c.setblocking(1)
                except socket.timeout:
                    continue

                conn = ConnectionHandler(c, self, addr)
                conn.start()
                self.addConn(conn)
        finally:
            self.running = False
            self.soc.close()

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            for c in self.threads[:]:
                c.close()


class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        super().__init__()
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = b''
        self.server = server

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except:
                pass
            self.clientClosed = True

        if not self.targetClosed:
            try:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
            except:
                pass
            self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)

            hostPort = self.findHeader(self.client_buffer, b'X-Real-Host')
            if not hostPort:
                hostPort = DEFAULT_HOST

            split = self.findHeader(self.client_buffer, b'X-Split')
            if split:
                self.client.recv(BUFLEN)

            if hostPort:
                passwd = self.findHeader(self.client_buffer, b'X-Pass')

                if PASS and passwd == PASS:
                    self.method_CONNECT(hostPort)
                elif PASS and passwd != PASS:
                    self.client.send(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
                elif hostPort.startswith(IP):
                    self.method_CONNECT(hostPort)
                else:
                    self.client.send(b'HTTP/1.1 403 Forbidden!\r\n\r\n')
            else:
                print('- No X-Real-Host!')
                self.client.send(b'HTTP/1.1 400 NoXRealHost!\r\n\r\n')

        except Exception as e:
            print(f"Erro: {e}")
        finally:
            self.close()
            self.server.removeConn(self)

    def findHeader(self, head, header):
        try:
            head_str = head.decode('utf-8', errors='ignore')
            aux = head_str.find(header.decode('utf-8') + ': ')
            if aux == -1:
                return ''

            aux = head_str.find(':', aux) + 2
            end = head_str.find('\r\n', aux)
            return head_str[aux:end] if end != -1 else ''
        except Exception as e:
            print(f"Erro ao processar header: {e}")
            return ''

    def connect_target(self, host):
        i = host.find(':')
        if i != -1:
            port = int(host[i + 1:])
            host = host[:i]
        else:
            port = 443 if self.method == 'CONNECT' else 22

        addr_info = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(addr_info[0], addr_info[1], addr_info[2])
        self.targetClosed = False
        self.target.connect(addr_info[4])

    def method_CONNECT(self, path):
        self.connect_target(path)
        self.client.sendall(RESPONSE)
        self.client_buffer = b''
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        error = False

        while True:
            count += 1
            recv, _, err = select.select(socs, [], socs, 3)
            if err:
                error = True

            if recv:
                for in_ in recv:
                    try:
                        data = in_.recv(BUFLEN)
                        if data:
                            if in_ is self.target:
                                self.client.sendall(data)
                            else:
                                while data:
                                    sent = self.target.send(data)
                                    data = data[sent:]

                            count = 0
                        else:
                            break
                    except:
                        error = True
                        break

            if count == TIMEOUT or error:
                break


def main():
    print("\033[0;34m━" * 8, "\033[1;32m VSAIO PSOCKS", "\033[0;34m━" * 8, "\n")
    print("\033[1;33mIP:\033[1;32m", IP)
    print("\033[1;33mPORTA:\033[1;32m", PORT, "\n")
    print("\033[0;34m━" * 10, "\033[1;32m VSAIOSSH", "\033[0;34m━\033[1;37m" * 11, "\n")

    server = Server(IP, PORT)
    server.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nParando...")
        server.close()


if __name__ == '__main__':
    main()