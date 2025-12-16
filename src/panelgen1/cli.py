import os
import argparse
import sys
import shutil

from pathlib import Path
from . import generate_addon, get_template_path

def _cmd_init(targetdir, **kwargs) -> None:
    targetdir=Path(targetdir)
    targetdir = targetdir.resolve()
    print(f"[panelgen] init: {targetdir}")

    spec = "panel_spec.toml"
    spec_path = targetdir / spec
    addons_dir = targetdir / "scripts" / "addons"

    targetdir.mkdir(parents=True, exist_ok=True)
    addons_dir.mkdir(parents=True, exist_ok=True)

    if spec_path.exists():
        print(f"[panelgen] panel_spec.toml already exists at {spec_path}")
    else:
        shutil.copyfile(src=get_template_path()/spec, dst=spec_path)
        # spec_path.write_text(SAMPLE_TOML, encoding="utf-8")
        print(f"[panelgen] wrote sample spec: {spec_path}")

    print(f"[panelgen] addons dir: {addons_dir}")

def _cmd_gen(tomlpath, **kwargs) -> None:
    # uses current working directory as project root
    generate_addon.main(tomlpath)

def basedir(kwargs):
    basedir = os.path.expanduser(f"~/.{kwargs['app']}/")
    os.makedirs(basedir, exist_ok=True)
    return basedir

def main():
    params = {"app": "panelgen"}

    parser = argparse.ArgumentParser(
        prog=params["app"],
        description='Creates blender add-on',
        epilog=f'Go to https://github.com/kkibria/panelgen1 for README/instructions')

    subparsers = parser.add_subparsers(title="commands", dest="command", help="Available commands") #

    parser_init = subparsers.add_parser("init", help="Initialize Add-on Project")
    parser_init.add_argument("targetdir", type=str, help="Project Path")
    parser_init.set_defaults(func=_cmd_init)

    parser_gen = subparsers.add_parser("gen", help="Generate python UI file")
    parser_gen.add_argument("--tomlpath", type=str, default="panel_spec.toml", help="toml spec file path")
    parser_gen.set_defaults(func=_cmd_gen)

    args = parser.parse_args()
    params = params | vars(args)
    print(params)

    set_warnigs_hook()
    try:
        if hasattr(args, "func"):
            args.func(**params)
        else:
            # If no subcommand is given (e.g., just running './myprogram.py'), print help
            parser.print_help()
    except Exception as e:
        print(f'{e.__class__.__name__}:', *e.args)
        return 1
    
    return 0

def set_warnigs_hook():
    import sys
    import warnings
    def on_warn(message, category, filename, lineno, file=None, line=None):
        print(f'Warning: {message}', file=sys.stderr)
    warnings.showwarning = on_warn

if __name__ == '__main__':
    sys.exit(main())
