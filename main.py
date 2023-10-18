import PySimpleGUI as sg
import numpy as np
from PIL import Image
import pandas as pd
from math import ceil


# Function defining GUI layout
def gui():
    width = 640
    height = 360

    results_columns = [[sg.Push(),
                        sg.Text(text='Color', size=(14, 1), font=('Helvetica', 16), justification='center'),
                        sg.Text(text='Hex Code', size=(14, 1), font=('Helvetica', 16), justification='center'),
                        sg.Text(text='Percentage', size=(14, 1), font=('Helvetica', 16), justification='center'),
                        sg.Push()],
                       [sg.Push(),
                        sg.Multiline('', size=(15, 13), key='color', disabled=True, no_scrollbar=True,
                                     justification='center', background_color='white', font=('Helvetica', 14)),
                        sg.Multiline('', size=(15, 13), key='hex_code', disabled=True, no_scrollbar=True,
                                     justification='center', background_color='white', font=('Helvetica', 14)),
                        sg.Multiline('', size=(15, 13), key='percent', disabled=True, no_scrollbar=True,
                                     justification='center', background_color='white', font=('Helvetica', 14)),
                        sg.Push()]]

    run_column = [[sg.Push(),
                   sg.Text('Number of Colors', font=('Helvetica', 16)),
                   sg.Push()],
                  [sg.Push(),
                   sg.Slider(range=(0, 10), default_value=5, key='num_colors', orientation='h', font=('Helvetica', 12)),
                   sg.Push()],
                  [sg.Text('', font=('Helvetica', 16))],
                  [sg.Push(),
                   sg.Text('Color Delta', font=('Helvetica', 16)),
                   sg.Push()],
                  [sg.Push(),
                   sg.Slider(range=(1, 255), default_value=16, key='delta', orientation='h', font=('Helvetica', 12)),
                   sg.Push()],
                  [sg.Push(),
                   sg.Button(button_text='Run', key='run', font=('Helvetica', 18), enable_events=True,
                             size=(6, 1), pad=40),
                   sg.Push()]]

    layout = [
        [sg.FileBrowse(key='image_browse', enable_events=True)],
        [sg.Push(), sg.Image(filename='', key='image', enable_events=True, size=(800, 500)), sg.Push()],
        [sg.Column(results_columns), sg.Column(run_column)],

    ]

    window = sg.Window('Color Finder', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            values = ['', 0]
            break
        # When user chooses to browse for image, check for filetype errors and save filename
        if event == 'image_browse':
            path = values['image_browse']
            filetype = path.split('.')[-1]
            if filetype not in ['jpg', 'jpeg', 'png']:
                sg.popup('Incorrect filetype\nTry uploading a PNG or JPG')
                values.pop('image_browse')
                continue
            elif filetype != 'png':
                original_image = Image.open(path)
                path = f"{'.'.join(path.split('.')[:-1])}.png"
                original_image.save(path)
            # Check whether image is bigger than GUI area and resize it is
            resize_ratio = 1
            img_x, img_y = Image.open(path).size
            ratio_x = img_x / width
            ratio_y = img_y / height
            if ratio_x > 1 or ratio_y > 1:
                resize_ratio = max(ratio_x, ratio_y)
            window['image'].update(filename=path, subsample=ceil(resize_ratio))
        # When user clicks "Run", check for errors and if there are none, run the find_colors function
        if event == 'run':
            window['color'].update(value='', background_color='white')
            window['hex_code'].update(value='')
            window['percent'].update(value='')
            if values['image_browse'] == '':
                sg.popup('Please choose an image file')
                continue
            results = find_colors(path=values['image_browse'],
                                  num_colors=values['num_colors'],
                                  delta=values['delta'])
            # Display results of find_colors function in GUI
            for i in range(0, results.shape[0]):
                window['color'].print('', background_color=results['hex_code'][i])
                window['hex_code'].print(results['hex_code'][i])
                window['percent'].print(results['percent'][i])
                if i != results.shape[0] - 1:
                    window['color'].print('', background_color='white', font=('Helvetica', 2))
                    window['hex_code'].print('', font=('Helvetica', 2))
                    window['percent'].print('', font=('Helvetica', 2))


# Function to hold possible filetypes and check if the chosen file is available
def check_for_image(path: str) -> bool:
    filetype = path.split('.')[-1]
    if filetype not in ['jpg', 'jpeg', 'png']:
        return False
    else:
        return True


# Function to find the pixels in RGB format and convert to hex
def find_colors(path: str, num_colors: int, delta: int) -> pd.DataFrame:
    # Open the image and convert to array
    img = Image.open(path)
    img_array = np.array(img)
    # Round to the nearest integer based on user's "delta" choice
    img_array = ((img_array / delta).round(decimals=0) * delta).astype(int)
    img_array[img_array > 255] = 255
    # Create array of unique colors and their frequencies
    color_rgb, color_freq = np.unique(img_array.reshape(-1, 3), return_counts=True, axis=0)
    # Create DataFrame from color arrays, sort by frequency, and trim down to the number of colors the user specified
    freq_df = pd.DataFrame({'r': color_rgb[:, 0], 'g': color_rgb[:, 1], 'b': color_rgb[:, 2], 'freq': color_freq})
    top_colors = (freq_df.sort_values(by='freq', ascending=False).reset_index(drop=True).head(int(num_colors)))
    top_colors['percent'] = round(top_colors['freq'] / top_colors['freq'].sum() * 100, 2)
    # Convert the most common colors to hexcode
    for color in ['r', 'g', 'b']:
        top_colors[f'{color}_hex'] = top_colors[color].apply(lambda x: hex(x)[2:])
        top_colors[f'{color}_hex'] = top_colors[f'{color}_hex'].str.zfill(2)
    top_colors['hex_code'] = ("#" +
                              top_colors['r_hex'] +
                              top_colors['g_hex'] +
                              top_colors['b_hex'])
    # Return DataFrame with the most common colors, percentages, and hexcodes
    return top_colors


if __name__ == '__main__':
    # Initiate GUI
    gui()
