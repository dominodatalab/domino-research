import tarfile
import os


def compress(model_path: str, outpath: str) -> str:
    with tarfile.open(outpath, "w:gz") as tar:
        tar.add(model_path, arcname=os.path.basename(model_path))
    return outpath
