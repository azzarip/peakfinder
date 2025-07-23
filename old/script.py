import os
from File import File


def process(root_folder=None):
    if root_folder is None:
        root_folder = os.getcwd()

    for dirpath, dirnames, filenames in os.walk(root_folder):
        for file in filenames:
            if file.lower().endswith('.xlsx'):
                full_path = os.path.join(dirpath, file)
                print(f"Processing file: {full_path}")

                f = File(full_path)
                f.load()
                f.findPeaks()
                f.analyzePeaks()
                f.save()
