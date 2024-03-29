from flask import Flask, render_template, request, jsonify
from gpiozero import LED
from pygame import mixer
from dataclasses import dataclass
from time import sleep


app = Flask(__name__)


@dataclass
class BoxItem:
    led: LED
    led_name: str
    led_color: str = 'grey'
    led_status: float = 0.0


class ColorManager:
    def __init__(self):
        self.counter = 0
        print('__init__()')
        self.current_led_status = 1.0
        self.gpios = ['GPIO13', 'GPIO6', 'GPIO5', 'GPIO22', 'GPIO27', 'GPIO17', 'GPIO4']
        self._max_counter = len(self.gpios)
        self.box_items = {}
        mixer.init()
        self.initialize_box_items()
        self.led_p_red = LED('GPIO26')
        self.led_p_blue = LED('GPIO19')
        self.police_mode = False
        self.led_a_red = LED('GPIO18')
        self.led_a_white = LED('GPIO23')
        self.ambulance_mode = False

    def inc_counter(self):
        print(f'inc_counter() counter: {self.counter}')
        print(f'inc_counter() current_led_status: {self.current_led_status}')
        if self.current_led_status == 1.0:
            print(f'inc_counter() current_led_status==1: {self.current_led_status}')
            self.counter += 1
            self.counter = min(self.counter, self._max_counter)
            self.current_led_status = 0.5
            print(f'inc_counter() current_led_status==1 new: {self.current_led_status}')
        elif self.current_led_status == 0.5:
            print(f'inc_counter() current_led_status==0.5: {self.current_led_status}')
            self.current_led_status = 1.0
            print(f'inc_counter() current_led_status==0.5 new: {self.current_led_status}')
        self.update_box_color()

    def dec_counter(self):
        print(f'dec_counter() counter: {self.counter}')
        print(f'dec_counter() current_led_status: {self.current_led_status}')
        if self.counter > 0:
            if self.current_led_status == 1.0:
                print(f'dec_counter() current_led_status==1: {self.current_led_status}')
                self.current_led_status = 0.5
                print(f'dec_counter() current_led_status==1 new: {self.current_led_status}')
            elif self.current_led_status == 0.5:
                print(f'dec_counter() current_led_status==0.5: {self.current_led_status}')
                self.current_led_status = 1.0
                self.counter -= 1
                self.counter = max(self.counter, 0)
                print(f'dec_counter() current_led_status==0.5 new: {self.current_led_status}')
            self.update_box_color()

    def initialize_box_items(self):
        # Initialize button colors to grey
        for gpio in self.gpios:
            self.box_items[gpio] = BoxItem(LED(gpio), gpio)

    def update_box_color(self):
        for id in range(self.counter):
            if id == 0:
                current_color = 'green'
            elif id == self._max_counter-1:
                current_color = 'red'
                mixer.music.load('Sirena_policii.mp3')
                mixer.music.play()
            else:
                current_color = 'yellow'
                mixer.music.load('Elektroshoker.mp3')
                mixer.music.play()
            cur_gpio = self.gpios[id]
            cur_box = self.box_items[cur_gpio]
            cur_box.led_status = 1.0
            cur_box.led_color = current_color
            print(f'update_box_color() id: {id}')
            print(f'update_box_color() current_led_status: {self.current_led_status}')
            if id == self.counter-1 and self.current_led_status == 0.5:
                cur_box.led_status = 0.5
                cur_box.led.blink(0.5, 0.5)
            else:
                cur_box.led.on()
        for id in range(self.counter, self._max_counter):
            cur_gpio = self.gpios[id]
            cur_box = self.box_items[cur_gpio]
            cur_box.led_status = 0
            cur_box.led_color = 'grey'
            cur_box.led.off()

    def toggle_police(self):
        if self.police_mode:
            self.police_mode = False
            self.led_p_red.off()
            self.led_p_blue.off()
        else:
            self.police_mode = True
            self.led_p_red.blink(0.5, 0.5)
            sleep(0.5)
            self.led_p_blue.blink(0.5, 0.5)
            mixer.music.load('Sirena.mp3')
            mixer.music.play()

    def toggle_ambulance(self):
        if self.ambulance_mode:
            self.ambulance_mode = False
            self.led_a_red.off()
            self.led_a_white.off()
        else:
            self.ambulance_mode = True
            self.led_a_red.blink(0.5, 0.5)
            sleep(0.5)
            self.led_a_white.blink(0.5, 0.5)
            mixer.music.load('Oshibka.mp3')
            mixer.music.play()


    def get_box_items(self):
        ui_dict = {}
        for item in self.box_items.values():
            ui_dict[item.led_name] = (item.led_color, item.led_status)
        return ui_dict

color_manager = ColorManager()

@app.route('/')
def index():
    return render_template('index_color_class.html', box_items=color_manager.get_box_items())

@app.route('/process_button/<button_id>', methods=['POST'])
def process_button(button_id):
    click_count = request.json.get('click_count', 0)
    # Update the color based on click count (for example, change to red on every even click)
    if button_id == 'better':
        color_manager.dec_counter()
    elif button_id == 'worse':
        color_manager.inc_counter()
    elif button_id == 'domofon':
        mixer.music.load('Domofon.mp3')
        mixer.music.play()
    elif button_id == 'police':
        color_manager.toggle_police()
    elif button_id == 'ambulance':
        color_manager.toggle_ambulance()
    # color_manager.update_box_color()
    print(color_manager.get_box_items())
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=False)

