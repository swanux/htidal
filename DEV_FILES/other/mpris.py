#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst
# from mpris_server.adapters import MprisAdapter, EventAdapter, Track, PlayState
# from mpris_server.server import Server

# from htidal import GUI
# import htidal

# class HAdapter(MprisAdapter):
#     def can_pause(self) -> bool:
#         return True

#     def quit(self):
#         GUI.on_main_delete_event(GUI, 0, 0)
    
#     def get_current_position(self):
#         try:
#             nan_pos = GUI.player.query_position(Gst.Format.TIME)[1]
#             position = float(nan_pos) / Gst.SECOND
#         except:
#             position = None
#         return position
    
#     def next(self):
#         GUI.on_next(GUI, 0)
    
#     def previous(self):
#         GUI.on_prev(GUI, 0)
    
#     def pause(self):
#         print('inside')
#         GUI.pause(GUI)
    
#     def resume(self):
#         GUI.resume(GUI)
    
#     def stop(self):
#         GUI.stop(GUI, 0)
    
#     def play(self):
#         GUI.play(GUI)
    
#     def get_playstate(self) -> PlayState:
#         if not GUI.playing:
#             if not GUI.res:
#                 return PlayState.STOPPED
#             else:
#                 return PlayState.PAUSED
#         else:
#             return PlayState.PLAYING
    
#     def seek(self, time):
#         print(time)
#         GUI.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, time * Gst.SECOND)
    
#     def get_art_url(self, track):
#         print('Later')
#         return 'Later'
    
#     def get_stream_title(self):
#         print('Later again')
    
#     def get_current_track(self):
#         art_url = self.get_art_url(0)
#         content_id = 0
#         name = 0
#         duration = 0
#         track = "xy"
#         return track

# class HEventHandler(EventAdapter):
#     def on_app_event(self, event: str):
#         if event == 'pause':
#             print('pause')
#         else:
#             print('NOPE')

# my_adapter = HAdapter()
# mpris = Server('HTidal', adapter=my_adapter)
# event_handler = HEventHandler(mpris.player, mpris.root)
# htidal.register_event_handler(event_handler)
# mpris.publish()
# mpris.loop()

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from typing import List
from mpris_server.adapters import Metadata, PlayState, MprisAdapter, \
  Microseconds, VolumeDecimal, RateDecimal, EventAdapter
from mpris_server.base import URI, MIME_TYPES, BEGINNING, DEFAULT_RATE, DbusObj
from mpris_server.server import Server

from htidal import GUI

class HAdapter(MprisAdapter):
  def get_uri_schemes(self) -> List[str]:
    return URI

  def get_mime_types(self) -> List[str]:
    return MIME_TYPES

  def can_quit(self) -> bool:
    return True

  def quit(self):
    GUI.on_main_delete_event(GUI, 0, 0)
  
  def get_current_position(self):
    try:
      nan_pos = GUI.player.query_position(Gst.Format.TIME)[1]
      position = float(nan_pos) / Gst.SECOND
    except:
      position = None
    return position

  def next(self):
    GUI.on_next(GUI, 0)
  
  def previous(self):
    GUI.on_prev(GUI, 0)
  
  def pause(self):
    print('inside')
    GUI.pause(GUI)
  
  def resume(self):
    GUI.resume(GUI)
  
  def stop(self):
    GUI.stop(GUI, 0)
  
  def play(self):
    GUI.play(GUI)
    
  def get_playstate(self) -> PlayState:
    if not GUI.playing:
      if not GUI.res:
          return PlayState.STOPPED
      else:
          return PlayState.PAUSED
    else:
      return PlayState.PLAYING

  def seek(self, time):
    print(time)
    GUI.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, time * Gst.SECOND)

  def is_repeating(self) -> bool:
    return False

  def is_playlist(self) -> bool:
    return self.can_go_next() or self.can_go_previous()

  def set_repeating(self, val: bool):
    pass

  def set_loop_status(self, val: str):
    pass

  def get_rate(self) -> float:
    return 1.0

  def set_rate(self, val: float):
    pass

  def get_shuffle(self) -> bool:
    return False

  def set_shuffle(self, val: bool):
    return False

  def get_art_url(self, track):
    print('Later')
    return 'Later'

  def get_stream_title(self):
    print('Later again')

  def is_mute(self) -> bool:
    return False

  def can_go_next(self) -> bool:
    return False

  def can_go_previous(self) -> bool:
    return  False

  def can_play(self) -> bool:
    return True

  def can_pause(self) -> bool:
    return True

  def can_seek(self) -> bool:
    return False

  def can_control(self) -> bool:
    return True

  def get_stream_title(self) -> str:
    return "Test title"

  def metadata(self) -> dict:
    metadata = {
      "mpris:trackid": "/track/1",
      "mpris:length": 0,
      "mpris:artUrl": "Example",
      "xesam:url": "https://google.com",
      "xesam:title": "Example title",
      "xesam:artist": [],
      "xesam:album": "Album name",
      "xesam:albumArtist": [],
      "xesam:discNumber": 1,
      "xesam:trackNumber": 1,
      "xesam:comment": [],
    }

    return metadata
    

class HEventHandler(EventAdapter):
    def on_app_event(self, event: str):
      print(f"Event received: {event}")

      if event == 'pause':
        self.on_playpause()

my_adapter = HAdapter()
mpris = Server('HTidal', adapter=my_adapter)
event_handler = HEventHandler(mpris.player, mpris.root) # need to pass mpris.player & mpris.root
# right here you need to pass event_handler to htidal

mpris.loop()