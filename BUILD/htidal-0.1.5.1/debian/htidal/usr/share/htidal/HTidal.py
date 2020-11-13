#! /usr/bin/python3
# -*- coding: utf-8 -*-

import tidalapi, time, gettext, locale, keyring, gi, subprocess, re, sys, os, threading, urllib, srt, datetime, webbrowser, random, requests
from configparser import ConfigParser
from concurrent import futures
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, Gio, GdkPixbuf, Gdk 
from getpass import getpass

class GUI:
    def __init__(self):
        # Prepare to use builder
        print('Init here')
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APP)
        # Import the glade file
        self.builder.add_from_file(UI_FILE)
        # Connect all signals
        self.builder.connect_signals(self)
        self.boxWait = self.builder.get_object('boxForWait')
        self.boxNo = self.builder.get_object('boxForNo')
        self.boxText = self.builder.get_object('boxForText')
        self.subStack = self.builder.get_object('subStack')
        self.sub = self.builder.get_object('sub')
        # Manual...
        # self.seekingLyr = False
        self.seekBack = False
        self.playlist = []
        self.builder.get_object('em_lab').set_label(emailC)
        self.builder.get_object('qual_combo').set_active(int(qualityC))
        if qualityC == '0':
            self.ftype = 'flac'
        else:
            self.ftype = 'm4a'
        self.allPlaylist = ''
        self.expanded = False
        self.position = 0
        self.adding = False
        self.multiTracks = True
        self.x = 0
        self.inFav = False
        self.fLab = self.builder.get_object("infoBut")
        self.relPos = 0
        self.tnum = 0
        self.query = {}
        self.playing = False
        self.res = False
        self.all = False
        self.playlistPlayer = False
        self.albume = False
        self.globSeek = True
        self.treeType = ""
        self.rem = self.builder.get_object("remember")
        self.trackCover = self.builder.get_object("cover")
        self.alb_cover = self.builder.get_object("album_img")
        self.plaicon = self.builder.get_object("play")
        self.playbut = self.builder.get_object("playBut")
        self.slider = Gtk.HScale()
        self.slider.set_margin_start(6)
        self.slider.set_margin_end(6)
        self.slider.set_draw_value(False)
        self.slider.set_increments(1, 10)
        self.slider_handler_id = self.slider.connect("value-changed", self.on_slider_seek)
        self.box = self.builder.get_object("slidBox")
        self.box.pack_start(self.slider, True, True, 0)
        self.label = Gtk.Label(label='0:00')
        self.label.set_margin_start(6)
        self.label.set_margin_end(6)
        self.box.pack_start(self.label, False, False, 0)
        self.boxMore = self.builder.get_object("more_box")
        # Dload
        self.dlStack = self.builder.get_object("dlStack")
        self.dlWin = self.builder.get_object("dlWin")
        self.whLab = self.builder.get_object("whDlLab")
        self.whLab1 = self.builder.get_object("whDlLab1")
        self.dlBar = self.builder.get_object("dlBar")
        self.dlBox1 = self.builder.get_object("dlBox1")
        self.dlBox = self.builder.get_object("dlBox")
        # Spotlight
        self.namer = self.builder.get_object("name")
        self.dat_role = self.builder.get_object("date_role")
        self.topOrNot = self.builder.get_object("track_label")
        self.rels = self.builder.get_object("nam_lab1")
        self.relis = self.builder.get_object("reli1")
        self.exLab = self.builder.get_object("extra_label")
        # Search widgets
        self.boxList = [self.builder.get_object('tracks_box'), self.builder.get_object('artists_box'), self.builder.get_object('albums_box'), self.builder.get_object('playlist_box'), self.builder.get_object('top_box')]
        self.s_label = [self.builder.get_object('top_label'), self.builder.get_object('tracks_label'), self.builder.get_object('artists_label'), self.builder.get_object('albums_label'), self.builder.get_object('playlist_label')]
        # Stores (shopping mall?)
        self.storePlaylist = Gtk.ListStore(str, str, int)
        self.allStore = Gtk.ListStore(str, int)
        self.storeAlbum = Gtk.ListStore(str, str, int)
        # Trees (forest?)
        self.tree = Gtk.TreeView.new_with_model(self.storePlaylist)
        self.tree.connect("row-activated", self.row_activated)
        self.tree.connect("button_press_event", self.mouse_click)
        self.tree.set_reorderable(True)
        self.allTree = Gtk.TreeView.new_with_model(self.allStore)
        self.allTree.connect("row-activated", self.all_row)
        self.allTree.connect("button_press_event", self.mouse_click)
        self.albumTree = Gtk.TreeView.new_with_model(self.storeAlbum)
        self.albumTree.connect("row-activated", self.album_row)
        self.albumTree.connect("button_press_event", self.mouse_click)
        # Scrolls (idk)
        self.playlistBox = self.builder.get_object("expanded")
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.add(self.tree)
        self.playlistBox.pack_start(self.scrollable_treelist, True, True, 0)
        self.allBox = self.builder.get_object("big")
        self.allScroll = Gtk.ScrolledWindow()
        self.allScroll.set_vexpand(True)
        self.allScroll.add(self.allTree)
        self.allBox.pack_start(self.allScroll, True, True, 0)
        self.albumBox = self.builder.get_object("general_top")
        self.album_scroll = Gtk.ScrolledWindow()
        self.album_scroll.set_vexpand(True)
        self.albumTree.set_vexpand(True)
        self.album_scroll.add(self.albumTree)
        self.albumBox.pack_end(self.album_scroll, True, True, 0)
        # END
        self.bigStack = self.builder.get_object("bigStack")
        self.emailEntry = self.builder.get_object("email")
        self.pwdEntry = self.builder.get_object("pwd")
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        # Get the main stack object
        global stack
        stack = self.builder.get_object('stack')
        global window
        window = self.builder.get_object(
            'main')
        if os.geteuid() == 0:
            # Indicate if runnung as root or not
            window.set_title(version+' (as superuser)')
        else:
            window.set_title(version)
        # Display the program
        window.show_all()
        for i in self.s_label:
            i.hide()
        self.force = False
        tC = futures.ThreadPoolExecutor(max_workers=2)
        tC.submit(self.check)

    def on_req_clicked(self, button):
        webbrowser.open_new("https://github.com/swanux/htidal_db/issues/new?assignees=swanux&labels=enhancement&template=custom.md&title=Lyrics+request")
    
    def on_fb_clicked(self, button):
        webbrowser.open_new("https://swanux.github.io/feedbacks.html")

    def on_main_delete_event(self, window, e):
        # Getting the window position
        x, y = window.get_position()
        # Get the size of the window
        sx, sy = window.get_size()
        dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text=_('Do you really would like to exit now?'))
        # set the title
        dialogWindow.set_title(_("Prompt"))
        dsx, dsy = dialogWindow.get_size()                          # get the dialogs size
        # Move it to the center of the main window
        dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
        dx, dy = dialogWindow.get_position()                        # set the position
        print(dx, dy)
        dialogWindow.show_all()
        res = dialogWindow.run()                                    # save the response
        if res == Gtk.ResponseType.YES:                             # if yes ...
            print('OK pressed')
            dialogWindow.destroy()
            self.force = True
            self.stopKar = True
            raise SystemExit
        elif res == Gtk.ResponseType.NO:                            # if no ...
            print('No pressed')
            dialogWindow.destroy()                                  # destroy dialog
            return True                                             # end function
        else:
            dialogWindow.destroy()                                  # destroy dialog
            return True                                             # end function
    
    def on_playBut_clicked(self, button):
        if not self.playing:
            if not self.res:
                self.play()
            else:
                self.resume()
        else:
            self.pause()

    def on_searchBut_clicked(self, button):
        self.expanded = False
        child = self.builder.get_object("search_box")
        GLib.idle_add(stack.set_visible_child, child)
    
    def get_type(self, item):
        try:
            item.audio_quality
            iType = 'track'
        except:
            try:
                item.get_top_tracks(limit=1, offset=0)
                iType = 'artist'
            except:
                try:
                    item.cover
                    iType = 'album'
                except:
                    iType = 'playlist'
        print(f'Type is: {iType}')
        return iType

    def on_searchItem_clicked(self, button):
        btn = Gtk.Buildable.get_name(button)
        print(btn)
        if 's_top' in btn:
            item = self.query['top_hit']
        elif 's_track' in btn:
            item = self.query['tracks'][int(re.findall(r'\d+', btn)[0])]
        elif 's_art' in btn:
            item = self.query['artists'][int(re.findall(r'\d+', btn)[0])]
        elif 's_album' in btn:
            item = self.query['albums'][int(re.findall(r'\d+', btn)[0])]
        elif 's_playl' in btn:
            item = self.query['playlists'][int(re.findall(r'\d+', btn)[0])]
        iType = self.get_type(item)
        if iType == 'artist':
            self.artist = item
            self.album = ''
            self.gen_playlist_view(name='album', playlistLoc=self.artist, again=self.albume, allPos='artistLoad')
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("dlAlb").hide()
            self.prevSlide = stack.get_visible_child()
            self.builder.get_object("general_bottom").show()
        elif iType == 'album' or iType == 'playlist':
            self.album = item
            self.artist = ''
            if iType == 'album':
                self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume)
            else:
                self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume, allPos='playlistPlease')
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("dlAlb").show()
            self.prevSlide = stack.get_visible_child()
            if iType == 'playlist':
                print('hiding')
                self.builder.get_object("general_bottom").hide()
            else:
                print('showing')
                self.builder.get_object("general_bottom").show()
        elif iType == 'track':
            self.gen_playlist_view(name='playlistPlayer', playlistLoc=item, again=self.playlistPlayer, allPos='radio')

    def backer(self):
        self.constructor(self.boxList[0], self.query['tracks'], 'track')
        self.constructor(self.boxList[1], self.query['artists'], 'artist')
        self.constructor(self.boxList[2], self.query['albums'], 'album')
        self.constructor(self.boxList[3], self.query['playlists'], 'playlist')
        self.constructor(self.boxList[4], [self.query['top_hit']], 'top')
    
    def seClean(self):
        if self.query['tracks'] == []:
            for i in self.s_label:
                if "track" in Gtk.Buildable.get_name(i):
                    i.hide()
        if self.query['artists'] == []:
            for i in self.s_label:
                if "artist" in Gtk.Buildable.get_name(i):
                    i.hide()
        if self.query['albums'] == []:
            for i in self.s_label:
                if "album" in Gtk.Buildable.get_name(i):
                    i.hide()
        if self.query['playlists'] == []:
            for i in self.s_label:
                if "playlist" in Gtk.Buildable.get_name(i):
                    i.hide()

    def on_searcher_search_changed(self, widget):
        txt = widget.get_text()
        if txt == '' or txt == None:
            for i in self.s_label:
                i.hide()
            for i in self.boxList:
                self.cleaner(i.get_children())
        else:
            self.query = self.session.search(txt, models=[tidalapi.artist.Artist, tidalapi.album.Album, tidalapi.media.Track, tidalapi.playlist.Playlist], limit=3, offset=0)
            for i in self.boxList:
                self.cleaner(i.get_children())
            qld = futures.ThreadPoolExecutor(max_workers=2)
            qld.submit(self.backer)
            time.sleep(0.1)
            window.show_all()
            self.seClean()

    def cleaner(self, lis):
        if lis == []:
            pass
        else:
            for i in lis:
                i.destroy()

    def constructor(self, targetParent, items, btn):
        self.inFav = False
        if items == []:
            print(f'Not in this category {btn}')
        else:
            moreBox = Gtk.Box.new(1, 10)
            moreBox.set_homogeneous(True)
            zed = 0
            for item in items:
                subBox = Gtk.Box.new(0, 10)
                namBut = Gtk.Button.new_with_label("test")
                tmpLab = namBut.get_child()
                tmpLab.set_ellipsize(3)
                tmpLab.set_markup('<big><b>'+item.name.replace('&', '')+'</b></big>')
                tmpLab.set_halign(Gtk.Align(1))
                tmpLab.set_valign(Gtk.Align(3))
                namBut.set_relief(Gtk.ReliefStyle.NONE)
                iType = "general"
                if btn == 'otAlBut':
                    Gtk.Buildable.set_name(namBut, f"s_album{zed}")
                elif btn == 'track':
                    Gtk.Buildable.set_name(namBut, f"s_track{zed}")
                elif btn == 'album':
                    Gtk.Buildable.set_name(namBut, f"s_album{zed}")
                elif btn == 'artist':
                    Gtk.Buildable.set_name(namBut, f"s_art{zed}")
                elif btn == 'playlist':
                    Gtk.Buildable.set_name(namBut, f"s_playl{zed}")
                elif btn == 'top':
                    Gtk.Buildable.set_name(namBut, f"s_top")
                    iType = self.get_type(item)
                else:
                    Gtk.Buildable.set_name(namBut, f"s_art{zed}")
                namBut.connect("clicked", self.on_searchItem_clicked)
                namBut.connect("button_press_event", self.mouse_click)
                imaje = Gtk.Image.new()
                imaje.set_margin_start(10)
                imaje.set_margin_end(10)
                imaje.set_margin_top(10)
                imaje.set_margin_bottom(10)
                subBox.pack_start(imaje, False, False, 0)
                subBox.pack_end(namBut, True, True, 0)
                moreBox.pack_end(subBox, True, True, 0)
                ld_cov = futures.ThreadPoolExecutor(max_workers=2)
                if btn == 'track' or iType == 'track':
                    ld_cov.submit(self.load_cover, where='search', widget=imaje, something=item.album)
                else:
                    ld_cov.submit(self.load_cover, where='search', widget=imaje, something=item)
                zed += 1
            targetParent.pack_start(moreBox, True, True, 0)
            moreBox.show_all()

    def on_git_link_clicked(self, button):
        # open project page in browser
        webbrowser.open_new("https://swanux.github.io/htidal.html")

    def on_go_more(self, button):
        self.cleaner(self.boxMore.get_children())
        btn = Gtk.Buildable.get_name(button)
        if self.artist == '':
            if btn == 'otAlBut':
                items = self.album.artist.get_albums()
                self.query['albums'] = items
            else:
                items = self.album.artist.get_similar()
                self.query['artists'] = items
        else:
            if btn == 'otAlBut':
                items = self.artist.get_albums()
                self.query['albums'] = items
            else:
                items = self.artist.get_similar()
                self.query['artists'] = items
        self.constructor(self.boxMore, items, btn)
        stack.set_visible_child(self.builder.get_object("scrollMore"))

    def on_go_radio(self, widget):
        if self.artist == '':
            item = self.album.tracks(limit=1, offset=0)[0]
        else:
            item = self.artist
        self.gen_playlist_view(name='playlistPlayer', playlistLoc=item, again=self.playlistPlayer, allPos='radio')

    def on_go_artist(self, widget):
        self.artist = self.playlist[self.tnum].artist
        self.album = ''
        self.gen_playlist_view(name='album', playlistLoc=self.artist, again=self.albume, allPos='artistLoad')
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollAlbum'))
        self.builder.get_object("general_bottom").show()
        self.builder.get_object("dlAlb").hide()
        self.prevSlide = stack.get_visible_child()

    def on_go_album(self, widget):
        btn = Gtk.Buildable.get_name(widget)
        if btn == 'goAlbum':
            self.album = self.playlist[self.tnum].album
        else:
            print('relplace')
            self.album = self.relList[self.relepo]
        self.artist = ''
        self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume)
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollAlbum'))
        self.builder.get_object("general_bottom").show()
        self.builder.get_object("dlAlb").show()
        self.prevSlide = stack.get_visible_child()

    def on_dl_alb(self, button):
        iType = self.get_type(self.album)
        dl = futures.ThreadPoolExecutor(max_workers=2)
        dl.submit(self.general_download, items=self.album.tracks(), tpe=iType, name=self.album.name)
        self.dlStack.set_visible_child(self.dlBox1)
        self.dlWin.show_all()

    def on_dload_activate(self, widget):
        dl = futures.ThreadPoolExecutor(max_workers=2)
        dl.submit(self.general_download, items=[self.playlist[self.tnum]], tpe='track')
        self.dlStack.set_visible_child(self.dlBox)
        self.dlWin.show_all()

    def general_download(self, items, tpe, name=''): # FIXME
        dlDir = {}
        self.tot_size = 0
        i = 1
        lens = len(items)
        for item in items:
            # self.updator(i=i, lens=lens)
            GLib.idle_add(self.whLab1.set_label, f"{i} out of {lens}")
            time.sleep(1.5)
            url = item.get_url()
            tmp = urllib.request.urlopen(url)
            file_name = item.name
            file_size = int(tmp.getheader('Content-Length'))
            if tpe == 'track':
                target = f'/home/{user}/Music/htidal/tracks/{item.name}.{self.ftype}'
            elif tpe == 'album':
                target = f'/home/{user}/Music/htidal/albums/{name}/{item.name}.{self.ftype}'
            elif tpe == 'playlist':
                target = f'/home/{user}/Music/htidal/playlists/{name}/{item.name}.{self.ftype}'
            elif tpe == 'playqueue':
                target = f'/home/{user}/Music/htidal/snapshots/{name}/{item.name}.{self.ftype}'
            # elif tpe == 'video':
            #     target = f'/home/{user}/Music/htidal/videos/{item.name}.{self.ftype}'
            dlDir[file_name] = {'size' : file_size, 'url' : url, 'target' : target.replace(' ', "\ ").replace('(', '').replace(')', '')}
            self.tot_size += file_size
            i += 1
        print(dlDir)
        self.dlBar.set_fraction(0.00)
        self.dlded = 0
        self.dlStack.set_visible_child(self.dlBox)
        dl = futures.ThreadPoolExecutor(max_workers=2)
        dl.submit(self.dl_backend, dlDir=dlDir)
        def counter(timer):
            if self.dlded < self.tot_size:
                print(self.dlded/self.tot_size)
                GLib.idle_add(self.dlBar.set_fraction, self.dlded/self.tot_size)
                return True
            else:
                GLib.idle_add(self.dlWin.hide)
                return False
        self.source_id = GLib.timeout_add(200, counter, None)

    def dl_backend(self, dlDir):
        GLib.idle_add(self.whLab.set_label, f"{round(self.dlded/1024/1024, 1)} MB downloaded of total {round(self.tot_size/1024/1024, 1)} MB")
        for current in dlDir:
            time.sleep(1)
            url = dlDir[current]['url']
            print(url)
            u = urllib.request.urlopen(url)
            target = dlDir[current]['target']
            targetList = target.split('/')
            targetList.remove(targetList[-1])
            os.system(f"mkdir -p {'/'.join(targetList)}")
            print(self.dlded, self.tot_size)
            with open(target.replace('\\ ', ' '), "wb") as f:
                while True:
                    buffer = u.read(4096)
                    if not buffer:
                        break
                    self.dlded += len(buffer)
                    f.write(buffer)
                    GLib.idle_add(self.whLab.set_label, f"{round(self.dlded/1024/1024, 1)} MB downloaded of total {round(self.tot_size/1024/1024, 1)} MB")

    def on_karaoke_activate(self, widget):
        print('Karaoke')
        self.stopKar = False
        track = self.playlist[self.tnum].name
        tid = self.playlist[self.tnum].id
        artists = self.playlist[self.tnum].artists
        dbnow = os.listdir('/usr/share/htidal/db/')
        self.sub.set_title('%s - %s' % (track, artists[0].name))
        if '%s-%s.srt' % (track.replace(' ', '_').replace("'", '').replace('(', '').replace(')', ''), tid) not in dbnow:
            indices = [i for i, s in enumerate(dbnow) if '%s' % track.replace(' ', '_').replace("'", '').replace('(', '').replace(')', '') in s]
            if indices == []:
                print("NEW NEEDED1")
                self.builder.get_object('id').set_label('Track ID: %s' % tid)
                self.subStack.set_visible_child(self.boxNo)
            else:
                print("PARTIAL")
                x, y = window.get_position()
                sx, sy = window.get_size()
                dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text=_('The current track does not have synced lyrics. However there is one which might be similar: %s.\nWould you like to give it a try?' % dbnow[indices[0]]))
                dialogWindow.set_title(_("Prompt"))
                dsx, dsy = dialogWindow.get_size()
                dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
                dx, dy = dialogWindow.get_position()
                print(dx, dy)
                dialogWindow.show_all()
                res = dialogWindow.run()
                if res == Gtk.ResponseType.YES:
                    print('OK pressed')
                    dialogWindow.destroy()
                    self.start_karaoke(dbnow[indices[0]])
                else:
                    print('No pressed')
                    dialogWindow.destroy()
                    self.builder.get_object('id').set_label('Track ID: %s' % tid)
                    self.subStack.set_visible_child(self.boxNo)
        else:
            print("FOUND")
            self.start_karaoke("%s-%s.srt" % (track.replace(' ', '_').replace("'", '').replace('(', '').replace(')', ''), tid))
        self.sub.show_all()

    def on_hide(self, window, e):
        print('hide')
        self.stopKar = True
        self.sub.hide()
        return True

    def on_settingBut_clicked(self, button):
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollSet'))

    def on_signOut_clicked(self, button):
        self.session = tidalapi.Session(self.c)
        os.system('rm /home/%s/.config/htidal.ini' % user)
        self.bigStack.set_visible_child(self.builder.get_object('loginBox'))

    def on_event1_button_press_event(self, event, button):
        print('eventhere')
    
    def on_event2_button_press_event(self, event, button):
        print('event2here')

    def on_wr_but_clicked(self, button):
        nQuality = self.builder.get_object('qual_combo').get_active()
        parser.set('misc', 'quality', str(nQuality))
        file = open("/home/%s/.config/htidal.ini" % user, "w+")
        parser.write(file)
        file.close()

    def on_fav_gen(self, button):
        self.cleaner(self.boxMore.get_children())
        try:
            btn = Gtk.Buildable.get_name(button)
        except:
            btn = button
        if "track" in btn:
            items = self.favs
            self.query['tracks'] = items
            btn = "track"
        elif "list" in btn:
            items = self.favPlys
            self.query['playlists'] = items
            btn = "playlist"
        elif "art" in btn:
            items = self.favArts
            self.query['artists'] = items
            btn = "artist"
        else:
            items = self.favAlbs
            self.query['albums'] = items
            btn = "album"
        self.constructor(self.boxMore, items, btn)
        self.inFav = True
        stack.set_visible_child(self.builder.get_object("scrollMore"))

    def on_favs_clicked(self, button):
        stack.set_visible_child(self.builder.get_object("scrollFavs"))

    def on_myLists_clicked(self, button):
        self.gen_playlist_view(name="all", again=self.all)
        stack.set_visible_child(self.builder.get_object('big'))

    def start_karaoke(self, sfile):
        print('HEY')
        with open ("/usr/share/htidal/db/%s" % (sfile), "r") as subfile:
            presub = subfile.read()
        subtitle_gen = srt.parse(presub)
        subtitle = list(subtitle_gen)
        self.subStack.set_visible_child(self.boxText)
        lyrs = futures.ThreadPoolExecutor(max_workers=4)
        lyrs.submit(self.slideShow, subtitle)

    def to1(self):
        if self.hav2:
            self.line1 = self.line2
        else:
            self.line1 = self.buffer
            self.buffer = []
        self.hav1 = True

    def to2(self):
        if self.where+1 <= self.lenlist:
            if self.hav3:
                self.line2 = self.line3
            else:
                self.line2 = self.buffer
                self.buffer = []
            self.hav2 = True
        else:
            if self.hav1 and not self.hav3:
                self.to1()
            self.line2 = self.line3
            self.line3 = []
            self.sync()

    def to3(self):
        if self.where+2 <= self.lenlist:
            if self.hav1 and self.hav3:
                self.to1()
            if self.hav2 and self.hav3:
                self.to2()
            self.line3 = self.buffer
            self.buffer = []
            self.hav3 = True
        else:
            if self.hav1:
                self.to1()
            if self.hav2:
                self.to2()
            self.line3 = self.buffer
            self.buffer = []
            self.hav3 = False
        self.sync()

    def sync(self):
        simpl2 = ""
        simpl3 = ""
        if self.line2 != []:
            for z in self.line2:
                if self.stopKar or self.seekBack:
                    break
                simpl2 += '%s ' % z.content.replace('#', '')
        else:
            simpl2 = ""
        if self.line3 != []:
            for z in self.line3:
                if self.stopKar or self.seekBack:
                    break
                simpl3 += '%s ' % z.content.replace('#', '')
        else:
            simpl3 = ""
        # if not self.seekingLyr:
        tg = GLib.idle_add(self.label2.set_label, simpl2)
        # GLib.source_remove(tg)
        tg = GLib.idle_add(self.label3.set_label, simpl3)
        # GLib.source_remove(tg)
        done = ""
        tmpline = self.line1[:]
        first = True
        tl1 = self.line1
        tl1.insert(0, "")
        it = 1
        maxit = len(tl1)-1
        for xy in tl1:
            # if self.position <= xy.end.total_seconds():
            #     self.seekingLyr = False
            if self.stopKar or self.seekBack:
                break
            if first:
                first = False
            else:
                tmpline = tmpline[1:]
            leftover = ""
            for y in tmpline:
                if self.stopKar or self.seekBack:
                    break
                leftover += '%s ' % y.content.replace('#', '')
            # if not self.seekingLyr:
            try:
                tg = GLib.idle_add(self.label1.set_markup, "<span color='green'>%s</span> <span color='green'>%s</span> <span color='white'>%s</span>" % (done, xy.content.replace('#', ''), leftover))
            except:
                print('Null')
                tg = GLib.idle_add(self.label1.set_markup, "<span color='green'>%s</span> <span color='green'>%s</span> <span color='white'>%s</span>" % (done, xy, leftover))
            # GLib.source_remove(tg)
            while not self.stopKar:
                time.sleep(0.01)
                if it > maxit:
                    if self.position >= xy.end.total_seconds()-0.05 and self.position >= 0.5:
                        break
                else:
                    xz = tl1[it]
                    if self.position >= xz.start.total_seconds()-0.1 and self.position >= 0.5:
                        break
                if self.seekBack:
                    break
            it += 1
            try:
                done += '%s ' % xy.content.replace('#', '')
            except:
                print('First word')

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        self.label1 = self.builder.get_object('label1')
        self.label2 = self.builder.get_object('label2')
        self.label3 = self.builder.get_object('label3')
        while not self.stopKar:
            time.sleep(0.01)
            self.line1 = []
            self.line2 = []
            self.line3 = []
            self.buffer = []
            self.hav1 = False
            self.hav2 = False
            self.hav3 = False
            self.where = -1
            for word in subtitle:
                if '#' in word.content:
                    self.buffer.append(word)
                    if not self.hav1:
                        self.to1()
                    elif not self.hav2:
                        self.to2()
                    else:
                        self.to3()
                else:
                    self.buffer.append(word)
                if self.stopKar or self.seekBack:
                    break
                self.where += 1
            if not self.seekBack:
                self.to2()
                self.to1()
                self.line2 = []
                self.sync()
                self.stopKar = True
            else:
                self.seekBack = False
            # for line in subtitle:
            #     if self.stopKar:
            #         break
            #     GLib.idle_add(label1.set_label, line.content)
            #     if subtitle.index(line)+1 <= lenlist:
            #         GLib.idle_add(label2.set_markup, "<span color='blue'>%s</span> <span color='red'>hey</span>" % subtitle[subtitle.index(line)+1].content)
            #     else:
            #         GLib.idle_add(label2.set_label, '')
            #         self.stopKar = True
            #     if subtitle.index(line)+2 <= lenlist:
            #         GLib.idle_add(label3.set_label, subtitle[subtitle.index(line)+2].content)
            #     else:
            #         GLib.idle_add(label3.set_label, '')
            #     # print(line.end.total_seconds())
            #     while not self.stopKar:
            #         time.sleep(0.01)
            #         if self.position >= line.end.total_seconds()-0.12 and self.position >= 0.5:
            #             break
            #         if self.seekBack == True:
            #             break
            #     if self.seekBack == True:
            #         self.seekBack = False
            #         break

    def row_activated(self, widget, row, col):
        self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.on_next("clickMode")
    
    def playIt(self, button):
        self.relPos = 0
        if self.artiste == False:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='albumLoad')
        else:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='artistLoad')
        print('submit3')
        self.on_next("clickModeA")
    
    def album_row(self, widget, row, col):
        print('posAlb')
        self.relPos = self.albumTree.get_selection().get_selected_rows()[1][0][0]
        if self.artiste == False:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='albumLoad')
        else:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='artistLoad')
        print('submit3')
        self.on_next("clickModeA")
    
    def on_newList_clicked(self, button):
        stack.set_visible_child(self.builder.get_object("scrollCreate"))

    def on_cancel(self, button):
        stack.set_visible_child(self.allBox)

    def on_create(self, button):
        name = self.builder.get_object("create_entry").get_text()
        tidalapi.user.LoggedInUser(self.session, self.userID).create_playlist(name, '')
        self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
        self.on_myLists_clicked("")

    def all_row(self, widget, row, col):
        if self.adding == False:
            print('pos')
            self.allPos = self.allTree.get_selection().get_selected_rows()[1][0][0]
            self.artist = ""
            self.album = self.allPlaylist[self.allPos]
            self.gen_playlist_view(name='album', playlistLoc="myList", again=self.albume, allPos=self.allPos)
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("general_bottom").hide()
            self.builder.get_object("dlAlb").show()
            self.prevSlide = stack.get_visible_child()
            print('submit2')
        else:
            allPos = self.allTree.get_selection().get_selected_rows()[1][0][0]
            playlist = self.allPlaylist[allPos]
            local = tidalapi.playlist.UserPlaylist(self.session, playlist.id)
            local.add([self.whatToAdd.id])
            self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
            stack.set_visible_child(self.prevTmp)
            self.adding = False

    def rem_fav(self, item):
        if 's_track' in self.btn:
            item = self.query['tracks'][int(re.findall(r'\d+', self.btn)[0])]
            self.favourite.remove_track(item.id)
            # self.favs = self.favourite.tracks()
            self.favs.remove(item)
            self.on_fav_gen("track")
        elif 's_art' in self.btn:
            item = self.query['artists'][int(re.findall(r'\d+', self.btn)[0])]
            self.favourite.remove_artist(item.id)
            self.favArts = self.favourite.artists()
            self.on_fav_gen("art")
        elif 's_album' in self.btn:
            item = self.query['albums'][int(re.findall(r'\d+', self.btn)[0])]
            self.favourite.remove_album(item.id)
            self.favAlbs = self.favourite.albums()
            self.on_fav_gen("album")
        elif 's_playl' in self.btn:
            item = self.query['playlists'][int(re.findall(r'\d+', self.btn)[0])]
            self.favourite.remove_playlist(item.id)
            self.favPlys = self.favourite.playlists()
            self.on_fav_gen("list")

    def mouse_click(self, widget, event):
        if event.button == 3:
            menu = Gtk.Menu()
            loc = Gtk.Buildable.get_name(stack.get_visible_child())
            if self.treeType == "own" and loc == "scrollAlbum":
                pthinfo = self.albumTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.albumTree.grab_focus()
                self.albumTree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Remove from playlist')
                menu_item.connect("activate", self.del_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif self.inFav == True and loc == "scrollMore":
                self.btn = Gtk.Buildable.get_name(widget)
                menu_item = Gtk.MenuItem.new_with_label('Remove from Favourites')
                menu_item.connect("activate", self.rem_fav)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "scrollAlbum" and self.artist == '':
                pthinfo = self.albumTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.albumTree.grab_focus()
                self.albumTree.set_cursor(path,col,0)
                this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
                for i in self.favs:
                    if self.albumTracks[self.storeAlbum[this][2]].id == i.id:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
                menu_item = Gtk.MenuItem.new_with_label(state)
                menu_item.connect("activate", self.add_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Add to playlist')
                menu_item.connect("activate", self.add_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "big":
                pthinfo = self.allTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.allTree.grab_focus()
                self.allTree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Delete playlist')
                menu_item.connect("activate", self.del_pyl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "expanded":
                pthinfo = self.tree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.tree.grab_focus()
                self.tree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Delete from current playqueue')
                menu_item.connect("activate", self.del_cur)
                menu.add(menu_item)
                this = self.tree.get_selection().get_selected_rows()[1][0][0]
                for i in self.favs:
                    if self.playlist[self.storePlaylist[this][2]].id == i.id:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
                menu_item = Gtk.MenuItem.new_with_label(state)
                menu_item.connect("activate", self.add_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Save current playqueue offline')
                menu_item.connect("activate", self.dl_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Add to playlist')
                menu_item.connect("activate", self.add_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
    
    def del_pyl(self, itme):
        this = self.allTree.get_selection().get_selected_rows()[1][0][0]
        local = tidalapi.playlist.UserPlaylist(self.session, self.allPlaylist[self.allStore[this][1]].id)
        local.delete()
        self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
        self.gen_playlist_view(name="all", again=self.all)

    def add_pl(self, item):
        self.prevTmp = stack.get_visible_child()
        self.whatToAdd = self.playlist[self.tnum]
        self.adding = True
        self.on_myLists_clicked('')

    def del_pl(self, item):
        this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
        local = tidalapi.playlist.UserPlaylist(self.session, self.album.id)
        local.remove_by_index(this)
        self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
        # self.album.remove(self.album[self.storeAlbum[this][2]])
        self.album = self.allPlaylist[self.allPos]
        self.gen_playlist_view(name='album', playlistLoc="myList", again=self.albume, allPos=self.allPos)

    def del_cur(self, item):
        this = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.playlist.remove(self.playlist[self.storePlaylist[this][2]])
        self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')
    
    def dl_cur(self, item):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dl = futures.ThreadPoolExecutor(max_workers=2)
        dl.submit(self.general_download, items=self.playlist, tpe='playqueue', name=f"Playqueue_{str(dt_string).replace('.', '-').replace(' ', '_')}")
        self.dlStack.set_visible_child(self.dlBox1)
        self.dlWin.show_all()

    def add_cur(self, item):
        state = item.get_label()
        loc = Gtk.Buildable.get_name(stack.get_visible_child())
        if loc == "expanded":
            this = self.tree.get_selection().get_selected_rows()[1][0][0]
            track = self.playlist[self.storePlaylist[this][2]]
        elif loc == "scrollAlbum":
            this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
            track = self.albumTracks[self.storeAlbum[this][2]]
        if "Add" in state:
            self.favourite.add_track(track.id)
            print(f"Added {track.name}")
        else:
            self.favourite.remove_track(track.id)
            print(f"Removed {track.name}")
        self.favs = self.favourite.tracks()
    
    def add_fav(self, button):
        state = button.get_label()
        if "Add" in state:
            if self.artist == '':
                try:
                    self.album.creator.name
                    self.favourite.add_playlist(self.album.id)
                    self.favPlys = self.favourite.playlists()
                    print(f"Added playlist {self.album.name}")
                except:
                    self.favourite.add_album(self.album.id)
                    self.favAlbs = self.favourite.albums()
                    print(f"Added album {self.album.name}")
            else:
                self.favourite.add_artist(self.artist.id)
                self.favArts = self.favourite.artists()
                print(f"Added artist {self.artist.name}")
            button.set_label("Remove from Favourites")
        else:
            if self.artist == '':
                try:
                    self.album.creator.name
                    self.favourite.remove_playlist(self.album.id)
                    self.favPlys = self.favourite.playlists()
                    print(f"Removed playlist {self.album.name}")
                except:
                    self.favourite.remove_album(self.album.id)
                    self.favAlbs = self.favourite.albums()
                    print(f"Removed album {self.album.name}")
            else:
                self.favourite.remove_artist(self.artist.id)
                self.favArts = self.favourite.artists()
                print(f"Removed artist {self.artist.name}")
            button.set_label("Add to Favourites")

    def on_next(self, button):
        print("Next")
        if button == "clickMode":
            self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        elif button == "clickModel":
            self.tnum = 0
        elif button == "clickModeA":
            self.tnum = self.storeAlbum[self.relPos][2] # pylint: disable=unsubscriptable-object
        else:
            try:
                self.albumTree.set_cursor(self.relPos)
            except:
                print('Out of length')
            self.tree.set_cursor(self.relPos)
            self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
            self.relPos = self.relPos + 1
            if self.relPos >= len(self.playlist):
                self.relPos = 0
            self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        try:
            self.globSeek = False
            self.stop("xy")
        except:
            print("No playbin yet to stop.")
        self.globSeek = True
        self.x = 0
        ld_cov = futures.ThreadPoolExecutor(max_workers=2)
        ld_cov.submit(self.load_cover)
        self.play()

    def on_prev(self, button):
        print("Prev")
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.relPos = self.relPos - 1
        if self.relPos < 0:
            self.relPos = len(self.playlist)-1
        self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        try:
            self.pause()
            self.globSeek = False
            self.stop("xy")
            self.globSeek = True
        except:
            print("No playbin yet to stop.")
        self.x = 0
        ld_cov = futures.ThreadPoolExecutor(max_workers=2)
        ld_cov.submit(self.load_cover)
        self.play()

    def next_rel(self, button):
        self.relepo += 1
        if self.relepo == len(self.relList)-1:
            self.builder.get_object("nextRel").set_sensitive(False)
        if self.relepo == 1:
            self.builder.get_object("prevRel").set_sensitive(True)
        self.skipper()

    def prev_rel(self, button):
        self.relepo -= 1
        if self.relepo == len(self.relList)-2:
            self.builder.get_object("nextRel").set_sensitive(True)
        if self.relepo == 0:
            self.builder.get_object("prevRel").set_sensitive(False)
        self.skipper()

    def skipper(self):
        x, y = window.get_size()
        album = self.relList[self.relepo]
        pic = album.image(640)
        response = urllib.request.urlopen(pic)
        input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None)
        num = int(y/2.8)
        coverBuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream, num, num, True, None)
        tg = GLib.idle_add(self.relis.set_from_pixbuf, coverBuf)
        tg2 = GLib.idle_add(self.rels.set_label, album.name)

    def load_cover(self, where='', widget='', something=''):
        # print("Load cover")
        x, y = window.get_size()
        if where == '':
            album = self.playlist[self.tnum].album
            pic = album.image(640)
            response = urllib.request.urlopen(pic)
            input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None)
            coverBuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream, int(x/2.1), int(y/1.3), False, None)
            tg = GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)
        elif where == 'album':
            pic = something.image(320)
            response = urllib.request.urlopen(pic)
            input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None)
            coverBuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream, 190, 190, True, None)
            tg = GLib.idle_add(self.alb_cover.set_from_pixbuf, coverBuf)
            self.relepo = 0
            try:
                self.skipper()
            except:
                pass
        elif where == 'search':
            pic = something.image(320)
            response = urllib.request.urlopen(pic)
            input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None)
            coverBuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream, 55, 55, True, None)
            tg = GLib.idle_add(widget.set_from_pixbuf, coverBuf)

    def on_expand_clicked(self, button):
        self.tree.set_cursor(self.relPos)
        if self.expanded == False:
            print("expand")
            self.expanded = True
            self.prevSlide = stack.get_visible_child()
            stack.set_visible_child(self.builder.get_object("expanded"))
        else:
            self.expanded = False
            stack.set_visible_child(self.prevSlide)
            try:
                self.albumTree.set_cursor(self.relPos)
            except:
                print('Out of length')
    
    def on_back(self, button):
        print("Home")
        self.expanded = False
        stack.set_visible_child(self.builder.get_object("scrollHome"))
        
    def on_slider_seek(self, widget):
        print("Slider seek")
        if self.globSeek:
            seek_time_secs = self.slider.get_value()
            # self.seekingLyr = True
            if seek_time_secs < self.position:
                self.seekBack = True
                print('back')
                print(seek_time_secs, self.position)
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs * Gst.SECOND)
        else:
            print("No need to seek")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.on_next("xy")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)

    def on_shuffBut_clicked(self, button):
        self.gen_playlist_view(name='shuffle')

    def gen_playlist_view(self, playlistLoc='', name='', again=False, allPos=''):
        if name == 'shuffle':
            if self.playlistPlayer == True:
                self.relPos = 0
                playlistLoc = random.sample(self.playlist, len(self.playlist))
                self.playlist = playlistLoc
                self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')
                self.on_next('clickModel')
        elif name == 'playlistPlayer':
            if allPos == 'albumLoad':
                self.playlist = self.album.tracks()
            elif allPos == 'artistLoad':
                self.playlist = self.artist.get_top_tracks()
            elif allPos == 'regen':
                print('Regenerate only')
            elif allPos == 'radio':
                self.relPos = 0
                if self.get_type(playlistLoc) == 'artist':
                    try:
                        self.playlist = playlistLoc.get_radio()
                    except:
                        print('No radio station avilable')
                else:
                    try:
                        self.playlist = playlistLoc.artist.get_radio()
                    except:
                        print('No radio station avilable')
                    self.playlist.insert(0, playlistLoc)
            else:
                print('Passing in generator')
            playlistLoc = self.playlist
            self.storePlaylist = Gtk.ListStore(str, str, int)
            self.tree.set_model(self.storePlaylist)
            def doapp():
                for x in range(len(playlistLoc)):
                    self.storePlaylist.append([t[x], a[x], il[x]])
                return False
            t = []
            a = []
            il = []
            for i in range(len(playlistLoc)):
                t.append(playlistLoc[i].name)
                a.append(playlistLoc[i].artist.name)
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time")
                for i, column_title in enumerate(["Title", "Artist", "ID"]):
                    renderer = Gtk.CellRendererText(xalign=0)
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    if column_title == "Title" or column_title == "Artist":
                        column.set_fixed_width(150)
                        column.set_resizable(True)
                    else:
                        column.set_max_width(50)
                        column.set_resizable(False)
                    column.set_sort_column_id(i)
                    column.set_sort_indicator(False)
                    self.tree.append_column(column)
            self.playlistPlayer = True
            ld_cov = futures.ThreadPoolExecutor(max_workers=2)
            ld_cov.submit(self.load_cover)
            if allPos == 'radio':
              self.on_next('clickModel')
        elif name == "all":
            self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
            playlistLoc = self.allPlaylist
            self.allStore = Gtk.ListStore(str, int)
            self.allTree.set_model(self.allStore)
            def doapp():
                for x in range(len(playlistLoc)):
                    self.allStore.append([t[x], il[x]])
                return False
            t = []
            il = []
            for i in range(len(playlistLoc)):
                t.append(playlistLoc[i].name)
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time")
                for i, column_title in enumerate(["Name", "ID"]):
                    renderer = Gtk.CellRendererText()
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    x, y = window.get_size()
                    print(x, y)
                    if column_title == "Name":
                        column.set_fixed_width(int(x/3))
                        column.set_resizable(True)
                    else:
                        column.set_fixed_width(30)
                        column.set_resizable(False)
                    self.allTree.append_column(column)
            self.all = True
        elif name == 'album':
            self.treeType = ""
            self.fLab.show()
            self.builder.get_object("otAlBut").show()
            self.builder.get_object("otArBut").show()
            if allPos == 'artistLoad':
                albumLoc = playlistLoc.get_top_tracks()
                self.albumTracks = albumLoc
                self.artiste = True
            elif playlistLoc == "myList":
                self.artiste = False
                albumLoc = self.allPlaylist[allPos].tracks()
                self.albumTracks = albumLoc
            else:
                self.artiste = False
                albumLoc = playlistLoc.tracks()
                self.albumTracks = albumLoc
            self.storeAlbum = Gtk.ListStore(str, str, int)
            self.albumTree.set_model(self.storeAlbum)
            def doapp():
                for x in range(len(albumLoc)):
                    self.storeAlbum.append([t[x], a[x], il[x]])
                return False
            t = []
            a = []
            il = []
            for i in range(len(albumLoc)):
                t.append(albumLoc[i].name)
                a.append(albumLoc[i].artist.name)
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time album")
                for i, column_title in enumerate(["Title", "Artist", "ID"]):
                    renderer = Gtk.CellRendererText(xalign=0)
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    if column_title == "Title" or column_title == "Artist":
                        column.set_fixed_width(150)
                        column.set_resizable(True)
                    else:
                        column.set_max_width(50)
                        column.set_resizable(False)
                    column.set_sort_column_id(i)
                    self.albumTree.append_column(column)
            self.albume = True
            ld_cov = futures.ThreadPoolExecutor(max_workers=2)
            if playlistLoc == "myList":
                self.namer.set_label(self.allPlaylist[allPos].name)
            else:
                self.namer.set_label(playlistLoc.name)
            if allPos == 'artistLoad':
                try:
                    self.dat_role.set_label(re.sub(r"[\(\[].*?[\)\]]", "", playlistLoc.get_bio()))
                except:
                    self.dat_role.set_label('No bio avilable')
                self.topOrNot.set_label("Top Tracks")
                self.relList = playlistLoc.get_albums(limit=None, offset=0)
                self.exLab.set_label("Albums")
                for i in self.favArts:
                    if playlistLoc.id == i.id:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
            else:
                if allPos == 'playlistPlease':
                    self.dat_role.set_label(f"Creator: {playlistLoc.creator.name}")
                    for i in self.favPlys:
                        if playlistLoc.id == i.id:
                            state = 'Remove from Favourites'
                            break
                        else:
                            state = 'Add to Favourites'
                elif playlistLoc == 'myList':
                    self.treeType = "own"
                    self.dat_role.set_label(f"Creator: {self.allPlaylist[allPos].creator.name}")
                    self.fLab.hide()
                    self.builder.get_object("otAlBut").hide()
                    self.builder.get_object("otArBut").hide()
                else:
                    self.dat_role.set_label(str(playlistLoc.release_date).split(' ')[0])
                    self.builder.get_object("prevRel").set_sensitive(False)
                    self.relList = playlistLoc.artist.get_albums(limit=None, offset=0)
                    for i in self.favAlbs:
                        if playlistLoc.id == i.id:
                            state = 'Remove from Favourites'
                            break
                        else:
                            state = 'Add to Favourites'
                self.topOrNot.set_label("Tracks")
                self.exLab.set_label("Releated")
            if playlistLoc != "myList":
                self.fLab.set_label(state)
                ld_cov.submit(self.load_cover, where='album', something=playlistLoc)
            else:
                ld_cov.submit(self.load_cover, where='album', something=self.allPlaylist[allPos])
    def play(self):
        print("Play")
        self.res = True
        self.playing = True
        self.position = 0
        url = self.playlist[self.tnum].get_url()
        self.player.set_property("uri", url)
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.player.set_state(Gst.State.PLAYING)
        self.plaicon.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(250, self.updateSlider)
        GLib.timeout_add(80, self.updatePos)
    
    def resume(self):
        print("Resume")
        self.playing = True
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.player.set_state(Gst.State.PLAYING)
        self.plaicon.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(250, self.updateSlider)
        GLib.timeout_add(80, self.updatePos)


    def stop(self, widget):
        print("Stop")
        self.res = False
        self.playing = False
        self.label.set_text("0:00")
        self.plaicon.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.slider.set_value(0)
        self.player.set_state(Gst.State.NULL)
    
    def pause(self): 
        print("Pause")
        self.playing = False
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.plaicon.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.player.set_state(Gst.State.PAUSED)

    def updatePos(self):
        if(self.playing == False):
            return False
        nanosecs = self.player.query_position(Gst.Format.TIME)[1]
        self.position = float(nanosecs) / Gst.SECOND
        return True

    def updateSlider(self):
        if(self.playing == False):
            return False # cancel timeout
        try:
                nanosecs = self.player.query_position(Gst.Format.TIME)[1]
                duration_nanosecs = self.player.query_duration(Gst.Format.TIME)[1]
                # block seek handler so we don't seek when we set_value()
                self.slider.handler_block(self.slider_handler_id)
                duration = float(duration_nanosecs) / Gst.SECOND
                position = float(nanosecs) / Gst.SECOND
                self.slider.set_range(0, duration)
                self.slider.set_value(position)
                self.label.set_text ("%d" % (position / 60) + ":%02d" % (position % 60))
                self.slider.handler_unblock(self.slider_handler_id)
        except Exception as e:
            print ('W: %s' % e)
            pass
        return True
    
    def check(self):
        try:
            urllib.request.urlopen('http://216.58.192.142', timeout=5)
            print('yes, net')
            net = True
        except:
            print('no internet')
            net = False
            offtxt = _("You have no internet connection!")
            os.system('zenity --warning --text=%s --ellipsize' % offtxt)
            raise SystemExit
    
    def on_remember_toggled(self, button, data=None):
        self.rmbe = self.rem.get_active()

    def favver(self):
        print('favving')
        self.favs = self.favourite.tracks()
        time.sleep(0.2)
        self.favArts = self.favourite.artists()
        time.sleep(0.2)
        self.favAlbs = self.favourite.albums()
        time.sleep(0.2)
        self.favPlys = self.favourite.playlists()
        # time.sleep(0.2)
        # self.favIds = self.favourite.videos()

    def on_login(self, button, email=None, password=None):
        global qualityC
        if email == None and password == None:
            email = self.emailEntry.get_text()
            password = self.pwdEntry.get_text()
            self.c = tidalapi.Config(tidalapi.Quality('LOSSLESS'))
            parser.set('misc', 'quality', '0')
            qualityC = '0'
            self.builder.get_object('em_lab').set_label(email)
        self.c = tidalapi.Config(tidalapi.Quality(qdict[qualityC]))
        self.session = tidalapi.Session(self.c)
        try:
            self.session.login(email, password)
            self.userID = self.session.user.id
            # Favourites
            self.favourite = tidalapi.user.Favorites(self.session, self.userID)
            ldg = futures.ThreadPoolExecutor(max_workers=2)
            ldg.submit(self.favver)
            ### End
            if confA == False and self.rmbe == True:
                print("Config written")
                parser.set('login', 'email', email)
                file = open("/home/%s/.config/htidal.ini" % user, "w+")
                parser.write(file)
                file.close()
                keyring.set_password('tidal', email, password)
                print("Saved")
            print("Login succesfull")
            self.bigStack.set_visible_child(self.builder.get_object("box"))
            stack.set_visible_child(self.builder.get_object("scrollHome"))
        except:
            print("Login failed")
            os.system('zenity --warning --text="Invalid email address or password!" --ellipsize')


