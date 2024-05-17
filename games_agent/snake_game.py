import pygame
import sys
import random
from multiprocessing import Process, Queue

class SnakeGame:
    def __init__(self, control_queue, output_queue):
        self.control_queue = control_queue
        self.output_queue = output_queue
        # 初始化 Pygame
        pygame.init()

        # 设置屏幕大小
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("贪吃蛇")

        # 定义颜色
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)

        # 设置时钟
        self.clock = pygame.time.Clock()

        # 设置蛇和食物的大小
        self.snake_block = 20
        self.snake_speed = 10

        # 字体设置
        self.font_style = pygame.font.SysFont(None, 50)

        # 初始化游戏状态
        self.game_over = False
        self.game_close = False

        self.x1 = self.screen_width / 2
        self.y1 = self.screen_height / 2

        self.x1_change = 0
        self.y1_change = 0

        self.snake_List = []
        self.Length_of_snake = 1

        self.snake_Head = [self.x1, self.y1]

        self.foodx = round(random.randrange(0, self.screen_width - self.snake_block) / self.snake_block) * self.snake_block
        self.foody = round(random.randrange(0, self.screen_height - self.snake_block) / self.snake_block) * self.snake_block

        # 添加用于保存上一个状态的变量
        self.previous_state = (self.snake_Head.copy(), self.snake_List.copy(), self.foodx, self.foody)
        self.output_queue.put(f"""
当前蛇头位置：{self.snake_Head}
当前蛇身位置：{self.snake_Head}
当前食物位置：[{self.foodx}, {self.foody}]
当前得分：{self.Length_of_snake - 1}
""")

    def our_snake(self):
        for x in self.snake_List:
            pygame.draw.rect(self.screen, self.GREEN, [x[0], x[1], self.snake_block, self.snake_block])

    def message(self, msg, color):
        mesg = self.font_style.render(msg, True, color)
        self.screen.blit(mesg, [self.screen_width / 6, self.screen_height / 3])

    def update_direction(self):
        while not self.control_queue.empty():
            direction = self.control_queue.get()
            if direction == "LEFT" and self.x1_change == 0:
                self.x1_change = -self.snake_block
                self.y1_change = 0
            elif direction == "RIGHT" and self.x1_change == 0:
                self.x1_change = self.snake_block
                self.y1_change = 0
            elif direction == "UP" and self.y1_change == 0:
                self.y1_change = -self.snake_block
                self.x1_change = 0
            elif direction == "DOWN" and self.y1_change == 0:
                self.y1_change = self.snake_block
                self.x1_change = 0

    def observation(self):
        # 比较当前状态和上一个状态，如果有变化，则输出状态
        current_state = (self.snake_Head.copy(), self.snake_List.copy(), self.foodx, self.foody)
        if current_state != self.previous_state:
            stat_snake = f"""
当前蛇头位置：{self.snake_Head}
当前蛇身位置：{self.snake_List}
当前食物位置：[{self.foodx}, {self.foody}]
当前得分：{self.Length_of_snake - 1}
"""
            self.output_queue.put(stat_snake)
            # 更新上一个状态
            self.previous_state = current_state

    def run(self):
        while not self.game_over:
            while self.game_close:
                self.screen.fill(self.BLACK)
                self.message("You Lost! Press Q-Quit or C-Play Again", self.RED)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.game_over = True
                            self.game_close = False
                        if event.key == pygame.K_c:
                            self.__init__(self.control_queue, self.output_queue)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            self.update_direction()

            if self.x1_change != 0 or self.y1_change != 0:
                self.x1 += self.x1_change
                self.y1 += self.y1_change

                if self.x1 >= self.screen_width or self.x1 < 0 or self.y1 >= self.screen_height or self.y1 < 0:
                    self.game_close = True

                self.snake_Head = [self.x1, self.y1]
                self.snake_List.append(self.snake_Head)

                if len(self.snake_List) > self.Length_of_snake:
                    del self.snake_List[0]

                for x in self.snake_List[:-1]:
                    if x == self.snake_Head:
                        self.game_close = True

                self.screen.fill(self.BLACK)
                pygame.draw.rect(self.screen, self.RED, [self.foodx, self.foody, self.snake_block, self.snake_block])
                self.our_snake()
                pygame.display.update()

                if self.x1 == self.foodx and self.y1 == self.foody:
                    self.Length_of_snake += 1
                    self.foodx = round(random.randrange(0, self.screen_width - self.snake_block) / self.snake_block) * self.snake_block
                    self.foody = round(random.randrange(0, self.screen_height - self.snake_block) / self.snake_block) * self.snake_block

                self.x1_change = 0
                self.y1_change = 0

                # 调用观察方法
                self.observation()

            self.clock.tick(self.snake_speed)

        pygame.quit()
        sys.exit()

def game_process(control_queue, output_queue):
    game = SnakeGame(control_queue, output_queue)
    game.run()

if __name__ == "__main__":
    control_queue = Queue()
    output_queue = Queue()
    process = Process(target=game_process, args=(control_queue, output_queue))
    process.start()
    process.join()
