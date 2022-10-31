from difflib import ndiff

import pandas as pd
import numpy as np

from src.dictionary import cluster, prepositions


def main():
    print("Start")
    df = load_data('C:/dev/repo//clustering/data/jobs.xlsx', "Tabelle1")
    df["job_lower"] = covert_to_lower_case(df, 'job')
    df["job_split"] = df["job_lower"].apply(split_and_reduce)

    print("## Job Frequency ##")
    print(print_job_frequency(df, 10))

    df['cluster_name'] = None
    df['distance'] = None

    # check if part of job title is already a cluster label (prioritized by order)
    df["cluster_name"] = df["job_split"].apply(find_job_in_cluster)
    df.loc[~df.cluster_name.isna(), 'distance'] = 0

    df['cluster_name'].loc[df['distance'].isna()], \
    df['distance'].loc[df['distance'].isna()] = zip(
        *df["job_split"].loc[df['distance'].isna()].apply(map_via_levenshtein)
    )

    print(df)


def load_data(path, sheet_name):
    return pd.read_excel(path, sheet_name=sheet_name)


# removes preposition from raw data
def split_and_reduce(job_str):
    words = job_str.split()
    for word in words:
        if word in prepositions:
            words.remove(word)
    return words


def covert_to_lower_case(df, column):
    return df[column].str.lower()


def print_job_frequency(df, count):
    freq = df.groupby(["job_lower"]).count()
    return freq.sort_values('job', ascending=False).head(count).to_string(header=False)


def map_via_levenshtein(jobs):
    best_match = ('', np.inf)
    for cluster_name, cluster_jobs in cluster.items():
        # print("cluster_name: ", cluster_name, " cluster_jobs: ", cluster_jobs)
        for item in cluster_jobs:
            for job in jobs:
                distance = levenshtein_distance(job, item)
                # print("item: ", item, " job: ", job, " distance: ", distance)
                if distance < best_match[1]:
                    best_match = (cluster_name, distance)
    return best_match[0], best_match[1]


def levenshtein_distance(str1, str2):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else:
            counter[edit_code] += 1
    distance += max(counter.values())
    return distance


def find_job_in_cluster(jobs):
    for key, value in cluster.items():
        if key in jobs:
            return key
    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
