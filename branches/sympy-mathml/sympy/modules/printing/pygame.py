#install TeX and these Debian packages: python-pygame, python-pexpect, dvipng
#

import tempfile

try:
    import pygame
except ImportError:
    print "Pygame is not installed. In Debian, install the " \
        "python-pygame package."

def print_pygame(st):

    from pygame import QUIT, KEYDOWN, K_ESCAPE, K_q
    pygame.font.init()
    size = 640, 240
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 24)
    text = font.render(st, True, (0, 0, 0))
    textpos = text.get_rect(centerx=screen.get_width()/2)
    screen.blit(text, textpos)
    pygame.display.flip()

    image = tex2png(st,pygame)
    imagepos = image.get_rect(centerx=screen.get_width()/2).move((0,30))
    screen.blit(image, imagepos)
    pygame.display.flip()

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_q:
                return

def tex2png(eq,pygame):
    #http://www.fauskes.net/nb/htmleqII/
    import os, sys

    import pexpect

    # Include your favourite plain TeX packages and commands here
    tex_preamble = r"""\nopagenumbers
"""

    tmp1 = tempfile.mktemp()
    #texfn = '/tmp/x.tex'

    # create a LaTeX document and insert equations
    f = open(tmp1,'w')
    f.write(tex_preamble)
    f.write(r"""$$%s$$
\vfill
\eject
""" % eq)
    # end LaTeX document    
    f.write(r'\bye')
    f.close()

    # compile LaTeX document. A DVI file is created
    cwd = os.getcwd()
    os.chdir("/tmp")
    pexpect.run('tex %s' % texfn)

    # Run dvipng on the generated DVI file. Use tight bounding box. 
    # Magnification is set to 1200
    cmd = "dvipng -T tight -x 1728 -z 9 -bg transparent " \
    + "-o x.png /tmp/x.dvi" 
    pexpect.run(cmd) 
    image = pygame.image.load("/tmp/x.png")

    #remove temporary files
    os.remove("/tmp/x.tex")
    os.remove("/tmp/x.dvi")
    os.remove("/tmp/x.log")
    os.remove("/tmp/x.png")
    os.chdir(cwd)

    return image