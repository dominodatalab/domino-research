import tarfile
import os


def compress(path: str) -> str:
    outpath = path + ".tar.gz"
    with tarfile.open(outpath, "w:gz") as tar:
        tar.add(path, arcname=os.path.basename(path))
    return outpath
