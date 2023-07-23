import subprocess

import pandas

from apixdev.core.settings import Settings
from apixdev.core.tools import bytes_to_json


class Images:
    def __init__(self):
        pass

    @staticmethod
    def ls():
        settings = Settings()
        repository = settings.get_var("docker.repository")

        args = ["docker", "image", "ls", "--format", "json"]
        res = subprocess.check_output(args)
        data = bytes_to_json(res)

        df = pandas.DataFrame(data)
        df2 = df.query(f"Repository == '{repository}'")
        # df2[["Tag", "Size"]].to_dict(orient="records")
        res = sorted(df2["Tag"].tolist())

        return res
