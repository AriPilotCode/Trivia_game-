import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

MAX_MSG_SIZE = 1024
SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT =  5678


def build_and_send_message(conn, code, data=''):

    msg = chatlib.build_message(code,data)
    conn.send(msg.encode())

def recv_message_and_parse(conn):

    msg = conn.recv(MAX_MSG_SIZE).decode()
    cmd, data = chatlib.parse_message(msg)
    return cmd, data

def connect():

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return my_socket

def error_and_exit(error_msg):

    print(error_msg)
    exit()

def build_send_recv_parse(conn, command, data=''):

    build_and_send_message(conn, command,data)
    cmd, code = recv_message_and_parse(conn)
    return cmd, code

def get_score(conn):

    cmd, data = build_send_recv_parse(conn,chatlib.PROTOCOL_CLIENT["myscore_msg"])
    if cmd == chatlib.PROTOCOL_SERVER["yourscore_msg"] :
        return "your score is " + data
    else:
        error_and_exit(cmd)

def  get_highscore(conn):

    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"])
    if cmd == chatlib.PROTOCOL_SERVER["allscore_msg"]:
        return data
    else:
        error_and_exit(cmd)

def play_question(conn):

    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["getquestion_msg"])

    if cmd == chatlib.PROTOCOL_SERVER["yourquestion_msg"]:
        splited = data.split('#')
        n, a, b, c, d, e = splited
        print('Q: ' + a, "  \n     1. " + b, "\n     2. " + c, "\n     3. " + d, " \n     4. " + e)

    elif cmd == chatlib.PROTOCOL_SERVER["noquestion_msg"]:
        print("GAME OVER")
        logout(conn)
        exit()

    else:
        error_and_exit(cmd)

    answer = input("Please choise your answer [1-4]:")
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["sendanswer_msg"],n + '#'+ splited[int(answer)+1])

    if cmd == chatlib.PROTOCOL_SERVER["correctanswer_msg"] or chatlib.PROTOCOL_SERVER["wronganswer_msg"]:
        if cmd == chatlib.PROTOCOL_SERVER["correctanswer_msg"]:
            print("YES!!!!")
        else:
            print("Nope, correct answer is #" + data)
    else:
        error_and_exit(cmd)

def get_logged_users(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged"])
    if cmd == chatlib.PROTOCOL_SERVER["loggedanswer_msg"]:
        return data
    else:
        error_and_exit(cmd)


def login(conn):

    conn.connect((SERVER_IP, SERVER_PORT))
    msg = ''

    while 'LOGIN_OK' not in msg:
        username = input("Please enter username: \n")
        password = input("Please enter the password: \n")
        msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["login_msg"], (username+"#"+password))

        if 'LOGIN_OK' not in msg:
            try:
                print(' '.join(msg))
            except:
                print(msg)
    print("Logged in!")


def logout(conn):

    build_and_send_message(conn,chatlib.PROTOCOL_CLIENT["logout_msg"])
    print("Goodbye!")
    conn.close()

def main():
    msg = ''
    conn = connect()

    login(conn)

    while msg != 'q':
        msg = input('p        Play a trivia question\n'
                    's        Get my score \n'
                    'h        Get high score\n'
                    'l        Get logged users\n'
                    'q        Quit\n'
                    'Please enter your choice:')

        if msg == 's':
           print(get_score(conn))

        elif msg == 'h':
           print(get_highscore(conn))

        elif msg =='p':
            play_question(conn)

        elif msg == 'l':
            print(get_logged_users(conn))


    logout(conn)

if __name__ == '__main__':
    main()
