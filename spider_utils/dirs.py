import os

def running_dir(*dir):
    return os.path.join(os.path.abspath("."), *dir)

def file_dir(file,*dir):
    return os.path.join(os.path.dirname(os.path.abspath(file)), *dir)

def temp_dir(*dir):
    if not os.path.exists(running_dir("temp")):
        os.mkdir(running_dir("temp"))
    return running_dir("temp", *dir)
