#%%
"""
通过键盘输入来控制贪吃蛇游戏。
"""
from multiprocessing import Queue, Process
import snake_game
import keyboard
import time

def get_user_input():
    while True:
        if keyboard.is_pressed('up'):
            return "UP"
        elif keyboard.is_pressed('down'):
            return "DOWN"
        elif keyboard.is_pressed('left'):
            return "LEFT"
        elif keyboard.is_pressed('right'):
            return "RIGHT"
        elif keyboard.is_pressed('esc'):
            return "EXIT"
        time.sleep(0.1)

if __name__ == "__main__":
    # 创建控制队列和输出队列
    control_queue = Queue()
    output_queue = Queue()

    # 启动游戏进程
    process = Process(target=snake_game.game_process, args=(control_queue, output_queue))
    process.start()

    try:
        while process.is_alive():
            # 获取用户输入并发送控制指令
            direction = get_user_input()
            if direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                control_queue.put(direction)
            elif direction == "EXIT":
                process.terminate()
                process.join()
                print("游戏结束")
                break

            # 检查输出队列并打印状态
            while not output_queue.empty():
                print(output_queue.get())

    except KeyboardInterrupt:
        print("游戏中断")
        process.terminate()
        process.join()
    except Exception as e:
        print(f"出现错误: {e}")
        process.terminate()
        process.join()
    finally:
        if process.is_alive():
            process.terminate()
        process.join()

# %%
