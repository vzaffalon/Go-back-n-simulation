from socket import *
from Ack import *
from Message import *
import time
import json
import random

#global variables
clientAddress = 0    #variavel que recebera endereco do cliente
randomChance = 10    #valor em porcentagem da chance de erros ocorrerem
timeBetweenAcksSend = 3   #tempo em segundos entre envio de acks

def sendAck(sequenceNumber,data):
    ack = Ack(sequenceNumber,data + " ack")
    ackSerialization = json.dumps(ack.__dict__)  #envia o ack em formato json
    serverSocket.sendto(ackSerialization, clientAddress)
    if sequenceNumber == -1:
        print "Ack com falha enviado: " + str(ack.__dict__) + '\n'
    else:
        print "Ack enviado: " + str(ack.__dict__) + '\n'


def receiveMessage():
    global clientAddress
    messageSerialized, address = serverSocket.recvfrom(2048)
    clientAddress = address
    message = json.loads(messageSerialized)  #recebe a mensagem em formato json
    print "Mensagem recebida " + str(message) + '\n'
    return message

def generateRandomChanceOfFail():
    global randomChance
    if random.randrange(0,100) < randomChance:
        return True
    else:
        return False

def verifyAckFailures():
    if generateRandomChanceOfFail() == True:
        #envia mensagem com falha de ack ou seja sequenceNumber -1 gerando timeout
        sendAck(-1,message['data'])
    else:
        if generateRandomChanceOfFail() == True:
            #envia mensagem na ordem incorreta ou seja envia sequenceNumber errado
            sendAck(message['sequenceNumber'] + 1,message['data'])
        else:
            #nenhum erro envia mensagem normalmente com sequenceNumber correto
            sendAck(message['sequenceNumber'],message['data'])

#socket config variables
serverIp = ''
serverPort = 12000

#server socket configuration
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverIp, serverPort))
print 'The server is ready to receive' + '\n'

while 1:
    time.sleep(timeBetweenAcksSend)          #gera um tempo entre envio de pacotes
    message = receiveMessage()
    verifyAckFailures()
