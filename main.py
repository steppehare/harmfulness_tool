from flask import Flask, render_template, request, jsonify
from gpiozero import LED
from pygame import mixer
from dataclasses import dataclass


app = Flask(__name__)


@dataclass
class BoxItem:
    led: LED
    led_name: str
    led_color: str = 'grey'
    led_status: float = 0.0
    led_name2: str = ''


class ColorManager:
    def __init__(self):
        self.counter = 0
        self.gpios = ['GPIO13', 'GPIO6', 'GPIO5', 'GPIO22', 'GPIO27', 'GPIO17', 'GPIO4']
        self._max_counter = len(self.gpios)
        self.box_items = {}
        mixer.init()
        self.initialize_box_items()

    def inc_counter(self):
        self.counter += 1
        self.counter = min(self.counter, self._max_counter)

    def dec_counter(self):
        self.counter -= 1
        self.counter = max(self.counter, 0)

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
                mixer.music.load('Oshibka.mp3')
                mixer.music.play()
            else:
                current_color = 'yellow'
                mixer.music.load('Elektroshoker.mp3')
                mixer.music.play()
            cur_gpio = self.gpios[id]
            cur_box = self.box_items[cur_gpio]
            cur_box.led_status = 1
            cur_box.led_color = current_color
            cur_box.led.on()
        for id in range(self.counter, self._max_counter):
            cur_gpio = self.gpios[id]
            cur_box = self.box_items[cur_gpio]
            cur_box.led_status = 0
            cur_box.led_color = 'grey'
            cur_box.led.off()

    def get_box_items(self):
        ui_dict = {}
        for item in self.box_items.values():
            ui_dict[item.led_name] = item.led_color
        return ui_dict

color_manager = ColorManager()

@app.route('/')
def index():
    return render_template('index_color_class.html', box_items=color_manager.get_box_items())

@app.route('/process_button/<button_id>', methods=['POST'])
def process_button(button_id):
    click_count = request.json.get('click_count', 0)
    # Update the color based on click count (for example, change to red on every even click)
    new_color = 'red' if button_id == 'worse' else 'grey'
    if button_id == 'better':
        new_color ='grey'
        color_manager.dec_counter()
    else:
        new_color = 'red'
        color_manager.inc_counter()
    print(f'Set color {new_color}')
    color_manager.update_box_color()
    print(color_manager.get_box_items())
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=False)

