import config as Config

class File_Reader:
    def read(file_path):
        file = open(file_path, 'r')
        lines = file.read().split('\n')
        file.close()
        return lines

def build_path(filename):
    return Config.IMPORT_BASE + filename