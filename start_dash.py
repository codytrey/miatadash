from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty
from kivy.garden.mapview import MapView, MapMarker
from kivy.garden.gauge import Gauge
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from datetime import datetime
import glob
from os import sep
import json
import googlemaps

with open("." + sep + "etc" + sep + "conf.json", "r") as f:
    conf = json.load(f)

Builder.load_string('''
<CustomLayout>
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
<RootWidget>
    CustomLayout:
        AsyncImage:
            source: './img/wallpaper-cf1-1280x800.png'
        NavLayout:
            size_hint: 1.0, 0.75
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
            AddressInput:
                id: addrinput
                hint_text: 'Enter Address'
                size_hint: 0.7, 0.09
                pos_hint: {'center_x': 0.62, 'center_y': 0.86}
            NavigateButton:
                id: navbutton
                text: 'Navigate'
                size_hint: 0.25, 0.09
                pos_hint: {'center_x': 0.125, 'center_y': 0.86}
                on_press: self.on_press
            Map:
                id: map
                size_hint: 0.75, 0.67
                pos_hint: {'center_x': 0.62, 'center_y': 0.44}
                zoom: 15
            Speedo:
                size_hint: 0.45, 0.45
                pos_hint: {'center_x': 0.26, 'center_y': 0.75}
        MusicPlayer:
            id: musicplayer
            size_hint: 1, 0.25
            pos_hint: {'center_x': 0.5, 'center_y': 0.1225}
            MuteButton:
                size_hint: 0.16, 0.16
                pos_hint: {'center_x': .41, 'center_y': 0.5}
            VolumeSlider:
                id: VolSlider
                value_track: True
                value_track_color: 1, 0, 0, 1
                min: 0
                max: 100
                step: 1
                value: 25
                size_hint: 0.4, 0.2
                pos_hint: {'center_x': 0.2, 'center_y': 0.5}
                on_value: self.OnSliderChange(self.value_normalized)
            VolumeLable:
                pos_hint: {'center_x': 0.45, 'center_y': 0.5}
                color: 1, 1, 1, 1
                text: str(VolSlider.value).split(".")[0]
            PrevButton:
                text: 'Prev'
                pos_hint: {'center_x': 0.525, 'center_y': 0.5}
                size_hint: .1225, .25
                on_press: musicplayer.prev
            PlayButton:
                text: 'Play'
                pos_hint: {'center_x': 0.625, 'center_y': 0.5}
                size_hint: .125, .25
            NextButton:
                text: 'Next'
                pos_hint: {'center_x': 0.725, 'center_y': 0.5}
                size_hint: .1225, .25
                on_press: musicplayer.next
            FileName:
                text: self.parent.filename
                pos_hint: {'center_x': 0.9, 'center_y': 0.5}
''')


class RootWidget(BoxLayout):
    pass


class VolumeLable(Label):
    id = 'volumelabel'


class VolumeSlider(Slider):
    def OnSliderChange(self, value):
        if self.parent.sound is not None:
            self.parent.sound.volume = value


class CustomLayout(RelativeLayout):
    pass


class MuteButton(ToggleButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MuteButton, self).__init__(**kwargs)
        self.source = './img/volume.png'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = './img/volume.png'
            if self.parent.sound is not None:
                self.parent.sound.volume = self.parent.volume
        else:
            self.source = './img/volume-off.png'
            if self.parent.sound is not None:
                self.parent.sound.volume = 0


class MusicPlayer(RelativeLayout):
    filename = StringProperty('')
    sound = ObjectProperty(None, allownone=True)
    volume = NumericProperty(1.0)
    filelist = ListProperty(glob.glob("." + sep + "audio" + sep + "*"))
    # sound = SoundLoader.load(glob.glob("." + sep + "audio" + sep + "*")[0])

    def __init__(self, **kwargs):
        super(MusicPlayer, self).__init__(**kwargs)
        Clock.schedule_once(self.loadsound, 5)

    def loadsound(self, dt):
        self.sound = SoundLoader.load(glob.glob("." + sep + "audio" + sep + "*")[0])

    def next(self):
        tmp = self.filelist.pop(0)
        self.filelist.append(tmp)
        self.sound.stop()
        self.sound.unload()
        self.sound = SoundLoader.load(self.filelist[0])
        self.filename = self.filelist[0].split(sep)[-1]
        self.sound.play()

    def prev(self):
        tmp = self.filelist.pop(-1)
        self.filelist.insert(0, tmp)
        self.sound.stop()
        self.sound.unload()
        self.sound = SoundLoader.load(self.filelist[0])
        self.filename = self.filelist[0].split(sep)[-1]
        self.sound.play()

    def play(self):
        if self.sound is None:
            self.sound = SoundLoader.load(self.filelist[0])
        self.sound.play()
        self.filename = self.filelist[0].split(sep)[-1]

    def pause(self):
        self.sound.stop()


class NextButton(Button):

    def on_press(self):
        self.parent.next()


class PrevButton(Button):

    def on_press(self):
        self.parent.prev()


class PlayButton(ToggleButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(PlayButton, self).__init__(**kwargs)
        self.text = 'Play'

    def on_state(self, widget, value):
        if value == 'down':
            self.text = 'Pause'
            self.parent.play()
        else:
            self.text = 'Play'
            self.parent.pause()


class FileName(Label):
    pass


class NavLayout(RelativeLayout):
    address = StringProperty(None)

    def get_nav_results(self):
        gmaps = googlemaps.Client(key=conf['gmaps']['apikey'])
        reverse_geocode_result = gmaps.reverse_geocode((conf['gmaps']['dummystart']['lat'], conf['gmaps']['dummystart']['lon']))
        address = ""
        x = 0
        while x < len(reverse_geocode_result[0]['address_components']):
            address = address + reverse_geocode_result[0]['address_components'][x]['long_name']
            address = address + " "
            x += 1
        print(address)
        now = datetime.now()
        directions_result = gmaps.directions(address,
                                             self.address,
                                             mode="driving",
                                             departure_time=now)
        print(directions_result)


class Map(MapView):

    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        self.lat = conf['gmaps']['dummystart']['lat']
        self.lon = conf['gmaps']['dummystart']['lon']


class AddressInput(TextInput):

    def __init__(self, **kwargs):
        super(AddressInput, self).__init__(**kwargs)
        self.bind(text=self.on_text)

    def on_text(self, instance, value):
        self.parent.address = value


class NavigateButton(Button):

    def on_press(self):
        self.parent.get_nav_results()


class Speedo(Gauge):
    pass


class MainApp(App):

    def build(self):
        return RootWidget()


if __name__ == '__main__':
    MainApp().run()
