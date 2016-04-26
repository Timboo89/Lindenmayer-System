'''
neues Vorgehen:
1) Eingabeparameter festlegen
    - Iterationen (n)
    - Winkel (a)
    - (Start-)Axiom
    - Regeln
2) n mal Variablen in Axiom ersetzen
3) Pfad Berechnen
    - Startwinkeln 180 Grad
    - bei - +a
    - bei + -a
    - bei Variable: Zeichne Strich in Richtung aktuellem Winkel
    - [] Ast. Bei finden von [ oeffne Ast mit 

Weiter:
- Szene bewegen
- Fuege Farbcodes hinzu
- Ersetze Striche durch Rechtecke/Polygone
'''


import argparse
import re
import math
import random
import pygame

###########################################################################################
######################## ARGUMENTS ########################################################
###########################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("-prod", "--productions")
parser.add_argument("-ax", "--axiom")
parser.add_argument("-a", "--angle", type=int)
parser.add_argument("-s", "--startangle", type=int)
parser.add_argument("-rec", "--recursions", type=int)
parser.add_argument("-d", "--distance", type=int)
parser.add_argument("-e", "--example")
parser.add_argument("-g", "--growing", action="store_true", help="shows each step of growing tree - doesn't work properly with randomangle")
parser.add_argument("--shrink", action="store_true")
parser.add_argument("-w", "--width", type=int, help="added width at the root of tree")
parser.add_argument("-r", "--randomangle", type=int, help="maximum addad angle per iteration - doesn't work properly with growing")
args = parser.parse_args()

