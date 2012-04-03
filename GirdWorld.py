"""

So far, we has histogram localisation implemented, and it seems to work OK.
There is no planning, or recognition of obstactles

Next:   Prove that localisation is working

        Kalman localisation (if possible in discrete world)
        Particle Filters
        A* and Dynamic Programming (obstactle recognition)

        Move away from colors and use wall range finding

        Smoothing (if possible in discrete world)
        PID Controller (ditto)

        Add continuous world for robot motion, but use discrete world as planning
            and localisation environment
        Landmarks in continuous space
"""



# Import the wxPython GUI library
import wx
import random

def printLists(l):
    for e in l:
        print e

class robot:
    def __init__(self, world, color, randomInit=0):
        self.x = 0
        self.y = 0
        self.facing = 0     # 0-3 = North, East, South, West
        self.moveProb = 0.9 # Chance we move correctly
        self.measurementNoise = 0.1 # Chance our measurement is wrong

        self.world = world
        self.worldX = len(world)
        self.worldY = len(world[0])

        self.color = color

        if randomInit:
            self.x = random.choice(range(self.worldX))
            self.y = random.choice(range(self.worldY))

        P = 1.0/(self.worldX * self.worldY)
        self.belief = [ [P for _ in range(self.worldY)] for _ in range(self.worldX) ]

    def setLocation(self, newX, newY, newFacing):
        if newX < 0 or newX >= worldX:
            raise ValueError, 'X Coordiate out of bound'
        if newY < 0 or newY >= worldY:
            raise ValueError, 'Y Coordiate out of bound'
        if newFacing not in [0, 1, 2, 3]:
            raise ValueError, 'Facing must be one of [0, 1, 2, 3]'

        self.x = newX
        self.y = newY
        self.facing = newFacing

    # We are wrong some percentage of the time
    # and so we return a random element from the color list
    def sense(self):
        if random.random() < (1.0 - self.measurementNoise):
            measurement = world[self.x][self.y][1]
        else:
            wrong = []
            for c in self.color:
                if c != world[self.x][self.y][1]:
                    wrong.append(c)
            measurement =  random.choice(wrong)

        q = []
        for x in range(self.worldX):
            tmp = []
            for y in range(self.worldY):
                hit = (world[x][y][1] == measurement)
                tmp.append( self.belief[x][y]*(1.0-self.measurementNoise)*hit +
                            self.belief[x][y]*self.measurementNoise*(1-hit) )
            q.append(tmp)

        sumQ = 0.0        
        for row in q:
            sumQ += sum(row)

        for x in range(self.worldX):
            for y in range(self.worldY):
                self.belief[x][y] = q[x][y]/sumQ

        return measurement

    def moveForward(self):        
        dX = 0
        dY = 0
        if random.random() > (1.0 - self.moveProb): 
            if self.facing == 0:    # North
                self.x = (self.x - 1)%self.worldX
            if self.facing == 1:    # East
                self.y = (self.y + 1)%self.worldY
            if self.facing == 2:    # South
                self.x = (self.x + 1)%self.worldX
            if self.facing == 3:    # West
                self.y = (self.y - 1)%self.worldY

        if self.facing == 0:    # North
            dX = -1
        if self.facing == 1:    # East
            dY = 1
        if self.facing == 2:    # South
            dX = 1
        if self.facing == 3:    # West
            dY = -1

        q = []
        for x in range(self.worldX):
            tmp = []
            for y in range(self.worldY):
                tmp.append( self.belief[x][y] * (1.0 - self.moveProb) +
                            self.belief[(x-dX)%self.worldX][(y-dY)%self.worldY] * self.moveProb )
            q.append(tmp)
            
        for x in range(self.worldX):
            for y in range(self.worldY):
                self.belief[x][y] = q[x][y]
                

    def turnLeft(self):
        self.facing = (self.facing - 1)%4

    def turnRight(self):
        self.facing = (self.facing + 1)%4

    def bestBelief(self):
        bestX = 0
        bestY = 0
        bestB = 0.0

        for x in range(self.worldX):
            for y in range(self.worldY):
                if self.belief[x][y] > bestB:
                    bestX = x
                    bestY = y
                    bestB = self.belief[x][y]
        return bestX, bestY, bestB
        

class WorldFrame(wx.Frame):
    def __init__(self, parent, title, sizeX, sizeY):
        wx.Frame.__init__(self, parent, title=title)
        self.SetSize((sizeX, sizeY))
        self.Centre()

        self.Show(True)

    def drawLine(self, sX, sY, eX, eY):
        dc = wx.ClientDC(self)
        #dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        dc.DrawLine(sX, sY, eX, eY)

# Grid of data items, made up of ["passability", "measurement"]
world = [
    [[0, 'Red'], [0, 'Blue'], [0, 'Yellow'], [0, 'Green'], [0, 'Blue']],
    [[0, 'Blue'], [0, 'Yellow'], [0, 'Green'], [0, 'Red'], [0, 'Black']],
    [[0, 'Black'], [0, 'Red'], [0, 'Black'], [0, 'Blue'], [0, 'Black']],
    [[0, 'Blue'], [0, 'Blue'], [0, 'Red'], [0, 'Green'], [0, 'Black']],
    [[0, 'Yellow'], [0, 'Blue'], [0, 'Yellow'], [0, 'Green'], [0, 'Black']]
        ]

# These are the possible measurements.
color = ['Red', 'Green', 'Blue', 'Yellow', 'Black']

# Replace this with a wxPythton GUI
def showWorld(w):
    dimX = len(w)
    dimY = len(w[0])
    for x in range(dimX):
        line = ""
        for y in range(dimY):
            line += str(w[x][y][0]) + ":" + str(w[x][y][1]) + "  "
        print line

## TODO : Unimplemented
def showWorldGUI(w):
    gridScale = 100
    padding = 50
    
    dimX = len(w)
    dimY = len(w[0])
    
    app = wx.App(False)
    frame = WorldFrame(None, "Grid World", 2*padding + dimX*gridScale, 2*padding + dimY*gridScale)

    for x in range(dimX+1):
        print "Drawing line"
        frame.drawLine(padding, padding + x*gridScale, dimY*gridScale, padding + x*gridScale)

    app.MainLoop()
    



#for i in range(25):
#    car = robot(world, color, randomInit=1)
#    print "X = " + str(car.x) + ", Y = " + str(car.y)
"""
right = 0
wrong = 0
for _ in range(100):
    car = robot(world, color, randomInit=1)
    car.sense()
    i = 0
    while car.bestBelief()[2] < 0.6 and i < 5000:
        car.moveForward()
        car.sense()
        car.turnRight()
        car.moveForward()
        car.sense()
        car.turnLeft()
        i += 1

    #printLists(car.belief)
    #print i

    if [car.x, car.y] == [car.bestBelief()[0], car.bestBelief()[1]]:
        right += 1
    else:
        wrong +=1
        print " ---- "
        print car.x, car.y, i
        print car.bestBelief()[0], car.bestBelief()[1]
        print " --- "
    print right, wrong
"""

car = robot(world, color, randomInit=1)
for _ in range(10):
    print [car.x, car.y] == [car.bestBelief()[0], car.bestBelief()[1]], car.bestBelief()[2]
    car.moveForward()
    car.sense()
    car.turnRight()
    car.moveForward()
    car.sense()
    car.turnLeft()
    car.moveForward()
    car.sense()
    

#printLists(car.belief)


#showWorld(world)
#showWorldGUI(world)
