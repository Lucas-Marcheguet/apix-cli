from apixdev.core.settings import settings, vars
from apixdev.core.tools import bytes_to_json, dict_to_dataframe, run_external_command

# pylint: disable=C0103


class Images:
    def __init__(self):
        pass

    @staticmethod
    def ls():
        """List local docker images related to ApiX repository."""

        repository = settings.get_var("docker.repository")

        res = run_external_command(vars.DOCKER_LIST_IMAGES)
        data = bytes_to_json(res)
        df = dict_to_dataframe(data)
        df2 = df.query(f"Repository == '{repository}'")

        # TODO: Return image size
        # df2[["Tag", "Size"]].to_dict(orient="records")

        res = sorted(df2["Tag"].tolist())

        return res
