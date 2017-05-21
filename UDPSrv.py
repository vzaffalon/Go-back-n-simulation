from socket import *
from Ack import *
from Message import *
import time
import json
import random
import thread

#todo
#checksum
#caracter shift for generating error
#not sendind ack on case off ack lost
#envio de arquivo

#global variables
clientAddress = 0    #variavel que recebera endereco do cliente
randomChance = 10    #valor em porcentagem da chance de erros ocorrerem
timeBetweenAcksSend = 2   #tempo em segundos entre envio de acks

def sendAck(sequenceNumber,data):
    ack = Ack(sequenceNumber,data + " ack")
    ackSerialization = json.dumps(ack.__dict__)  #envia o ack em formato json
    serverSocket.sendto(ackSerialization, clientAddress)
    if sequenceNumber == -1:
        print "Ack com falha enviado: " + '\n' + "Mensagem: "+ ack.data + '\n' + "sequenceNumber: " + str(ack.sequenceNumber)  +  '\n'
    else:
        print "Ack enviado: " + '\n' + "Mensagem: "+ ack.data + '\n' + "sequenceNumber: " + str(ack.sequenceNumber)  + '\n'


def receiveMessage():
    global clientAddress
    messageSerialized, address = serverSocket.recvfrom(2048)
    clientAddress = address
    message = json.loads(messageSerialized)  #recebe a mensagem em formato json
    print "Mensagem Recebida: " + '\n' + "Mensagem: "+ message['data'] + '\n' + "sequenceNumber: " + str(message['sequenceNumber']) +  '\n'
    return message

def generateRandomChanceOfFail():
    global randomChance
    if random.randrange(0,100) < randomChance:
        return True
    else:
        return False

def verifyAckFailures(message):
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

def receiveAck():
    while 1:
        time.sleep(timeBetweenAcksSend)          #gera um tempo entre envio de pacotes
        message = receiveMessage()
        verifyAckFailures(message)

if __name__ == "__main__":
    #socket config variables
    serverIp = ''
    serverPort = 12000

    #server socket configuration
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((serverIp, serverPort))
    print 'The server is ready to receive' + '\n'

    #create and start threads
    thread.start_new_thread(receiveAck, ())

    while 1:
        pass
