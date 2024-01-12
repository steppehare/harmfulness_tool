from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class ColorManager:
    def __init__(self):
        self.counter = 0
        self._max_counter = 10
        self.box_colors = {}
        self.initialize_button_colors()

    def inc_counter(self):
        self.counter += 1
        self.counter = min(self.counter, self._max_counter)

    def dec_counter(self):
        self.counter -= 1
        self.counter = max(self.counter, 0)

    def initialize_button_colors(self):
        # Initialize button colors to grey
        for i in range(0, self._max_counter):
            self.box_colors[f'box{i}'] = 'grey'

    def update_box_color(self):
        for id in range(self.counter):
            if id == 0:
                current_color = 'green'
            elif id == self._max_counter-1:
                current_color = 'red'
            else:
                current_color = 'yellow'
            self.box_colors[f'box{id}'] = current_color
        for id in range(self.counter, self._max_counter):
            self.box_colors[f'box{id}'] = 'grey'

    def get_box_colors(self):
        return self.box_colors

color_manager = ColorManager()

@app.route('/')
def index():
    return render_template('index_color_class.html', box_colors=color_manager.get_box_colors())

@app.route('/process_button/<button_id>', methods=['POST'])
def process_button(button_id):
    click_count = request.json.get('click_count', 0)
    # Update the color based on click count (for example, change to red on every even click)
    new_color = 'red' if button_id == 'btn2' else 'grey'
    if button_id == 'btn1':
        new_color ='grey'
        color_manager.dec_counter()
    else:
        new_color = 'red'
        color_manager.inc_counter()
    print(f'Set color {new_color}')
    color_manager.update_box_color()
    print(color_manager.get_box_colors())
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)

