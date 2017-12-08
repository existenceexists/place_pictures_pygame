# -*- coding: utf-8 -*-

import pygame


class Map:
  
  def __init__(self,game):
    self.game=game
    self.moving=False
    self.movement_step=10
    self.movement=[0,0]
    
  def update(self,event):
    return_value=False
    self.moving=False
    self.movement=[0,0]
    rect_left=self.rect.left
    rect_top=self.rect.top
    if event.type==pygame.KEYDOWN:
      if event.key==pygame.K_DOWN:
        self.set_moving([self.movement[0],-self.movement_step])
      elif event.key==pygame.K_UP:
        self.set_moving([self.movement[0],self.movement_step])
      elif event.key==pygame.K_RIGHT:
        self.set_moving([-self.movement_step,self.movement[1]])
      elif event.key==pygame.K_LEFT:
        self.set_moving([self.movement_step,self.movement[1]])
    elif event.type==pygame.KEYUP:
      if event.key==pygame.K_DOWN or event.key==pygame.K_UP:
        self.set_moving([self.movement[0],0])
      elif event.key==pygame.K_RIGHT or event.key==pygame.K_LEFT:
        self.set_moving([0,self.movement[1]])
    if self.moving:
      self.rect.topleft=(self.rect.left+self.movement[0],self.rect.top+self.movement[1])
      if self.rect.left>0:
        self.rect.left=0
      if self.rect.right<self.game.screen_rect.right:
        self.rect.right=self.game.screen_rect.right
      if self.rect.top>0:
        self.rect.top=0
      if self.rect.bottom<self.game.screen_rect.bottom:
        self.rect.bottom=self.game.screen_rect.bottom
    movement_x=self.rect.left-rect_left
    movement_y=self.rect.top-rect_top
    if movement_x!=0 or movement_y!=0:
      return_value=True
      self.game.pictures.move_all_pictures_by(movement_x,movement_y)
    return return_value
    
  def draw(self):
    self.game.screen.blit(self.image,self.rect.topleft)
    
  def set_moving(self, movement):
    self.movement=movement
    if movement==[0,0]:
      self.moving=False
    else:
      self.moving=True
    
  def open_image(self,path):
    self.path=path
    image=pygame.image.load(path).convert_alpha()
    rect=image.get_rect()
    width=rect.width
    height=rect.height
    if self.game.screen_rect.width>width:
      width=self.game.screen_rect.width
    if self.game.screen_rect.height>height:
      height=self.game.screen_rect.height
    rect.center=(int(width/2),int(height/2))
    self.image=pygame.Surface((width,height)).convert_alpha()
    self.rect=self.image.get_rect()
    self.image.fill(pygame.Color(0,0,0,255))
    self.image.blit(image,rect)
    self.rect.left=int((self.game.screen_rect.width-self.rect.width)/2.0)
    self.rect.top=int((self.game.screen_rect.height-self.rect.height)/2.0)
    self.game.screen.blit(self.image,self.rect.topleft)
    
