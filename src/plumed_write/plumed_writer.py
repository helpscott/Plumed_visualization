import os


def write_plumed_file(filename, lines):
    with open(filename,"w") as f:
        for line in lines:
            f.write(line+"\n")
