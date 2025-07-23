import os
import time


class Image:
    def __init__(self, file_path: str, sample):
        self.full_path = file_path
        self.name = os.path.basename(file_path)
        self.sample = sample

    def __repr__(self) -> str:
        return self.name

    def extract(self):
        import pandas as pd
        xlsx = pd.ExcelFile(self.full_path, engine='openpyxl')

        self.profile_names = [
            name for name in xlsx.sheet_names if name.startswith("Profile")]
        self.profiles = pd.DataFrame()
        data = {sheet: xlsx.parse(sheet) for sheet in self.profile_names}

        for name in data:
            number = name.replace("Profile ", "")
            df = data[name]
            df = df.iloc[1:, 1:]
            df.columns.values[0] = f"Distance {number}"
            df.columns.values[1] = f"Height {number}"
            self.profiles = pd.concat(
                [self.profiles, df.reset_index(drop=True)], axis=1)

        return self.profiles


class Sample:
    def __init__(self, full_path: str, experiment):
        self.full_path = full_path
        self.path = os.path.dirname(full_path)
        self.name = os.path.basename(self.path)
        self.experiment = experiment
        self.images = []

    def __repr__(self):
        return f"{self.experiment} - {self.name}'"

    def loadImages(self):
        reports_path = os.path.join(self.path, 'Reports')
        self.images = []

        if os.path.isdir(reports_path):
            for file in os.listdir(reports_path):
                if file.endswith('.xlsx') and not file.startswith('.') and not file.startswith('~'):
                    file_path = os.path.join(reports_path, file)
                    self.images.append(Image(file_path, self))

        return self


class Experiment:
    import os

    def __init__(self, name: str):
        self.name = name
        self.folder_path = os.path.join('raw', self.name)
        self.samples = []

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def load(self):
        self.samples = []
        if os.path.isdir(self.folder_path):
            for root, dirs, files in os.walk(self.folder_path):
                for dir_name in dirs:
                    if dir_name == 'Reports':
                        full_path = os.path.join(root, dir_name)
                        sample = Sample(full_path, self)
                        sample.loadImages()
                        self.samples.append(sample)

    def copy(self):
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        experiment_folder = os.path.join(data_folder, self.name)
        if not os.path.exists(experiment_folder):
            os.makedirs(experiment_folder)

        print('Experiment: ' + self.name)
        for sample in self.samples:
            sample_folder = os.path.join(experiment_folder, sample.name)
            if not os.path.exists(sample_folder):
                os.makedirs(sample_folder)

            print('  sample: ' + sample.name)
            for image in sample.images:
                file_path = os.path.join(
                    sample_folder, image.name).replace('xlsx', 'csv')
                data = image.extract()
                data.to_csv(file_path, index=False)


data_folder = 'data'

if os.path.exists(data_folder):
    shutil.rmtree(data_folder)
    print(f"Removed existing folder: {data_folder}")

start_time = time.perf_counter()
for name in os.listdir('raw'):
    if os.path.isdir(os.path.join('raw', name)):
        experiment = Experiment(name)
        experiment.load()
        experiment.copy()
elapsed = time.perf_counter() - start_time
print(f"Elapsed time: {int(elapsed)} seconds")
