# python lind.py "{w=F--F--F,F=F+F--F+F}" 1

import argparse
import re
import math
import pygame

__DEBUG__ = False

###########################################################################################
######################## ARGUMENTS ########################################################
###########################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("productions")
parser.add_argument("recursions", type=int)
args = parser.parse_args()




def debug_print(to_print):
    if __DEBUG__:
        print to_print

###########################################################################################
######################## PRINTING FUNCTIONS ###############################################
###########################################################################################

class LindenmayerNode:

    def __init__(self, position, angle):
        self.angle = angle
        self.position = position
        rot = self.rotate()
        self.tips = rot['tips']
        self.feet = rot['feet']
        self.nextPosition = rot['position']

    def getFeet(self):
        result = self.feet
        return result

    def getTips(self):
        result = self.tips
        return result

    def getPosition(self):
        result = self.position
        return result

    def getNextPosition(self):
        result = self.nextPosition
        return result

    def getAngle(self):
        result = self.angle
        return result

    def rotate(self):
        angle = self.angle #(self.angle - rotationAngle) % 360
        position = self.position
        debug_print (("rotate by ", angle))
        return self.calc_positions()
    ### fed rotate

    def calc_positions(self):
        rad = self.angle * math.pi / 180
        cos_angle = math.cos(rad)
        sin_angle = math.sin(rad)
        debug_print (("got position %s", str(self.position)))
        return  {
            'position' : ( self.position[0] - (start_metrics[1] * sin_angle)   # x Koordinate der Rotation ist immer 0
                         , self.position[1] + (start_metrics[1] * cos_angle)), # x Koordinate der Rotation ist immer 0
            'tips' : [
                (   self.position[0] + (start_metrics[0] / -2) * cos_angle - start_metrics[1] * sin_angle,
                    self.position[1] + start_metrics[1] * cos_angle + (start_metrics[0] / -2) * sin_angle ),
                (   self.position[0] + (start_metrics[0] /  2) * cos_angle - start_metrics[1] * sin_angle,
                    self.position[1] + start_metrics[1] * cos_angle + (start_metrics[0] /  2) * sin_angle ),
            ],
            'feet' : [
                (   self.position[0] + (start_metrics[0] /  2) * cos_angle - 0 * sin_angle,
                    self.position[1] + 0 * cos_angle + (start_metrics[0] /  2) * sin_angle ),
                (   self.position[0] + (start_metrics[0] / -2) * cos_angle - 0 * sin_angle,
                    self.position[1] + 0 * cos_angle + (start_metrics[0] / -2) * sin_angle ),
            ],
        }
    #fed calc_positions


class LindenmayerTree:
    ''' Klasse zum Erzeugen eines Lindenmayer Baums '''

    def __init__(self, rules, position, angle, rotAngle, recursions):
        self.productions = self.parse_productions(re.findall('\w=[+A-Z-]+', args.productions))
        self.position = position
        self.angle = angle
        self.rotAngle = rotAngle
        self.recursions = recursions
        self.nodes = []

    def parse_productions(self, productions_input):
        # associative array for production rules
        productions = {}
        # parse all given production rules
        for p in productions_input:
            # split every string of rules at "="
            # resulting array:
            # [0] = name of variable
            # [1] = rule
            p = p.split("=")
            productions[p[0]] = []
            for c in p[1]:
                productions[p[0]].append(c)
        return productions
    # fed parse_productions

    def variable(self, angle, position, symbol, n):
        if ((n >= 0) and (symbol in self.productions)):
            for p in self.productions[symbol]:
                if (p == '-') or (p == '+'):
                    if (p == '-'):
                        angle -= self.rotAngle
                    if (p == '+'):
                        angle += self.rotAngle
                    angle %= 360
                    node = LindenmayerNode(position, angle)
                    self.nodes.append(node)
                    position = node.getNextPosition()
                else: # variable
                    self.variable(angle, position, p, n-1)
                    if len(self.nodes) > 0:
                        angle = self.nodes[-1].getAngle()
                        position = self.nodes[-1].getNextPosition()
    ### fed variable

    def calcTree(self):
        self.variable(self.angle, (0,0), 'w', self.recursions)
    # fed calcTree

    def toPolygon(self, position=False, zoom=1):
        if not position:
            position = self.position
        start = [(position[0] - start_metrics[0] / 2, position[1])]
        end = [(position[0] + start_metrics[0] / 2, position[1])]
        polygon_head = start
        polygon_tail = end
        for p in self.nodes:
            c_tips = [[p.tips[0][0],p.tips[0][1]],[p.tips[1][0], p.tips[1][1]]]
            c_tips[0][0] = c_tips[0][0] * zoom
            c_tips[0][1] = c_tips[0][1] * zoom
            c_tips[1][0] = c_tips[1][0] * zoom
            c_tips[1][1] = c_tips[1][1] * zoom
            polygon_head.append([c_tips[0][0] + position[0], c_tips[0][1] + position[1]])
            polygon_tail.append([c_tips[1][0] + position[0], c_tips[1][1] + position[1]])
        polygon_tail.reverse()
        return polygon_head + polygon_tail

############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class



###########################################################################################
######################## MAIN #############################################################
###########################################################################################

#debug
colorcnt = 7
colors = [
    (255,255,255),
    (255,255,0),
    (255,0,0),
    (0,255,0),
    (0,0,255),
    (255,0,255),
    (0,255,255),
]

screen_metrics = (800, 600)
start_point = [screen_metrics[0] / 6, screen_metrics[1] / 3]
start_metrics = (2, 3)

rotationAngle = 60
start_angle = 0


# calculate tree
angle = start_angle

ltree = LindenmayerTree(
    args.productions, 
    start_point, 
    start_angle, 
    rotationAngle, 
    args.recursions) #rules, position, angle, rotAngle, recursions
ltree.calcTree()
#polygon = ltree.toPolygon()


### Init Pygame
pygame.init()
pygame.display.set_caption("Lindenmayer-Systems")
screen = pygame.display.set_mode(screen_metrics)
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()


### the loop
running = True
top = 0
position = start_point
zoom = 1.0
recalc = True
#counter = 1
while running:
    clock.tick(30)
    screen.fill((0,0,0))

    if recalc:
        polygon = ltree.toPolygon(position, zoom)
        recalc = False
    pygame.draw.polygon(screen, (0,255,0), polygon)
    pygame.display.update()

    for event in pygame.event.get():
        # Spiel beenden, wenn wir ein QUIT-Event finden.
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                running = False  
            if event.key == pygame.K_UP:
                position[1] = position[1] - 1
            if event.key == pygame.K_DOWN:
                position[1] = position[1] + 1
            if event.key == pygame.K_LEFT:
                position[0] = position[0] - 1
            if event.key == pygame.K_RIGHT:
                position[0] = position[0] + 1
            if event.key == pygame.K_F1:
                zoom -= 0.05
            if event.key == pygame.K_F2:
                zoom += 0.05
        recalc = True            

# raw_input("Press Enter to terminate.")

