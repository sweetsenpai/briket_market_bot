from datetime import datetime


def order_time_chekker():
    now_h = int(datetime.now().hour)
    if now_h > 20 or now_h < 10:
        return False
    return True