class Setup:
    def __init__(self):
        print("Running Htidal...")

    def is_running(self, process):
        try: #Linux/Unix
            s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
        except: #Windows
            s = subprocess.Popen(["tasklist", "/v"],stdout=subprocess.PIPE)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False

    def get_desktop_environment(self):
        if sys.platform in ["win32", "cygwin"]:
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else: #Most likely either a POSIX system or something not much common
            desktop_session = os.environ.get("DESKTOP_SESSION")
            if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                        "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde", "ubuntu"]:
                    return desktop_session
                ## Special cases ##
                elif "xubuntu" in desktop_session:
                    return "xfce4"     
                elif desktop_session.startswith("lubuntu"):
                    return "lxde" 
                elif desktop_session.startswith("pop"):
                    return "gnome"
                elif desktop_session.startswith("pantheon"):
                    return "elementary"
                elif desktop_session.startswith("kubuntu"): 
                    return "kde"
                elif desktop_session.startswith("budgie"): 
                    return "budgie"
                elif desktop_session.startswith("razor"): # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                    return "windowmaker"
            else:
                if os.environ.get('KDE_FULL_SESSION') == 'true':
                    return "kde"
                elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                    if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                        return "gnome2"
                else:
                    return "unknown"

    def keyringer(self):
        kmode4 = keyring.backends.kwallet.DBusKeyringKWallet4()
        kmode5 = keyring.backends.kwallet.DBusKeyring()
        gmode = keyring.backends.SecretService.Keyring()
        DE = self.get_desktop_environment()
        if "kde" in DE or "qt" in DE:
            kver = os.popen("plasma-desktop --version").read()
            kver = kver.split("\n")
            kver = kver[2].replace("Plasma Desktop Shell: ", "")
            kver = kver.split(".")
            if kver[0] == 4:
                keyring.set_keyring(kmode4)
            else:
                keyring.set_keyring(kmode5)
        else:
            keyring.set_keyring(gmode)


