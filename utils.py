import json
import os

def read_json(path: str):
    infile = open(path, "r")
    return json.loads(infile.read())

def read_files(path: str):
    file_list = []
    for root, folders, docs in os.walk(path):
        file_list.extend( [os.path.join(root, doc) for doc in docs if '.json' in doc] )

    return file_list

def rename_files(folder: str):
    file_list = read_files(folder)

    for path in file_list:
        data = read_json(path)
        rank: int = data['Rank']
        deceased: bool = True if 'DOD' in data else False
        
        prefix = None
        if rank < 10:
            prefix = '00'
        elif rank < 100:
            prefix = '0'
        else: 
            prefix = ''

        rank_str = str.format("{0}{1}", prefix, rank)
        new_filename = str.format("./JSON/{0}{1}_{2}", ('Deceased/' if deceased else ''), rank_str, path.replace('./JSON/', ''))
        contents = json.dumps(data)
        with open(new_filename, 'w') as new_file:
            new_file.write(contents)
            new_file.close()


# rename_files('./JSON/')