# examples
example = {
    'cross' : {
        'productions'    : "{F=F+F--F+F}",
        'axiom'          : "F--F--F",
        'angle'          : 90,
        'recursions'     : 6,
        'start_angle'    : 180,
        'start_position' : [400,650],
        'metrics'        : [800,650],
        'distance'       : 10
    },
    'Joined Cross Curves' : {
        'productions'    : "{F=,X=FX+FX+FXFY-FY-,Y=+FX+FXFY-FY-FY}",
        'axiom'          : "XYXYXYX+XYXYXYX+XYXYXYX+XYXYXYX",
        'angle'          : 90,
        'recursions'     : 3,
        'start_angle'    : 180,
        'start_position' : [530,630],
        'metrics'        : [700,700],
        'distance'       : 3
    },
    'Lace' : {
        'productions'    : "{W=+++X--F--ZFX+,X=---W++F++YFW-,Y=+ZFX--F--Z+++,Z=-YFW++F++Y---}",
        'axiom'          : "W",
        'angle'          : 30,
        'recursions'     : 6,
        'start_angle'    : 180,
        'start_position' : [300,550],
        'metrics'        : [310,550],
        'distance'       : 6
    },
    'Sierpinski Median Curve' : {
        'productions'    : "{L=+R-F-R+,R=-L+F+L-}",
        'axiom'          : "L--F--L--F",
        'angle'          : 45,
        'recursions'     : 8,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 10
    },
    'Space Filling Curve' : {
        'productions'    : "{X=-YF+XFX+FY-,Y=+XF-YFY-FX+}",
        'axiom'          : "X",
        'angle'          : 90,
        'recursions'     : 8,
        'start_angle'    : 180,
        'start_position' : [0,600],
        'metrics'        : [800,600],
        'distance'       : 2
    },
    'Sierpinski Carpet' : {
        'productions'    : "{F=F+F-F-F-G+F+F+F-F,G=GGG}",
        'axiom'          : "F",
        'angle'          : 90,
        'recursions'     : 4,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 7
    },
    'Koch Snowflake' : {
        'productions'    : "{F=F-F++F-F,X=FF}",
        'axiom'          : "F++F++F",
        'angle'          : 60,
        'recursions'     : 4,
        'start_angle'    : 180,
        'start_position' : [550,580],
        'metrics'        : [800,600],
        'distance'       : 7
    },
    'Pleasant Error' : {
        'productions'    : "{F=F-F++F+F-F-F}",
        'axiom'          : "F-F-F-F-F",
        'angle'          : 72,
        'recursions'     : 4,
        'start_angle'    : 180,
        'start_position' : [625,300],
        'metrics'        : [800,600],
        'distance'       : 6
    },
    'Dragon Curve' : {
        'productions'    : "{X=X+YF,Y=FX-Y}",
        'axiom'          : "FX",
        'angle'          : 90,
        'recursions'     : 10,
        'start_angle'    : 180,
        'start_position' : [550,350],
        'metrics'        : [800,600],
        'distance'       : 6
    },
    'Sierpinski Triangle 1' : {
        'productions'    : "{F=F-G+F+G-F,G=GG}",
        'axiom'          : "F-G-G",
        'angle'          : 120,
        'recursions'     : 6,
        'start_angle'    : 180,
        'start_position' : [200,600],
        'metrics'        : [800,600],
        'distance'       : 9
    },
    'Sierpinski Triangle 2' : {
        'productions'    : "{A=B-A-B,B=A+B+A}",
        'axiom'          : "A",
        'angle'          : 60,
        'recursions'     : 7,
        'start_angle'    : 180,
        'start_position' : [200,600],
        'metrics'        : [800,600],
        'distance'       : 4
    },
    'Koch Curve' : {
        'productions'    : "{F=F+F-F-F+F}",
        'axiom'          : "-F",
        'angle'          : 90,
        'recursions'     : 4,
        'start_angle'    : 180,
        'start_position' : [35,590],
        'metrics'        : [800,600],
        'distance'       : 9
    },
    'Fractal Plant' : {
        'productions'    : "{X=(140,80,60)F-[(48,220,48)[X]+(64,255,64)X]+(24,180,24)F[(64,255,64)+FX]-X,F=FF}",
        'axiom'          : "X",
        'angle'          : 25,
        'recursions'     : 6,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 3
    },
    'Pond Weed' : {
        'productions'    : "{F=(140,80,60)FF[(24,180,24)-F++F][(48,220,48)+F--F](64,255,64)++F--F}",
        'axiom'          : "F",
        'angle'          : 27,
        'recursions'     : 5,
        'start_angle'    : 180,
        'start_position' : [780,600],
        'metrics'        : [800,600],
        'distance'       : 1
    },
    'Wispy Tree' : {
        'productions'    : "{F=(140,80,60)FF-[(24,180,24)-F+F]+[(48,220,48)+F-F],X=(140,80,60)FF+[(24,180,24)+F]+[(64,255,64)-F]}",
        'axiom'          : "FX",
        'angle'          : 25,
        'recursions'     : 5,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 5
    },
    'Tree' : {
        'productions'    : "{F={3,7}(140,80,60)FF-[{3,4}(24,180,24)-F+F+F]+[{2,2}(48,220,48)+F-F-F]}",
        'axiom'          : "F",
        'angle'          : 22,
        'recursions'     : 5,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 5
    },
    'Random Tree' : {
        'productions'    : "{F={5,7}(140,80,60)FF-[{3,4}(24,180,24)-F+F+F]+[{2,2}(48,220,48)+F-F-F]}",
        'axiom'          : "F",
        'angle'          : 22,
        'recursions'     : 5,
        'start_angle'    : 180,
        'start_position' : [400,600],
        'metrics'        : [800,600],
        'distance'       : 5,
        'randomangle'    : 10
    },
    'Highway Dragon' : {
        'productions'    : "{X=X+YF+,Y=-FX-Y}",
        'axiom'          : "FX",
        'angle'          : 90,
        'recursions'     : 12,
        'start_angle'    : 180,
        'start_position' : [400,150],
        'metrics'        : [800,600],
        'distance'       : 3
    }
}

# Default Values
settings = example['Tree']

if args.example:
    if args.example in example:
        settings = example[args.example]
    else:
        print "Das Beispiel -", args.example, "- existiert nicht!"
        exit()

if args.productions:
    settings['productions'] = args.productions
if args.axiom != None:
    settings['axiom'] = args.axiom
if args.angle != None:
    settings['angle'] = args.angle
if args.recursions != None:
    settings['recursions'] = args.recursions
if args.startangle != None:
    settings['start_angle'] = args.startangle
if args.distance != None:
    settings['distance'] = args.distance
if args.width != None:
    settings['width'] = args.width
else:
    settings['width'] = 0
if args.randomangle != None:
    settings['randomangle'] = args.randomangle
elif 'randomangle' not in settings:
    settings['randomangle'] = 0.0
