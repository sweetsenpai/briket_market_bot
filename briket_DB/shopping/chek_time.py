from datetime import datetime


def order_time_chekker():
    data_time = datetime.now()
    w_day = data_time.weekday()
    h_day = int(data_time.now().hour)
    if w_day == 6:
        if h_day > 23 or h_day < 11:
            return False
        else:
            return True
    else:
        if h_day > 21 or h_day < 10:
            return False
        else:
            return True

