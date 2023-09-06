import sys
import pygame
import time
import numpy as np
import requests as req
from argparse import ArgumentParser

url = "http://127.0.0.1:8080"

def parse_action(x,y):
    return x+1,y+1

class Game:
    def __init__(self, you_are_black):
        self.board = empty_broad.copy()
        self.player = 1
        self.new(you_are_black)

    def new(self, you_are_black):
        json = {"you_are_black": you_are_black}
        res = req.post(f"{url}/new",json=json)
        json = res.json()
        self.id = json["id"]
        if "action" in json:
            self.take_action(json['action'])

    def play(self, action):
        json = {
            "id" : self.id,
            "action": list(action)
        }
        res = req.post(f"{url}/play",json=json)
        json = res.json()
        action = json.get("action", None)
        if action:
            self.take_action(action)
        return json["gameover"],json["winner"], action


    def take_action(self, action):
        i, j = action
        self.board[i-1, j-1] = self.player
        self.player *= -1
        return self.board

empty_broad = np.zeros([11, 11], dtype=np.int64)
for i in range(11//2):
    empty_broad[i][11-(5-i):] = 10
    empty_broad[10-i][:5-i] = 10


def visual_coordinates():
    L = 5 # number of layers
    XY = np.full((1+2*L, 1+2*L, 2), np.nan)

    R = (3**.5) / 2
    dxNewLayer = [None, -.5, .5, 1, .5, -.5, -1]
    dyNewLayer = [None, R, R, 0, -R, -R, 0]
    dxSameLayer = [None, 1, .5, -.5, -1, -.5, .5]
    dySameLayer = [None, 0, -R, -R, 0, R, R]
    diNewLayer = [None, 1, 1, 0, -1, -1, 0]
    djNewLayer = [None, 0, 1, 1, 0, -1, -1]
    diSameLayer = [None, 0, -1, -1, 0, 1, 1]
    djSameLayer = [None, 1, 0, -1, -1, 0, 1]
    
    i, j = L, L # stone positions
    x, y = 0, 0 # visual coordinates
    XY[i, j] = x, y
    for n in range(L):        # build a new layer
        for u in range(1, 7): # define a corner
            i = (n+1)*diNewLayer[u] + 5
            j = (n+1)*djNewLayer[u] + 5
            x = (n+1)*dxNewLayer[u]
            y = (n+1)*dyNewLayer[u]
            XY[i, j] = [x, y]
            for v in range(1, n+1): # go from the corner clockwise
                i += diSameLayer[u] # to the next corner
                j += djSameLayer[u]
                x += dxSameLayer[u]
                y += dySameLayer[u]
                XY[i, j] = [x, y]
    XY *= 60
    XY[..., 0] += 320 # x
    XY[..., 1] += 280 # y
    return XY

def displayboard_people(you_are_black=False, time_limit=5):
    pygame.init()
    # 设置主屏窗口
    screen = pygame.display.set_mode((640,560))
    # 设置窗口的标题，即游戏名称
    pygame.display.set_caption('HexWuZi')

    screen_color= '#E7B941'
    line_color = '#000000'
    screen.fill(screen_color)
    verts = visual_coordinates()
    all_verts = []

    for i in verts:
        for j in i:
            all_verts.append(j)


    display_board = np.zeros((12, 12), dtype=int)
    display_board[0, 1:] = np.arange(0, 11)
    display_board[1:, 0] = np.arange(0, 11)
    game = Game(you_are_black)
    display_board[1:, 1:] = game.board
    print(display_board)

    tim = 0
    flag=False


    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(screen_color)
        for i in all_verts:
            for j in all_verts:
                if sum((i-j)**2) < 3900:
                    pygame.draw.line(screen,line_color,i,j,2)

        for i in range(len(game.board)):
            for j in range(len(game.board)):
                if game.board[i][j] == 1:
                    pygame.draw.circle(screen, "#000000",all_verts[11*i+j], 18,0)
                    pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
                if game.board[i][j] == -1:
                    pygame.draw.circle(screen, "#FFFFFF",all_verts[11*i+j], 18,0)
                    pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)

        pygame.display.flip()


        # input your position

        
        x,y = pygame.mouse.get_pos()
        maybe_position = all_verts[60]
        for i in all_verts:
            if sum((i-np.array([x,y]))**2) < 500:
                pygame.draw.circle(screen, "#808080",i, 18,1)
                maybe_position = i
        pygame.display.update()


        validflag = False
        keys_pressed = pygame.mouse.get_pressed()
        if keys_pressed[0] and tim==0:
            flag = True
            for i in range(len(verts)):
                for j in range(len(verts[0])):
                    if verts[i,j][0] == maybe_position[0] and verts[i,j][1] == maybe_position[1]:
                        maybe_action = (i,j)
            if game.board[maybe_action[0], maybe_action[1]] == 0:
                action = parse_action(*maybe_action)
                validflag = True

        if flag:
            tim+=1
        if tim%20==0:#延时200ms
            flag=False
            tim=0

        if validflag:
            print(game.player, action)
            game.take_action(action)
            display_board[1:, 1:] = game.board
            print(display_board)
            for i in range(len(game.board)):
                for j in range(len(game.board)):
                    if game.board[i][j] == 1:
                        pygame.draw.circle(screen, "#000000",all_verts[11*i+j], 18,0)
                        pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
                    if game.board[i][j] == -1:
                        pygame.draw.circle(screen, "#FFFFFF",all_verts[11*i+j], 18,0)
                        pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
            pygame.display.update()
            print("AI is searching...")
            pygame.display.set_caption('HexWuZi(AI is searching...)')
            # state = backend.take_action(state, action)
            # winner, gameover = backend.check(game.board)
            # action, detail = backend.search_b(searcher, state, action, need_details=True)
            # state = backend.take_action(state, action)
            # winner, gameover = backend.check(game.board)
            gameover, winner, action = game.play(action)
            pygame.display.set_caption('HexWuZi(Your turn)')
            # print(game.player, action, detail)
            display_board[1:, 1:] = game.board
            print(display_board)
            for i in range(len(game.board)):
                for j in range(len(game.board)):
                    if game.board[i][j] == 1:
                        pygame.draw.circle(screen, "#000000",all_verts[11*i+j], 18,0)
                        pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
                    if game.board[i][j] == -1:
                        pygame.draw.circle(screen, "#FFFFFF",all_verts[11*i+j], 18,0)
                        pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
            pygame.display.update()
            if gameover:
                if winner != 0:
                    print(f"Player({winner}) win!")
                    pygame.display.set_caption(f'HexWuZi(Player[{winner}] win!)')
                else:
                    print("Draw!")
                    pygame.display.set_caption('HexWuZi(Draw!)')
                break

            
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            time.sleep(.1)

