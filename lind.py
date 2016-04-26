# Simple Lindenmayer System Interpreter
# author: Timo Schmidt
# date: 26.04.2016

# Main Program starts at line 431

import argparse
import re
import math
import random
import pygame

###########################################################################################
######################## ARGUMENTS ########################################################
###########################################################################################

def coords(s):
    try:
        x, y= map(int, s.split(','))
        return [x, y]
    except:
        raise argparse.ArgumentTypeError("Coordinates must be x,y")

parser = argparse.ArgumentParser(description='test', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--coord', help="Coordinate to start drawing", type=coords)
parser.add_argument('--metrics', help="Screensize", type=coords)

parser.add_argument("-prod", "--productions", 
    help="in syntax of {F=F+G,G=--F}\n"
    "+       - turn anti-clockwise\n"
    "-       - turn clockwise\n"
    "{w,d}   - w : width at that part of the L-System\n"
    "        - d : length of each branch at that part of the L-System\n"
    "(r,g,b) - colorcode, to encolor that part of the L-System\n"
    "[...]   - [ : open a new branch\n"
    "        - ] : close the current branch\n"
    )
parser.add_argument("-ax", "--axiom", help="in syntax of F--G+F (see productions)")
parser.add_argument("-a", "--angle", type=int, help="angle each +anti-clockwise -clockwise turn, the tree takes")
parser.add_argument("-s", "--startangle", type=int, help="angle to start tree")
parser.add_argument("-rec", "--recursions", type=int, help="number of recursive replacements of rules in axiom")
parser.add_argument("-d", "--distance", type=int, help="standard length of a branch (if not given otherwise in production)")
parser.add_argument("-g", "--growing", action="store_true", help="shows each step of growing tree - doesn't work properly with randomangle")
parser.add_argument("--shrink", action="store_true", help="lets shrink width of each deeper branch")
parser.add_argument("-w", "--width", type=int, help="added width at the root of tree (if not given otherwise in production)")
parser.add_argument("-r", "--randomangle", type=int, help="maximum addad angle per iteration - doesn't work properly with growing")
parser.add_argument("-e", "--example", 
    help="Pick one of various example L-Systems. \n"
    "Examples are: \n"
    "- cross\n"
    "- Joined Cross Curves\n"
    "- Lace\n"
    "- Sierpinski Median Curve\n"
    "- Space Filling Curve\n"
    "- Sierpinski Carpet\n"
    "- Koch Snowflake\n"
    "- Pleasant Error\n"
    "- Dragon Curve\n"
    "- Sierpinski Triangle 1\n"
    "- Sierpinski Triangle 2\n"
    "- Koch Curve\n"
    "- Fractal Plant\n"
    "- Pond Weed\n"
    "- Wispy Tree\n"
    "- Tree (default)\n"
    "- Highway Dragon"
    )
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
    settings['width'] = 1
if args.randomangle != None:
    settings['randomangle'] = args.randomangle
elif 'randomangle' not in settings:
    settings['randomangle'] = 0
if args.metrics != None:
    settings['metrics'] = args.metrics
elif 'metrics' not in settings:
    settings['metrics'] = [800,600]
if args.coord != None:
    settings['start_position'] = args.coord
elif 'start_position' not in settings:
    settings['start_position'] = [settings['metrics'][0]/2,settings['metrics'][1]]
settings['growing'] = args.growing
settings['shrink'] = args.shrink

###########################################################################################
################################# FUNCTIONS ###############################################
###########################################################################################

# calculate the radiant of an angle
def radAngle(angle):
    return angle * math.pi / 180

# create an array of a string of production rules
def parse_productions(productions_input):
    # associative array for production rules
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
# end def parse_productions

# iterate the given axiom with productions at least once
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
# end def iterate axiom

# surface = surface to draw on
# word = word to draw
# offset = where to start drawing
# s = settings
# Note: if randomangle is set, each use of draw will create a different tree
def draw(surface, word, offset, s):
    # width to start drawing at root
    width = s['width']
    # number of entered branches (to shrink width of the tree)
    shrinked = 0
    # stack to store settings before entering a new branch
    bracketstack = []
    # current position in tree-word
    n = 0
    # current angle to draw
    angle = s['start_angle']
    # current position to draw
    position = offset
    # current length of branch to draw
    distance = s['distance']
    # standard / current color to draw with
    color = [200,200,200]
    # go through every step of word
    while n < len(word):
        # current sign of word
        c = word[n]
        # just turn the angle
        if   c == '+' or c == '-':
            if c == '+':
                angle -= s['angle']
            else:
                angle += s['angle']
            angle %= 360
        # create new branch
        elif c == '[':
            bracketstack.append({
                'angle' : angle,
                'position' : position,
                'color' : color,
                'width' : width,
                'distance' : distance
                })
            shrinked += 1
        # return to point, where branch was created
        elif c == ']':
            pop = bracketstack.pop()
            angle = pop['angle']
            position = pop['position']
            color = pop['color']
            shrinked -= 1
        # change color to draw with
        elif c == '(':
            colorcode = word[n+1:]
            endofcolor = colorcode.find(')')
            colorcode = colorcode[0:endofcolor]
            color = colorcode.split(',')
            color[0],color[1],color[2] = int(color[0]),int(color[1]),int(color[2])
            n += endofcolor+1
        # change width and length {width, length} or {width}
        elif c == '{':
            tmp = word[n+1:]
            endofwidth = tmp.find('}')
            tmp = tmp[0:endofwidth]
            tmp = tmp.split(',')
            if len(tmp) > 1:
                distance = int(tmp[1])
            width = int(tmp[0])
            n += endofwidth+1
        # actually draw a branch
        else:
            # copy old position
            old_position = position[:]
            # add some randomness to current angle
            angle += int(s['randomangle'] * random.uniform(-1.0,1.0))
            # radiant of current angle
            rad = radAngle(angle)
            # calculate new position
            cos_angle = math.cos(rad)
            sin_angle = math.sin(rad)
            position = [old_position[0] - (distance * sin_angle)   # x Koordinate der Rotation ist immer 0
                       ,old_position[1] + (distance * cos_angle)]
            # get current width to draw with
            cur_width = width
            if s['shrink']:
                cur_width -= shrinked
            # draw branch 
            if cur_width > 0:
                pygame.draw.line(surface, color, old_position, position, cur_width)
            else:
                pygame.draw.line(surface, color, old_position, position, 1)
        n+=1
    # end while
# end def draw


###########################################################################################
############################# MAIN ########################################################
###########################################################################################

### Init Pygame
pygame.init()
pygame.display.set_caption("Lindenmayer-Systems")
screen = pygame.display.set_mode(settings['metrics'])
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()

# create a list of production rules
parsed_prods = parse_productions(settings['productions'])
# if growing is active, set start axiom as currently created word
if settings['growing']:
    word = settings['axiom']
else:
    # otherwise calculate the actual word after n iterations
    word = iterate_axiom(
            settings['axiom'], 
            parsed_prods, 
            settings['recursions'])
    # draw word as a tree on screen only once
    screen.fill((0,0,0))
    draw(screen, word, settings['start_position'], settings)
    pygame.display.update()

### the loop
running = True
grown = 0
# run program as long as the user didn't press ESC
while running:
    clock.tick(1)

    # if the tree is supposed to grow:
    if settings['growing'] and grown <= settings['recursions']:
        screen.fill((0,0,0))
        # draw current tree
        draw(screen, word, settings['start_position'], settings)
        pygame.display.update()
        # if maximum growth of tree isn't achieved yet:
        if grown <= settings['recursions']:
            # calculate next iteration of tree / word
            word = iterate_axiom(word, parsed_prods)
            grown += 1

    for event in pygame.event.get():
        # Spiel beenden, wenn wir ein QUIT-Event finden.
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                running = False  

