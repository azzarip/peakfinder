class File:
    def __init__(self, fullpath):
        self.fullpath = fullpath
        import os
        self.dirpath = os.path.dirname(self.fullpath)
        self.filename = os.path.basename(fullpath).replace('.xlsx', '')

    def load(self):
        from pandas import ExcelFile
        xlsx = ExcelFile(self.fullpath, engine='openpyxl')

        self.profile_names = [
            name for name in xlsx.sheet_names if name.startswith("Profile")]
        data = {sheet: xlsx.parse(sheet) for sheet in self.profile_names}
        for name in data:
            df = data[name]
            df = df.iloc[1:, 1:]
            df.reset_index(drop=True, inplace=True)
            df.columns.values[0] = "Distance"
            df.columns.values[1] = "Height"

            from scipy.interpolate import UnivariateSpline
            spline = UnivariateSpline(df['Distance'], df['Height'], s=.001)
            df['Smooth'] = spline(df['Distance'])

            from numpy import gradient
            df['Derivative'] = gradient(df['Smooth'], df['Distance'])
            df['Derivative2'] = df['Derivative']**2
            df["Baseline"] = df["Derivative2"].apply(
                lambda x: x if x >= 0.1 else 0)
            data[name] = df
        self.data = data

    def findPeaks(self):
        from scipy.signal import find_peaks
        peaks_dict = {}
        for name in self.data:
            df = self.data[name]
            peaks, _ = find_peaks(df['Baseline'])
            peaks_df = df.iloc[peaks].copy()
            peaks_dict[name] = peaks_df
        self.peaks = peaks_dict

    def analyzePeaks(self):
        rows = []
        for name, df in self.peaks.items():
            rows.append({
                "name": name,
                "num_peaks": len(df),
                "avg_height": df["Height"].mean(),
                "std_height": df["Height"].std(),
                "max_height": df["Height"].max()
            })

        from pandas import DataFrame
        self.analyzedPeaks = DataFrame(rows)
        return self.analyzedPeaks

    def save(self):
        if not hasattr(self, 'analyzedPeaks') or self.analyzedPeaks is None:
            print('No Peaks found, run .analyzePeaks()')
            return

        import os
        new_filename = os.path.join(self.dirpath, f"peaks_{self.filename}.csv")

        self.analyzedPeaks.to_csv(new_filename, index=False)

    def getProfile(self, profile_id):
        return self.data['Profile ' + str(profile_id)]

    def getPeaks(self, profile_id):
        return self.peaks['Profile ' + str(profile_id)]
