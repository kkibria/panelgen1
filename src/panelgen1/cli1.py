from pathlib import Path
from . import generate_addon, get_template_path
import sys
import shutil

def _cmd_init(target_dir: Path) -> None:
    target_dir = target_dir.resolve()
    print(f"[panelgen] init: {target_dir}")

    spec = "panel_spec.toml"
    spec_path = target_dir / spec
    addons_dir = target_dir / "scripts" / "addons"

    target_dir.mkdir(parents=True, exist_ok=True)
    addons_dir.mkdir(parents=True, exist_ok=True)

    if spec_path.exists():
        print(f"[panelgen] panel_spec.toml already exists at {spec_path}")
    else:
        shutil.copyfile(src=get_template_path()/spec, dst=spec_path)
        # spec_path.write_text(SAMPLE_TOML, encoding="utf-8")
        print(f"[panelgen] wrote sample spec: {spec_path}")

    print(f"[panelgen] addons dir: {addons_dir}")


def _cmd_gen() -> None:
    # uses current working directory as project root
    generate_addon.main()


def main() -> None:
    """
    Minimal CLI:

      python -m panelgen1 init <directory>
      python -m panelgen1 gen
    """
    args = sys.argv[1:]

    if not args or args[0] in {"-h", "--help", "help"}:
        print("Usage:")
        print("  python -m panelgen1 init <directory>")
        print("  python -m panelgen1 gen")
        return

    cmd = args[0]

    if cmd == "init":
        if len(args) < 2:
            print("panelgen1: 'init' requires a <directory>")
            return
        _cmd_init(Path(args[1]))
    elif cmd == "gen":
        _cmd_gen()
    else:
        print(f"panelgen1: unknown command '{cmd}'")
        print("Use: init <directory> or gen")

