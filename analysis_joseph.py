import os
import pandas as pd
import time
start_time = time.perf_counter()

data_dir = 'data'
analysis_dir = 'analysis_joseph'


class Profile:
    def __init__(self, df):
        self.df = df

    def smooth(self):
        from scipy.interpolate import UnivariateSpline
        spline = UnivariateSpline(
            self.df['distance'], self.df['height'], s=.001)
        self.df['smooth'] = spline(self.df['distance'])

    def derive(self):
        from numpy import gradient
        self.df['derivative'] = gradient(
            self.df['smooth'], self.df['distance'])
        self.df['derivative2'] = self.df['derivative']**2
        self.df["baseline"] = self.df["derivative2"].apply(
            lambda x: x if x >= 0.1 else 0)

    def findPeaks(self):
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(self.df['baseline'])
        peaks_df = self.df.iloc[peaks].copy()
        return peaks_df[['distance', 'height']]


class File:
    def __init__(self, fullpath):
        self.fullpath = fullpath
        import os
        self.dirpath = os.path.dirname(self.fullpath)
        self.filename = os.path.basename(fullpath).replace('.csv', '')

    def load(self):
        from pandas import read_csv
        df = read_csv(self.fullpath).dropna()

        profiles = {}
        num_profiles = df.shape[1] // 2

        for i in range(num_profiles):
            dist_col = df.columns[2 * i]
            height_col = df.columns[2 * i + 1]
            profile_df = df[[dist_col, height_col]].copy()
            profile_df.columns = ['distance', 'height']
            profiles[f'profile_{i + 1}'] = Profile(profile_df)

        self.profiles = profiles
        return self

    def getPeaks(self):
        results = []
        for name, profile in self.profiles.items():
            profile.smooth()
            profile.derive()
            peaks = profile.findPeaks()
            results.append({
                "name": name,
                "num_peaks": len(peaks),
                "avg_height": peaks["height"].mean(),
                "std_height": peaks["height"].std(),
                "max_height": peaks["height"].max()
            })

        import pandas as pd
        df = pd.DataFrame(results)
        average_row = df.mean(numeric_only=True).to_frame().T
        average_row['name'] = ['average']
        return pd.concat([df, average_row])


for root, dirs, files in os.walk(data_dir):

    rel_path = os.path.relpath(root, data_dir)
    analysis_path = os.path.join(analysis_dir, rel_path)

    os.makedirs(analysis_path, exist_ok=True)

    for file in files:
        if file.endswith('.csv'):
            data_file_path = os.path.join(root, file)
            analysis_file_path = os.path.join(analysis_path, file)

            try:
                f = File(data_file_path).load()
                df_peaks = f.getPeaks()  # Must return a pandas DataFrame
                df_peaks.to_csv(analysis_file_path, index=False)
                print(f"Processed: {data_file_path} -> {analysis_file_path}")
            except Exception as e:
                print(f"Error processing {data_file_path}: {e}")
elapsed = time.perf_counter() - start_time
print('\n')
print(f"Elapsed time: {int(elapsed)} seconds")
