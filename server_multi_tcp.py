##############################################################################
# server.py
##############################################################################
import random
import socket
import chatlib
import select
import time
import ast
import requests
import json
#import logging
from  loguru import logger


client_sockets = []
messages_to_send = []
logged_users = {}
MAX_MSG_SIZE = 1024
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "0.0.0.0"
users = {}
questions = {}

#logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')

r = requests.get('https://opentdb.com/api.php?amount=50&type=multiple')
b = r.json()





with open('C:\\users\\ariel\PycharmProjects\pythonProject\\venv\\users', 'r') as f:
    for line in f:
        users.update(ast.literal_eval(line.strip()))


def print_client_socket(client_sockets):

    for c in client_sockets:
        print("\t", c.getpeername())


def build_and_send_message(conn, code, data=''):

    global messages_to_send

    msg = chatlib.build_message(code, data)
    logger.info('["SERVER"] {} msg: {} ', conn.getpeername(), msg )
    messages_to_send.append((conn, msg))



def recv_message_and_parse(conn):

    msg = conn.recv(MAX_MSG_SIZE).decode()
    cmd, data = chatlib.parse_message(msg)

    if len(msg) > 1:
        #print(["CLIENT11"], conn.getpeername(), 'msg:', msg)
        logger.info('["CLIENT22"] {} msg: {}', conn.getpeername(), msg )
    return cmd, data

def load_questions():

    counter = 1
    for i in b['results']:
        questions[int(counter)] = str(i).replace('&#039;', '`').replace('&quot;', '`')
        counter += 1

    return questions

def load_user_database():

    return users

def setup_socket():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    return server_socket

def send_error(conn, error_msg):

    build_and_send_message(conn,chatlib.PROTOCOL_SERVER["error_msg"], error_msg)

def handle_getscore_message(conn, username):

    score_users = load_user_database()
    build_and_send_message(conn,chatlib.PROTOCOL_SERVER["yourscore_msg"] ,score_users[username]["score"])

def handle_highscore_message(conn):

    score_of_the_player = {}
    users = load_user_database()
    for i in users.keys():
        score_of_the_player[i] = users[i]["score"]
        result = '\n'.join(f'{key}: {value}' for key, value in sorted(score_of_the_player.items(), key=lambda item: item[1], reverse=True))
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["allscore_msg"], result )

def handle_logged_message(conn):

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["loggedanswer_msg"], ', '.join(logged_users.values()))


def handle_logout_message(conn):

    global logged_users

    #print("Connection closed", conn.getpeername())
    logger.info("Connection closed {}", conn.getpeername())
    client_sockets.remove(conn)
    logged_users.pop(conn)
    conn.close()

def create_random_question(conn, username):

    users = load_user_database()
    question = load_questions()
    questions_list = [i for i in question.keys() if i not in users[username]['questions_asked']]

    try:
        rand = random.choice(questions_list)
        res = eval(question[rand])
        key, value = (rand, res)
        print(res)
    except:
        logger.info(conn.getpeername())
        #print('Cannot choose from an empty sequence')
        Exception('Cannot choose from an empty sequence')
        key, value = None, None
        return key, value

    else:
        with open('C:\\users\\ariel\PycharmProjects\pythonProject\\venv\\users', 'w') as f:
            users[username]['questions_asked'].append(key)
            f.write(str(users))
        q_list = [i for i in value['incorrect_answers']]
        q_list.append(value['correct_answer'])
        q_list.sort()

        return str(key) + '#' + value['question'] + '#' + q_list[0]  + '#' + q_list[1] + '#' + q_list[2] + '#' + q_list[3]

def handle_question_message(conn, username):

    new_question = create_random_question(conn, username)
    if new_question != (None, None):
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["yourquestion_msg"], new_question)
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["noquestion_msg"])


def handle_answer_message(conn, username, data):

    users = load_user_database()
    questions = load_questions()

    number, answer = chatlib.split_data(data, 1)
    if (number in users[username]['questions_asked']) == False:
        correct_answer = eval(questions[int(number)])
        if answer ==  correct_answer['correct_answer']:
            with open('C:\\users\\ariel\PycharmProjects\pythonProject\\venv\\users', 'w') as f:
                users[username]['score'] = users[username]['score'] + 5
                f.write(str(users))

            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correctanswer_msg"])

        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wronganswer_msg"] , correct_answer['correct_answer'] )
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wronganswer_msg"],chatlib.PROTOCOL_SERVER["answer_twice"] )

def handle_login_message(conn, data):

    global logged_users
    user, password =  chatlib.split_data(data, 1)
    exists_users = load_user_database()
    if user in exists_users.keys():
        if password == exists_users[user]['password']:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"])
            logged_users.update({conn:user})
        else:
            send_error(conn, chatlib.PROTOCOL_SERVER["password_is_not_match"])
    else:
        send_error(conn,chatlib.PROTOCOL_SERVER["user_is-not_exists"])


def handle_client_message(conn, cmd, data):

    global logged_users
    if conn not in logged_users.keys():

        if cmd == 'LOGIN' :
            handle_login_message(conn, data)

        elif cmd == None:
            handle_logout_message(conn)

        else:
             send_error(conn, chatlib.PROTOCOL_SERVER["error_msg"] + " Unknow command!")


    elif cmd == "LOGOUT" or cmd == None:
        handle_logout_message(conn)

    elif cmd == 'MY_SCORE':
        handle_getscore_message(conn, logged_users[conn])

    elif cmd == 'HIGHSCORE':
        handle_highscore_message(conn)

    elif cmd == 'LOGGED':
        handle_logged_message(conn)

    elif cmd == 'GET_QUESTION':
        handle_question_message(conn,  logged_users[conn])

    elif cmd == 'SEND_ANSWER':
        handle_answer_message(conn, logged_users[conn], data)

    else:
        send_error(conn, chatlib.PROTOCOL_SERVER["error_msg"] + " Unknow command!")

def main():
    global users
    global questions
    global client_sockets

    server_socket = setup_socket()
    data = ''

    while True:

        logger.info("['SERVER'] waiting for connection...")
        ready_to_read, ready_to_write, in_erorr = select.select([server_socket] + client_sockets, [] , [] )

        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                logger.info('New client joined! {} {yossi}', client_address, yossi=client_address)
                client_sockets.append(client_socket)

            else:

                try:
                    cmd, data = recv_message_and_parse(current_socket)

                    if data == " " or  data == None :
                        handle_client_message(current_socket, cmd, data)
                        client_sockets.remove(current_socket)
                        logged_users.pop(conn)

                    else:
                        handle_client_message(current_socket, cmd, data)

                except:
                    Exception(ConnectionResetError)
        for message in messages_to_send:
            current_socket, data = message
            current_socket.send(data.encode())
        messages_to_send.clear()


if __name__ == '__main__':
    main()

