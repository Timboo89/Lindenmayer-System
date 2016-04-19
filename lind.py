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

def parse_productions(productions_input):
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


def debug_print(to_print):
    if __DEBUG__:
        print to_print

###########################################################################################
######################## PRINTING FUNCTIONS ###############################################
###########################################################################################

class LindenmayerTree:
    ''' Klasse zum Erzeugen eines Lindenmayer Baums '''

    def __init__(self, position):
        self.position = position

    def variable(self, data, n):
        angles = []
        angle = data['angle']
        position = data['position']
        var = data['production_symbol']
        if ((n > 0) and (var in productions)):
            for p in productions[var]:
                result = get_print_function(p)({'angle':angle,'position':position,'production_symbol':p}, n-1)
                if 'nothing' not in result:
                    if 'result' in result:
                        angle = result['result'][-1]['angle']
                        position = result['result'][-1]['position']
                        angles.extend(result['result'])
                    else: # if 'angle' in result
                        angle = result['angle']
                        position = result['position']
                        angles.append(result)
                # fi 'nothing' not in result
            # for p in productions[var]
        else:
            return {'nothing' : 0}
        return { 'result' : angles }
    ### fed variable

    def rotate_left(self, data, n=0):
        angle = (data['angle'] - rotationAngle) % 360
        position = data['position']
        debug_print (("left: rotate by ", angle))
        return calc_positions(angle, position)

    ### fed rotate_left

    def rotate_right(self, data, n=0):
        angle = (data['angle'] + rotationAngle) % 360
        position = data['position']
        debug_print (("right: rotate by %s", angle))
        return calc_positions(angle, position)
    ### fed rotate_right

    def calc_positions(self, angle, position):
        rad = angle * math.pi / 180
        cos_angle = math.cos(rad)
        sin_angle = math.sin(rad)
        debug_print (("got position %s", str(position)))
        return  {
            'angle' : angle,
            'position' : ( position[0] - (start_metrics[1] * sin_angle)   # x Koordinate der Rotation ist immer 0
                         , position[1] + (start_metrics[1] * cos_angle)), # x Koordinate der Rotation ist immer 0
            'tips' : [
                (   position[0] + (start_metrics[0] / -2) * cos_angle - start_metrics[1] * sin_angle,
                    position[1] + start_metrics[1] * cos_angle + (start_metrics[0] / -2) * sin_angle ),
                (   position[0] + (start_metrics[0] /  2) * cos_angle - start_metrics[1] * sin_angle,
                    position[1] + start_metrics[1] * cos_angle + (start_metrics[0] /  2) * sin_angle ),
            ],
            'feet' : [
                (   position[0] + (start_metrics[0] /  2) * cos_angle - 0 * sin_angle,
                    position[1] + 0 * cos_angle + (start_metrics[0] /  2) * sin_angle ),
                (   position[0] + (start_metrics[0] / -2) * cos_angle - 0 * sin_angle,
                    position[1] + 0 * cos_angle + (start_metrics[0] / -2) * sin_angle ),
            ],
        }
    #fed calc_positions

    def get_print_function(self, c):
        functions = {
            '-' : rotate_left,
            '+' : rotate_right,
        }
        if c in functions:
            return functions[c]
        return variable
    #fed get_print_function

############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class
############################################## End of Class

def toPolygon(positions):
    start = [(start_point[0] - start_metrics[0] / 2, start_point[1])]
    end = [(start_point[0] + start_metrics[0] / 2, start_point[1])]
    polygon_head = start
    polygon_tail = end
    for p in positions:
        polygon_head.append(p['tips'][0])
        polygon_tail.append(p['tips'][1])
    polygon_tail.reverse()
    return polygon_head + polygon_tail

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
start_point = (screen_metrics[0] / 6, screen_metrics[1] / 6)
start_metrics = (5, 10)

rotationAngle = 60
start_angle = 0

productions = parse_productions(re.findall('\w=[+A-Z-]+', args.productions))

# calculate tree
angle = start_angle
positions = []
position = (start_point[0] - (start_metrics[0] / 2), start_point[1] - start_metrics[1])
for p in productions['w']:
    result = get_print_function(p)({'angle':angle,'position':position,'production_symbol':p}, args.recursions)
    if 'nothing' not in result:
        if 'result' in result:
            angle = result['result'][-1]['angle']
            position = result['result'][-1]['position']
            positions.extend(result['result'])
        else:
            angle = result['angle']
            position = result['position']
            positions.append(result)

polygon = toPolygon(positions)


### Init Pygame
pygame.init()
pygame.display.set_caption("Lindenmayer-Systems")
screen = pygame.display.set_mode(screen_metrics)
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()


### the loop
running = 1
top = 0
#counter = 1
while running:
    clock.tick(30)
    screen.fill((0,0,0))

    tree = pygame.draw.polygon(screen, (0,255,0), polygon)
    tree.move(7,0)
    pygame.display.update()

    for event in pygame.event.get():
        # Spiel beenden, wenn wir ein QUIT-Event finden.
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  
        #elif event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
        #    counter += 1            

# raw_input("Press Enter to terminate.")

