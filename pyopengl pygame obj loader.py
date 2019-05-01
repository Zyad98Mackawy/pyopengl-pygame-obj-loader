
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame

# screen resolution
from ctypes import windll, Structure, c_long, byref
user32 = ctypes.windll.user32                                      #######
res = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]     #######

def MTL(filename,path=''):
    contents = {}
    mtl = None
    with open(path + filename, "r") as openedfile:
        for line in openedfile:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError("mtl file doesn't start with newmtl stmt")
            elif values[0] == 'map_Kd':
                # load the texture referred to by this declaration

                vvi = 0
                vw = str()
                for vv in values:
                    if vvi:
                        vw += vv + ' '
                    vvi += 1
                mtl[values[0]] = path+vw
                surf = pygame.image.load(mtl['map_Kd'])
                image = pygame.image.tostring(surf, 'RGBA', 1)
                ix, iy = surf.get_rect().size
                texid = mtl['texture_Kd'] = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texid)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                    GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                    GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                    GL_UNSIGNED_BYTE, image)
            #else:
                #mtl[values[0]] = list(map(float, values[1:]))
        #openedfile.close()
    return contents
#====================================================
class OBJ:
    def __init__(self, filename, swapyz=False,path=''):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        with open(path + filename, "r") as openedfile:
            for line in openedfile:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'v':
                    v = list(map(float, values[1:4]))
                    if swapyz:
                        v = v[0], v[2], v[1]
                    self.vertices.append(v)
                elif values[0] == 'vn':
                    v = list(map(float, values[1:4]))
                    if swapyz:
                        v = v[0], v[2], v[1]
                    self.normals.append(v)
                elif values[0] == 'vt':
                    self.texcoords.append(list(map(float, values[1:3])))
                elif values[0] in ('usemtl', 'usemat'):
                    material = values[1]
                elif values[0] == 'mtllib':
                    self.mtl = MTL(values[1],path)
                elif values[0] == 'f':
                    face = []
                    texcoords = []
                    norms = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append(int(w[0]))
                        if len(w) >= 2 and len(w[1]) > 0:
                            texcoords.append(int(w[1]))
                        else:
                            texcoords.append(0)
                        if len(w) >= 3 and len(w[2]) > 0:
                            norms.append(int(w[2]))
                        else:
                            norms.append(0)
                    self.faces.append((face, norms, texcoords, material))

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                glColor(*mtl['Kd'])

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

def import_movment(path,folders,mov,index):
    movment_type=0
    for folder in folders:
        mov.append([])
        movment_index = 0
        if folder != '':
            p = os.path.join(path, folder)
        else:
            p = path
        for filename in os.listdir(p):
            if filename.partition('.')[2] == 'obj':
                print(p + '\\' + filename)
                mov[movment_type].append(OBJ(filename, path=p + '\\'))
                movment_index += 1
        index.append(movment_index)
        movment_type+=1



obj=[]

# Used to rotate the world
mouse_x = 0
mouse_y = 0



def MouseMotion(x, y):
    global mouse_x
    global mouse_y
    mouse_x, mouse_y =x,y

def myInit():
    global rr
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50,rr, 1, 1000)                    ########
    gluLookAt(0, 4, 6,
              0,0,-3,
              0, 1, 0)

    glClearColor(1, 1, 1, 1)

    # Enable light 1 and set position
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glLight(GL_LIGHT0, GL_POSITION, (0.5, 0.5, 0))

def draw():
    global rot
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    #glClearColor(51 / 255, 164 / 255, 1, 1)
    glClearColor(0,0,0,1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    # reseting transformations
    glLoadIdentity()

    # Rotate around the x and y axes to create a mouse-look camera
    glRotatef(mouse_y - hmy, 1, 0, 0)
    glRotatef(mouse_x - hmx, 0, 1, 0)

    glLight(GL_LIGHT0, GL_POSITION, (1, 1, 0))

    glColor(1, 1, 1)
    #glCallList(obj[0].gl_list)    #draw the obj


    glRotate(rot, 0, 1, 0)
    glColor(0, 0, 1)
    glutWireTeapot(0.25)
    rot += 1

    glutSwapBuffers()

    glColor(1,1,1) #so we don't affect the 3D models


rr=res[0]/res[1]
hmx=int(res[0]/2)
hmy=int(res[1]/2)

rot =0

def timerz(value):
    global mouse_x
    global mouse_y
    global hmx
    global hmy

    desiredFPS = 60
    glutTimerFunc(1000 // desiredFPS, timerz, value)

    #mouse_x,mouse_y= MousePosition_ctypes()
    print('x = ',mouse_x,' , y= ',mouse_y)

    glutPostRedisplay()

def load_data():
    #obj.append(OBJ("objFile.obj", path='objFile_Path\\'))   #objFile_Path\objFile

    path = 'playableChracter\\'
    folders = ['Sprint']
    #import_movment(path, folders, spider, spiderIndex)


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(res[0], res[1])
glutCreateWindow(b"objLoader")
glutFullScreen()
myInit()
glutDisplayFunc(draw)
glutTimerFunc(0,timerz,0)
glutPassiveMotionFunc(MouseMotion)
load_data()
glutMainLoop()
