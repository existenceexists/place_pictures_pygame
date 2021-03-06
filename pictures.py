#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2017 František Brožka <sentientfanda@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import pygame

import mouse
import picture


class Pictures:
  """Handles pictures that are placed on the background map image."""
  def __init__(self,game):
    self.game=game
    self.do_not_interact_with_pictures=False
    self.is_multiple_selection_on=False
    self.is_selecting_on=True
    self.is_set_within_layers=False
    self.within_layers=[]
    self.pictures_all=pygame.sprite.LayeredUpdates()
    self.pictures_to_display=pygame.sprite.LayeredUpdates()
    self.pictures_selected=pygame.sprite.LayeredUpdates()
    self.picture_highlighted=pygame.sprite.GroupSingle()
  
  def update(self,event):
    return_value=False
    if self.do_not_interact_with_pictures:
      self.do_not_interact_with_pictures=False
      return False
    if hasattr(event,"pos"):
      event_dict=dict(event.dict)
      pos=list(event_dict["pos"])
      pos[1]=pos[1]-self.game.map.display_area_rect.top
      event_dict["pos"]=pos
      event=pygame.event.Event(event.type,event_dict)
      self.game.mouse.update(event)
    if event.type==pygame.MOUSEMOTION:
      pictures_list=pygame.sprite.spritecollide(self.game.mouse,self.pictures_to_display,False)
      if pictures_list and (not self.is_set_within_layers or (self.is_set_within_layers and self.pictures_all.get_layer_of_sprite(pictures_list[-1]) in self.within_layers)):
        if self.picture_highlighted.sprite:
          if pictures_list[-1]!=self.picture_highlighted.sprite:
            self.picture_highlighted.sprite.unhighlight()
            pictures_list[-1].highlight()
            self.picture_highlighted.empty()
            self.picture_highlighted.add(pictures_list[-1])
            self.game.gui.set_label_highlighted()
            return_value=True
        else:
            pictures_list[-1].highlight()
            self.picture_highlighted.add(pictures_list[-1])
            self.game.gui.set_label_highlighted()
            return_value=True
      elif self.picture_highlighted.sprite:
            self.picture_highlighted.sprite.unhighlight()
            self.picture_highlighted.empty()
            self.game.gui.set_label_highlighted()
            return_value=True
    elif event.type==pygame.MOUSEBUTTONUP:
      pictures_list=pygame.sprite.spritecollide(self.game.mouse,self.pictures_to_display,False)
      if pictures_list and self.is_selecting_on and (not self.is_set_within_layers or (self.is_set_within_layers and self.pictures_all.get_layer_of_sprite(pictures_list[-1]) in self.within_layers)):
        if not pictures_list[-1] in self.pictures_selected.sprites():
          if not self.is_multiple_selection_on:
            for picture in self.pictures_selected.sprites():
              picture.unselect()
            self.pictures_selected.empty()
          pictures_list[-1].select()
          self.pictures_selected.add(pictures_list[-1])
          self.game.gui.set_label_selected()
          return_value=True
        else:
          pictures_list[-1].unselect()
          self.pictures_selected.remove(pictures_list[-1])
          self.game.gui.set_label_selected()
          return_value=True
      elif self.pictures_selected.sprites():
        self.selected_pictures_go_to(event.pos)
        pictures_list=pygame.sprite.spritecollide(self.game.mouse,self.pictures_to_display,False)
        return_value=True
        if pictures_list:
          if self.picture_highlighted.sprite:
            if pictures_list[-1]!=self.picture_highlighted.sprite:
              self.picture_highlighted.sprite.unhighlight()
              pictures_list[-1].highlight()
              self.picture_highlighted.empty()
              self.picture_highlighted.add(pictures_list[-1])
              self.game.gui.set_label_highlighted()
              return_value=True
          else:
              pictures_list[-1].highlight()
              self.picture_highlighted.add(pictures_list[-1])
              self.game.gui.set_label_highlighted()
              return_value=True
    return return_value
    
  def draw(self):
    for picture in self.pictures_to_display:
      picture.draw(self.game.map.display_area)
    
  def move_all_pictures_by(self,movement_x,movement_y):
    for picture in self.pictures_all:
      picture.move_by(movement_x,movement_y)
  
  def open_picture_file(self,path,layer,scale,center_x,center_y,select=False,display=True):
    pic=picture.Picture(path,scale,center_x,center_y)
    self.pictures_all.add(pic,layer=layer)
    if select:
      pic.select()
      self.pictures_selected.add(pic,layer=layer)
    if display:
      self.pictures_to_display.add(pic,layer=layer)
    
  def selected_pictures_go_to(self,position):
    if self.pictures_selected.sprites():
      picture_selected=self.pictures_selected.sprites()[-1]
      left=picture_selected.rect.left
      right=picture_selected.rect.right
      top=picture_selected.rect.top
      bottom=picture_selected.rect.bottom
      for pic in self.pictures_selected.sprites():
        left=min(left,pic.rect.left)
        right=max(right,pic.rect.right)
        top=min(top,pic.rect.top)
        bottom=max(bottom,pic.rect.bottom)
      center=(int(left+((right-left)/2.0)),int(top+((bottom-top)/2.0)))
      for pic in self.pictures_selected.sprites():
        pic.rect.center=(position[0]-(center[0]-pic.rect.center[0]),position[1]-(center[1]-pic.rect.center[1]))
      # if a picture's center is outside map borders, move the picture's center on the border
      for pic in self.pictures_selected.sprites():
        if pic.rect.center[0]<self.game.map.rect.left:
          pic.rect.center=(self.game.map.rect.left+1,pic.rect.center[1])
        if pic.rect.center[1]<self.game.map.rect.top:
          pic.rect.center=(pic.rect.center[0],self.game.map.rect.top+1)
        if pic.rect.center[0]>self.game.map.rect.right:
          pic.rect.center=(self.game.map.rect.right-1,pic.rect.center[1])
        if pic.rect.center[1]>self.game.map.rect.bottom:
          pic.rect.center=(pic.rect.center[0],self.game.map.rect.bottom-1)
    
  def get_number_of_layers(self):
    return len(self.pictures_all.layers())
  
  def get_number_of_selected_pictures(self):
    return len(self.pictures_selected.sprites())
  
  def turn_on_multiple_selection(self):
    self.is_multiple_selection_on=True
  
  def turn_off_multiple_selection(self):
    self.is_multiple_selection_on=False
  
  def turn_on_selecting(self):
    self.is_selecting_on=True
  
  def turn_off_selecting(self):
    self.is_selecting_on=False
  
  def set_selecting_within_layers(self,layers):
    self.is_set_within_layers=True
    self.within_layers=layers
  
  def unset_selecting_within_layers(self):
    self.is_set_within_layers=False
    self.within_layers=[]

  def deselect_selected(self):
    for picture in self.pictures_selected.sprites():
      picture.unselect()
    self.pictures_selected.empty()
    self.game.gui.set_label_selected()
  
  def select_same_file(self):
    path=self.pictures_selected.sprites()[-1].path
    for picture in self.pictures_to_display.sprites():
      if picture.path==path:
        picture.select()
        self.pictures_selected.add(picture)
    self.game.gui.set_label_selected()
  
  def select_same_file_and_scale(self):
    path=self.pictures_selected.sprites()[-1].path
    scale=self.pictures_selected.sprites()[-1].scale
    for picture in self.pictures_to_display.sprites():
      if picture.path==path and picture.scale==scale:
        picture.select()
        self.pictures_selected.add(picture)
    self.game.gui.set_label_selected()
  
  def delete_selected(self):
    for picture in self.pictures_selected.sprites():
      self.pictures_all.remove(picture)
      self.pictures_to_display.remove(picture)
      self.pictures_selected.remove(picture)
      if picture==self.picture_highlighted.sprite:
        self.picture_highlighted.remove(picture)
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
  
  def scale_selected_pictures(self,scale):
    for picture in self.pictures_selected.sprites():
      picture.scale_image(scale)
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
    
  def copy_selected_pictures(self):
    if self.pictures_selected.sprites():
      left=self.game.map.display_area_rect.width
      right=0
      top=self.game.map.display_area_rect.height
      bottom=0
      for pic in self.pictures_selected.sprites():
        left=min(left,pic.rect.left)
        right=max(right,pic.rect.right)
        top=min(top,pic.rect.top)
        bottom=max(bottom,pic.rect.bottom)
      center=(int(left+((right-left)/2.0)),int(top+((bottom-top)/2.0)))
      for pic in self.pictures_selected.sprites():
        self.open_picture_file(pic.path,self.pictures_all.get_layer_of_sprite(pic),pic.scale,self.game.map.display_area_rect.center[0]-(center[0]-pic.rect.center[0]),self.game.map.display_area_rect.center[1]-(center[1]-pic.rect.center[1]))
   
  def move_selected_to_new_layer(self,insert_after_layer):
    layers_new_order=self.pictures_all.layers()
    layers_new_order.insert(insert_after_layer+1,"n")
    self.pictures_all.remove(self.pictures_selected.sprites())
    layers_old=self.pictures_all.layers()
    for l in range(len(layers_new_order)):
      if not l in layers_old and l in layers_new_order:
        layers_new_order.remove(l)
    # now we have layers_new_order e.g. [0,1,"n",2,3]
    # so we move pictures according to layers_new_order layer model
    pictures_all=pygame.sprite.LayeredUpdates()
    pictures_to_display=pygame.sprite.LayeredUpdates()
    pictures_selected=pygame.sprite.LayeredUpdates()
    l=0
    for layer in layers_new_order:
      if layer=="n":
        for picture in self.pictures_selected.sprites():
          pictures_all.add(picture,layer=l)
          if picture in self.pictures_to_display.sprites():
            pictures_to_display.add(picture,layer=l)
          pictures_selected.add(picture,layer=l)
      else:
        for picture in self.pictures_all.remove_sprites_of_layer(layer):
          pictures_all.add(picture,layer=l)
          if picture in self.pictures_to_display.sprites():
            pictures_to_display.add(picture,layer=l)
          if picture in self.pictures_selected.sprites():
            pictures_selected.add(picture,layer=l)
      l+=1
    self.pictures_all=pictures_all
    self.pictures_to_display=pictures_to_display
    self.pictures_selected=pictures_selected
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
  
  def move_selected_to_layer(self,layer_number):
    layers_old_order=self.pictures_all.layers()
    for picture in self.pictures_selected.sprites():
      self.pictures_all.remove(picture)
      self.pictures_all.add(picture,layer=layer_number)
      self.pictures_selected.remove(picture)
      self.pictures_selected.add(picture,layer=layer_number)
      if picture in self.pictures_to_display:
        self.pictures_to_display.remove(picture)
        self.pictures_to_display.add(picture,layer=layer_number)
    layers_new_order=self.pictures_all.layers()
    if layers_old_order==layers_new_order:
      # now we have layers_new_order e.g. [0,1,2] and that is OK
      # so we don't need to do anything more with pictures
      self.game.gui.set_label_selected()
      self.game.gui.set_label_highlighted()
      return
    # now we have layers_new_order e.g. [0,1,3] but instead we want [0,1,2]
    # so we move pictures according to the layers_new_order layer model
    pictures_all=pygame.sprite.LayeredUpdates()
    pictures_to_display=pygame.sprite.LayeredUpdates()
    pictures_selected=pygame.sprite.LayeredUpdates()
    l=0
    for layer in layers_new_order:
      for picture in self.pictures_all.remove_sprites_of_layer(layer):
        pictures_all.add(picture,layer=l)
        if picture in self.pictures_to_display.sprites():
          pictures_to_display.add(picture,layer=l)
        if picture in self.pictures_selected.sprites():
          pictures_selected.add(picture,layer=l)
      l+=1
    self.pictures_all=pictures_all
    self.pictures_to_display=pictures_to_display
    self.pictures_selected=pictures_selected
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
  
  def move_layers(self,layers_to_move,insert_after_layer):
    where_to_be_moved=insert_after_layer+1
    layers_new_order=self.pictures_all.layers()
    for layer in layers_to_move:
      layers_new_order[layer]=None
    for layer in layers_to_move:
      layers_new_order.insert(where_to_be_moved,layer)
      where_to_be_moved+=1
    while True:
      if None in layers_new_order:
        layers_new_order.remove(None)
      else:
        break
    if layers_new_order==self.pictures_all.layers():
      # now we have layers_new_order e.g. [0,1,2] and that is OK
      # so we don't need to do anything more with pictures
      return
    # now we have layers_new_order e.g. [0,2,1] but instead we want [0,1,2]
    # so we move pictures according to the layers_new_order layer model
    pictures_all=pygame.sprite.LayeredUpdates()
    pictures_to_display=pygame.sprite.LayeredUpdates()
    pictures_selected=pygame.sprite.LayeredUpdates()
    l=0
    for layer in layers_new_order:
      for picture in self.pictures_all.remove_sprites_of_layer(layer):
        pictures_all.add(picture,layer=l)
        if picture in self.pictures_to_display.sprites():
          pictures_to_display.add(picture,layer=l)
        if picture in self.pictures_selected.sprites():
          pictures_selected.add(picture,layer=l)
      l+=1
    self.pictures_all=pictures_all
    self.pictures_to_display=pictures_to_display
    self.pictures_selected=pictures_selected
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
  
  def join_layers(self,layers_to_join):
    layers_new_order=self.pictures_all.layers()
    layers_new_order[layers_new_order.index(layers_to_join[0])]="+".join(map(str,layers_to_join))
    for layer in list(layers_new_order):
      if layer in layers_to_join:
        layers_new_order.remove(layer)
    # Now we have list of layers in the form e.g. [0,1,2,"3+4+5+6",7,8]
    # So join and move layers according to it
    pictures_all=pygame.sprite.LayeredUpdates()
    pictures_to_display=pygame.sprite.LayeredUpdates()
    pictures_selected=pygame.sprite.LayeredUpdates()
    l=0
    for layer in layers_new_order:
      if type(layer) is str:
        for la in layers_to_join:
          for picture in self.pictures_all.remove_sprites_of_layer(la):
            pictures_all.add(picture,layer=l)
            if picture in self.pictures_to_display.sprites():
              pictures_to_display.add(picture,layer=l)
            if picture in self.pictures_selected.sprites():
              pictures_selected.add(picture,layer=l)
      else:
        for picture in self.pictures_all.remove_sprites_of_layer(layer):
          pictures_all.add(picture,layer=l)
          if picture in self.pictures_to_display.sprites():
            pictures_to_display.add(picture,layer=l)
          if picture in self.pictures_selected.sprites():
            pictures_selected.add(picture,layer=l)
      l+=1
    self.pictures_all=pictures_all
    self.pictures_to_display=pictures_to_display
    self.pictures_selected=pictures_selected
    self.game.gui.set_label_selected()
    self.game.gui.set_label_highlighted()
