import os
import json
import numpy as np
import sys


def read_labels(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)


def process_bounding_boxes(npy_file, labels):
    bbox_data = np.load(npy_file, allow_pickle=True)
    processed_boxes = []
    for bbox in bbox_data:
        label = labels[str(bbox['semanticId'])]['class']
        if not (label == "background"):
            x_min, y_min, x_max, y_max = int(bbox['x_min']), int(bbox['y_min']), int(bbox['x_max']), int(bbox['y_max'])
            width, height = x_max - x_min, y_max - y_min
            processed_boxes.append({
                "label": label,
                "x": x_min,
                "y": y_min,
                "width": width,
                "height": height
            })
    return processed_boxes


def main(input_folder):
    output_data = {}
    render_number = 0

    while True:
        image_file = f'rgb_{str(render_number).zfill(4)}.png'
        bbox_file = f'bounding_box_2d_tight_{str(render_number).zfill(4)}.npy'
        label_file = f'bounding_box_2d_tight_labels_{str(render_number).zfill(4)}.json'

        if not (os.path.exists(os.path.join(input_folder, bbox_file)) and os.path.exists(os.path.join(input_folder, label_file))):
            print("Complete or missing file(s): " + str(render_number))
            break

        labels = read_labels(os.path.join(input_folder, label_file))
        processed_boxes = process_bounding_boxes(os.path.join(input_folder, bbox_file), labels)
        output_data[image_file] = processed_boxes

        render_number += 1

    with open(os.path.join(input_folder, 'bounding_boxes.labels'), 'w') as file:
        json.dump({
            "version": 1,
            "type": "bounding-box-labels",
            "boundingBoxes": output_data
        }, file, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python basic_writer_to_pascal_voc.py <input_folder>")
    else:
        main(sys.argv[1])
