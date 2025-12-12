def get_template_path():
    from importlib.resources import files
    return files(__package__).joinpath(f"templates")
