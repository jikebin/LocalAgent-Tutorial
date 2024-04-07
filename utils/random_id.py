
#%%
import time
import random
import string

def get_id():
    # 获取当前时间的时间戳（自纪元以来的秒数）
    epoch_seconds = int(time.time())
    # 获取秒数的后四位
    last_four_digits = str(epoch_seconds)[-4:]
    # Generate a random character from a-z, A-Z, and 0-9
    random_char = random.choice(string.ascii_letters + string.digits)
    return str(last_four_digits)+random_char


if __name__ == "__main__":
    print(get_id())
# %%