# def displayBoard():
#     pygame.init()
#     # 设置主屏窗口
#     screen = pygame.display.set_mode((640,560))
#     # 设置窗口的标题，即游戏名称
#     pygame.display.set_caption('HexWuZi')
#     verts = visual_coordinates()
#     all_verts = []

#     for i in verts:
#         for j in i:
#             all_verts.append(j)

#     screen_color= '#E7B941'
#     line_color = '#000000'
#     screen.fill(screen_color)
#     display_board = np.zeros((12, 12), dtype=int)
#     display_board[0, 1:] = np.arange(0, 11)
#     display_board[1:, 0] = np.arange(0, 11)
#     broad = empty_broad.copy()
#     broad[5, 5] = 1
#     state = backend.HexState(broad, -1)
#     display_board[1:, 1:] = broad
#     print(display_board)
#     searcher = backend.MCTS(time_limit=5)

#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#         screen.fill(screen_color)
#         for i in all_verts:
#             for j in all_verts:
#                 if sum((i-j)**2) < 3900:
#                     pygame.draw.line(screen,line_color,i,j,2)

#         for i in range(len(game.board)):
#             for j in range(len(game.board)):
#                 if game.board[i][j] == 1:
#                     pygame.draw.circle(screen, "#000000",all_verts[11*i+j], 18,0)
#                     pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
#                 if game.board[i][j] == -1:
#                     pygame.draw.circle(screen, "#FFFFFF",all_verts[11*i+j], 18,0)
#                     pygame.draw.circle(screen, "#808080",all_verts[11*i+j], 18,1)
#         pygame.display.flip()

#         currentPlayer = game.player
#         print(f"AI:{currentPlayer} is searching...")
#         pygame.display.set_caption(f'HexWuZi(AI[{currentPlayer}] is searching...)')
#         action, detail = backend.search_b(searcher, state, need_details=True)
#         print(action, detail)
#         state = backend.take_action(state, action)
#         display_board[1:, 1:] = game.board
#         print(display_board)
#         winner, gameover = backend.check(game.board)
#         if gameover:
#             if winner == currentPlayer:
#                 print(f"AI:{currentPlayer} win!")
#                 pygame.display.set_caption(f'HexWuZi(Player[{currentPlayer}] win!)')
#             else:
#                 print("Draw!")
#                 pygame.display.set_caption('HexWuZi(Draw!)')
#             break
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             time.sleep(.1)

# def main(you_are_black=False, opponent_name = None):
#     # if opponent_name == "self":
#     #     displayBoard()        
#     # else:
#     displayboard_people(you_are_black=you_are_black)

parser = ArgumentParser()
parser.add_argument('-b', '--you_are_white',
                    action='store_true')
args = parser.parse_args()
displayboard_people(you_are_black=(not args.you_are_white))




