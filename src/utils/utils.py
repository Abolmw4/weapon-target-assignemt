import yaml


def read_config_file(file_src: str="configs/scenario1.yaml") -> dict:
    with open(file_src, 'r') as stream:
        try:
            configs = yaml.safe_load(stream)
            # print(configs)
            return configs
        except yaml.YAMLError as exc:
            print(exc)
