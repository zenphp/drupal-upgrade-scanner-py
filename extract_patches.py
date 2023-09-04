import json
import csv


def main():
    patch_data = json.load(open('composer.patches.json'))
    with open('composer.patches.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['module', 'description', 'url/path'])

        for modulename in patch_data['patches']:
            for patch_name in patch_data['patches'][modulename]:
                patch = patch_data['patches'][modulename][patch_name]
                writer.writerow([modulename, patch_name, patch])


if __name__ == '__main__':
    main()