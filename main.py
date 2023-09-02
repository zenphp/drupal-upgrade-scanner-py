import csv
import requests
from bs4 import BeautifulSoup
import lxml.etree
import json


class PatchData:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(PatchData, cls).__new__(cls)
            cls.instance.patch_data = json.load(open('composer.patches.json'))

        return cls.instance

    def is_patched(self, module_name):
        patch_key = "drupal/{}".format(module_name)
        if self.patch_data['patches'].keys().__contains__(patch_key):
            number_of_patches = len(self.patch_data['patches'][patch_key])
            custom = 0
            community = 0
            for patch_name in self.patch_data['patches'][patch_key]:
                if self.patch_data['patches'][patch_key][patch_name].startswith("http"):
                    community += 1
                else:
                    custom += 1

            return "Yes ({} patches [ {} contrib / {} custom ])".format(number_of_patches, community, custom)
        else:
            return "No"


def fetch_results(module_name):
    print("Processing: {}".format(module_name))
    url = "https://dev.acquia.com/drupal10/deprecation_status/projects?names={}".format(module_name)
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    tree = lxml.etree.HTML(str(soup))

    category = tree.xpath('//table[@data-drupal-selector]/tbody/tr[1]/td[2]/span/a')
    next_steps = tree.xpath('//table[@data-drupal-selector]/tbody/tr[1]/td[3]/a')

    if category:
        category = category[0].text
    else:
        category = "Not Found"

    if next_steps:
        next_steps = next_steps[0].text
    else:
        next_steps = "Not Found"

    print("   Result: {}".format(category))
    print("   Next Step: {}".format(next_steps))

    patch_data = PatchData()
    patched = patch_data.is_patched(module_name)

    return [module_name, url, category, next_steps, patched]


def scan_modules():
    results = []
    with open('info.csv') as csvfile:
        module_reader = csv.reader(csvfile, delimiter=',')
        for row in module_reader:
            if row[1] != "Name":
                results.append(fetch_results(row[1]))

    results = sorted(results, key=lambda x: (x[0]))

    with open('combined-results.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Name", "URL", "Status", "Notes", "Is Patched"])
        for row in results:
            writer.writerow(row)

    with open('not-found.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Name", "URL", "Status", "Notes", "Is Patched"])
        for row in results:
            if row[2] == "Not Found":
                writer.writerow(row)

    with open('d10-ready.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Name", "URL", "Status", "Notes", "Is Patched"])
        for row in results:
            if row[2] == "Release as Drupal 10-ready":
                writer.writerow(row)

    with open('needs-work.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Name", "URL", "Status", "Notes", "Is Patched"])
        for row in results:
            if row[2] != "Not Found" and row[2] != "Release as Drupal 10-ready":
                writer.writerow(row)

    with open('patched.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Name", "URL", "Status", "Notes", "Is Patched"])
        for row in results:
            if row[4].startswith("Yes"):
                writer.writerow(row)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scan_modules()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
