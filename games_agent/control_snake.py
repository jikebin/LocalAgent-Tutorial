#%%
from multiprocessing import Queue, Process
import time
import snake_game
from AgentControl import AgentControl

def get_user_input():
    # 获取用户输入的方向
    direction = input("输入控制指令（UP, DOWN, LEFT, RIGHT，EXIT）: ").strip().upper()
    return direction


# 这个后面应该是一个类，而不是方法 
# def agent_control(process,control_queue, output_queue):
#     while process.is_alive():
#         # 获取用户输入并发送控制指令
#         direction = get_user_input()
#         if direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
#             control_queue.put(direction)
#         elif direction == "EXIT":
#             process.terminate()
#             process.join()
#             print("游戏结束")
#             break

#         # 等待片刻以便状态更新
#         time.sleep(0.1)

#         # 检查输出队列并打印状态
#         while not output_queue.empty():
#             print(output_queue.get())



if __name__ == "__main__":
    # 创建控制队列和输出队列
    control_queue = Queue()
    output_queue = Queue()
    llm = AgentControl()

    # 启动游戏进程
    process = Process(target=snake_game.game_process, args=(control_queue, output_queue))
    process.start()

    try:
        # 通过Agent进行游戏控制
        # agent_control(process,control_queue, output_queue)
        res = llm.control(process,control_queue, output_queue)
        # 输出内容
        for i in res:
            print(i,end="")
        
           
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