if __name__ == "__main__":
    qdict = {'0' : 'LOSSLESS', '1' : 'HIGH', '2' : 'LOW'}
    # Dev/Use mode
    version = 'HTidal Beta 0.1 Snapshot 5'
    if os.path.exists('/home/daniel/GitRepos/htidal'):
        fdir = "/home/daniel/GitRepos/htidal/DEV_FILES/"
        print(fdir)
        os.chdir(fdir)
        print('Running in development mode.')
    else:
        fdir = "/usr/share/htidal/"
        print(fdir)
        os.chdir(fdir)
        print('Running in production mode.')
    # Translate
    APP = "htidal"
    WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
    LOCALE_DIR = os.path.join(WHERE_AM_I, 'translations/mo')
    locale.setlocale(locale.LC_ALL, locale.getlocale())
    locale.bindtextdomain(APP, LOCALE_DIR)
    gettext.bindtextdomain(APP, LOCALE_DIR)
    gettext.textdomain(APP)
    _ = gettext.gettext
    parser = ConfigParser()
    user = os.popen("who|awk '{print $1}'r").read()
    user = user.rstrip()
    user = user.split('\n')[0]
    if os.path.exists("/home/%s/.config/htidal.ini" % user):
        print('Configured already')
        confA = True
        parser.read("/home/%s/.config/htidal.ini" % user)
        emailC = parser.get('login', 'email')
        qualityC = parser.get('misc', 'quality')
    else:
        print("Not configured yet")
        confA = False
        emailC = ''
        qualityC = '0'
        parser.add_section('login')
        parser.add_section('misc')
    # GUI
    UI_FILE = "htidal.glade"
    Gst.init(None)
    sp = Setup()
    app = GUI()
    sp.keyringer()
    if confA:
        pwd = keyring.get_password('tidal', emailC)
        if pwd != None or pwd != "":
            app.on_login(0, emailC, pwd)
        else:
            app.bigStack.set_visible_child(app.builder.get_object("loginBox"))
    else:
        app.bigStack.set_visible_child(app.builder.get_object("loginBox"))
    Gtk.main()