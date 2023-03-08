# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "myscore_msg": "MY_SCORE",
    "highscore_msg": "HIGHSCORE",
    "getquestion_msg": "GET_QUESTION",
    "sendanswer_msg": "SEND_ANSWER",
    "logged": "LOGGED"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "logout_msg": "LOGOUT",
    "user_is-not_exists": "Username does not exist",
    "password_is_not_match": "Error! Password does not match!",
    "yourscore_msg": "YOUR_SCORE",
    "allscore_msg": "ALL_SCORE",
    "yourquestion_msg": "YOUR_QUESTION",
    "correctanswer_msg": "CORRECT_ANSWER!",
    "wronganswer_msg": "WRONG_ANSWER",
    "noquestion_msg": "NO_QUESTIONS",
    "loggedanswer_msg": "LOGGED_ANSWER",
    "error_msg": "ERROR",
    "answer_twice": "Error! USED ANSWER!"

}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data=''):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    data = str(data)
    space = ' '
    full_msg = "'{}{}|{}|{}'".format(cmd, space *(16-len(cmd)), str(len(data)).zfill(4), data)
    if len(cmd) >= 5 and len(cmd) <= 15:
        return full_msg[1:-1]
    else:
        return ERROR_RETURN


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    if data.count('|') != 2:
        return None, None

    full_data = data.split('|')
    cmd = full_data[0].replace(" ", "")
    lngth = full_data[1]
    msg = full_data[2]

    for i in lngth:
        if i.isspace() == False and i.isnumeric() == False:
            return None, None

    if len(lngth) != 4:
        return ERROR_RETURN, ERROR_RETURN

    if len(msg) != int(lngth):
        return ERROR_RETURN, ERROR_RETURN
    else:
        return cmd, msg


def split_data(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    # Implement code ...

    if msg.count('#') != expected_fields:
        return ERROR_RETURN
    else:
        return msg.split('#')


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    # Implement code ...

    str_list = []
    for i in msg_fields:
        str_list.append(str(i))

    return "#".join(str_list)