settings['growing'] = args.growing
settings['shrink'] = args.shrink

###########################################################################################
################################# FUNCTIONS ###############################################
###########################################################################################

def radAngle(angle):
    return angle * math.pi / 180

def parse_productions(productions_input):
    # associative array for production rules
    #regexp = re.compile(ur'(\w=((\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3}\))?[+A-Z-\[\]]*)*)') 
    regexp = re.compile(ur'(\w=((\{[0-9]{1,2}(,[0-9]{1,2})?\})?(\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3}\))?[+A-Z-\[\]]*)*)') 
    productions_input = re.findall(regexp, productions_input)
    productions = {}
    # parse all given production rules
    for p in productions_input:
        # split every string of rules at "="
        # resulting array:
        # [0] = name of variable
        # [1] = rule
        p = p[0]
        p = p.split("=")
        productions[p[0]] = p[1]
    return productions
# fed parse_productions

def iterate_axiom(axiom, productions, iterations=1):
    result = axiom
    for i in range(0,iterations):
        result = ''
        for a in axiom:
            if a in productions:
                result += productions[a]
            else:
                result += a
        axiom = result
    return result

# s = settings
def draw(surface, word, offset, s):
    width = s['width']
    shrinked = 0
    bracketstack = []
    n = 0
    angle = s['start_angle']
    position = offset
    distance = s['distance']
    color = [200,200,200]
    while n < len(word):
        c = word[n]
        if   c == '+' or c == '-':
            if c == '+':
                angle -= s['angle']
            else:
                angle += s['angle']
            angle %= 360
        elif c == '[':
            bracketstack.append({
                'angle' : angle,
                'position' : position,
                'color' : color,
                'width' : width,
                'distance' : distance
                })
            shrinked += 1
        elif c == ']':
            pop = bracketstack.pop()
            angle = pop['angle']
            position = pop['position']
            color = pop['color']
            shrinked -= 1
        #expect color
        elif c == '(':
            colorcode = word[n+1:]
            endofcolor = colorcode.find(')')
            colorcode = colorcode[0:endofcolor]
            color = colorcode.split(',')
            color[0],color[1],color[2] = int(color[0]),int(color[1]),int(color[2])
            n += endofcolor+1
        # expect {width, length} or {width}
        elif c == '{':
            tmp = word[n+1:]
            endofwidth = tmp.find('}')
            tmp = tmp[0:endofwidth]
            tmp = tmp.split(',')
            if len(tmp) > 1:
                distance = int(tmp[1])
            width = int(tmp[0])
            n += endofwidth+1
        else:
            old_position = position[:]
            angle += int(s['randomangle'] * random.uniform(-1.0,1.0))
            rad = radAngle(angle)
            cos_angle = math.cos(rad)
            sin_angle = math.sin(rad)
            position = [old_position[0] - (distance * sin_angle)   # x Koordinate der Rotation ist immer 0
                       ,old_position[1] + (distance * cos_angle)]
            cur_width = width
            if s['shrink']:
                cur_width -= shrinked
            if cur_width > 0:
                pygame.draw.line(surface, color, old_position, position, cur_width)
            else:
                pygame.draw.line(surface, color, old_position, position, 1)
        n+=1

### Init Pygame
pygame.init()
pygame.display.set_caption("Lindenmayer-Systems")
screen = pygame.display.set_mode(settings['metrics'])
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()


parsed_prods = parse_productions(settings['productions'])
if settings['growing']:
    word = settings['axiom']
else:
    word = iterate_axiom(
            settings['axiom'], 
            parsed_prods, 
            settings['recursions'])
    screen.fill((0,0,0))
    draw(screen, word, settings['start_position'], settings)
    pygame.display.update()

### the loop
running = True
grown = 0
#counter = 1
while running:
    clock.tick(1)

    #eigentlich hier zeichnen
    if settings['growing'] and grown <= settings['recursions']:
        screen.fill((0,0,0))
        draw(screen, word, settings['start_position'], settings)
        pygame.display.update()
        if grown <= settings['recursions']:
            word = iterate_axiom(word, parsed_prods)
            grown += 1

    for event in pygame.event.get():
        # Spiel beenden, wenn wir ein QUIT-Event finden.
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                running = False  

