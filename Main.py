# Set up pygame and modules
import pygame
from pygame.locals import *

pygame.init()

from Constants import *

# Create window
wSurface = pygame.display.set_mode(WINDOWSIZE, 0, 32)
pygame.display.set_caption("CoronaVirus eats people!!")

import random, copy

from Character import Character
from CoronaVirus import CoronaVirus
from Bacteria import Bacteria
from Walls import Walls
from Dots import Dots
from Sound import Sound

# Create game objects
background = pygame.image.load("bg.png").convert()
corona = CoronaVirus()
bacteria = [Bacteria()]
walls = Walls.createList(Walls())
pellets_small = Dots.createListSmall(Dots())
pellets_large = Dots.createListLarge(Dots())
clock = pygame.time.Clock()
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(0.1)

# Opening screen and music
Sound.channel.play(Sound.opening)
wSurface.fill((0, 0, 0))
wSurface.blit(background, (100, 0))
wSurface.blit(corona.getScoreSurface(), (10, 10))
wSurface.blit(corona.getLivesSurface(), (WINDOWSIZE[0] - 200, 10))
for p in pellets_small:
    wSurface.blit(Dots.images[0], (p[0] + Dots.shifts[0][0], p[1] + Dots.shifts[0][1]))
for p in pellets_large:
    wSurface.blit(Dots.images[1], (p[0] + Dots.shifts[1][0], p[1] + Dots.shifts[1][1]))
for g in bacteria:
    wSurface.blit(g.surface, g.rect)
wSurface.blit(corona.surface, corona.rect)
pygame.display.update()
while True:
    if not pygame.mixer.get_busy():
        break

# Вся игра
keepGoing_game = True
while keepGoing_game:
    # Один раунд
    keepGoing_round = True
    pygame.mixer.music.play(-1, 0.0)
    while keepGoing_round:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            # Quitting
            if event.type == QUIT:
                keepGoing_game = keepGoing_round = False

            # Нажатия кнопок
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    corona.moveUp = True
                    corona.moveLeft = corona.moveDown = corona.moveRight = False
                    corona.direction = 0
                elif event.key == K_LEFT:
                    corona.moveLeft = True
                    corona.moveUp = corona.moveDown = corona.moveRight = False
                    corona.direction = 1
                elif event.key == K_DOWN:
                    corona.moveDown = True
                    corona.moveUp = corona.moveLeft = corona.moveRight = False
                    corona.direction = 2
                elif event.key == K_RIGHT:
                    corona.moveRight = True
                    corona.moveUp = corona.moveLeft = corona.moveDown = False
                    corona.direction = 3

            # Arrow key up
            elif event.type == KEYUP:
                corona.moveUp = corona.moveLeft = corona.moveDown = corona.moveRight = False

        # Move pacman rectangle
        corona.move_c(walls)

        # Check if pacman must teleport to the other side
        corona.teleport()

        # Animate and rotate pacman sprite
        corona.getSurface()

        # Check if pacman has eaten any pellets and delete them
        Dots.check(Dots(), pellets_small, pellets_large, corona, bacteria)

        # Add a new ghost if necessary
        Bacteria.add(Bacteria(), bacteria)

        # Check if blue ghosts must return to normal
        for g in bacteria:
            if g.isBlue:
                g.checkBlue()

        # Move ghosts
        for g in bacteria:
            g.move(walls, corona)

        # Draw screen
        wSurface.fill((0, 0, 0))
        wSurface.blit(background, (100, 0))
        wSurface.blit(corona.getScoreSurface(), (10, 10))
        wSurface.blit(corona.getLivesSurface(), (WINDOWSIZE[0] - 200, 10))
        for p in pellets_small:
            wSurface.blit(Dots.images[0], (p[0] + Dots.shifts[0][0], p[1] + Dots.shifts[0][1]))
        for p in pellets_large:
            wSurface.blit(Dots.images[1], (p[0] + Dots.shifts[1][0], p[1] + Dots.shifts[1][1]))
        for g in bacteria:
            wSurface.blit(g.surface, g.rect)
        wSurface.blit(corona.surface, corona.rect)
        pygame.display.update()

        # Check if pacman collided with a ghost
        for g in bacteria[:]:
            if corona.rect.colliderect(g.rect):
                if not g.isBlue:
                    keepGoing_round = False
                    corona.lives -= 1
                    if corona.lives == 0:
                        keepGoing_game = False
                    else:
                        Sound.channel.play(Sound.death)
                    break
                else:  # Ghost is blue
                    del bacteria[bacteria.index(g)]
                    corona.score += 100
                    Sound.channel.play(Sound.eatGhost)


        # Check if pacman has eaten all the pellets
        else:
            if len(pellets_small) == 0 and len(pellets_large) == 0:
                keepGoing_game = keepGoing_round = False

    # Reset round
    pygame.mixer.music.stop()
    corona.reset()
    for g in bacteria:
        g.reset()
    while True:
        if not pygame.mixer.get_busy():
            break

# End of game screen
wSurface.fill((0, 0, 0))
surface_temp = None

if corona.lives == 0:  # Player loses
    Sound.channel.play(Sound.lose)
    surface_temp = corona.getLosingSurface()

elif len(pellets_small) == 0 and len(pellets_large) == 0:  # Player wins
    Sound.channel.play(Sound.win)
    surface_temp = corona.getWinningSurface()

if surface_temp != None:  # Player loses or wins (does not quit)
    rect_temp = surface_temp.get_rect()
    rect_temp.center = wSurface.get_rect().center
    wSurface.blit(surface_temp, rect_temp)
    pygame.display.update()

while True:
    if not pygame.mixer.get_busy():
        pygame.quit()
        break
