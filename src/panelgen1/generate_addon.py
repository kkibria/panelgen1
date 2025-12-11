import tomllib  # Python 3.11+; for older versions use `tomli` and import that instead
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


# ─────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────

def operator_idname_to_class(idname: str) -> str:
    # "myaddon.dummy_operator" -> "MYADDON_OT_dummy_operator"
    parts = idname.split(".")
    if len(parts) == 2:
        prefix, name = parts
        return f"{prefix.upper()}_OT_{name}"
    return idname.replace(".", "_").upper()


def panel_idname_to_class(idname: str) -> str:
    # "MYADDON_PT_main" -> "MYADDON_PT_main" (already in Blender style)
    return idname


def owner_to_bpy(owner: str) -> str:
    # Map "Scene" -> "bpy.types.Scene"
    return f"bpy.types.{owner}"


def owner_to_context(owner: str) -> str:
    # Map "Scene" -> "context.scene"
    return f"context.{owner.lower()}"


def python_literal(value):
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, bool):
        return "True" if value else "False"
    # int / float / etc.
    return repr(value)


# ─────────────────────────────────────────
# Spec loading and context prep
# ─────────────────────────────────────────

def load_spec(path: Path) -> dict:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data


def prepare_context(spec: dict) -> dict:
    addon = spec["addon"]

    # ───── Properties ─────
    properties = []
    prop_imports_set = set()
    props_by_id = {}

    for p in spec.get("properties", []):
        p_type = p["type"]  # e.g. "StringProperty"
        func_name = p_type

        prop_imports_set.add(p_type)

        owner = p["owner"]          # "Scene"
        owner_bpy = owner_to_bpy(owner)        # "bpy.types.Scene"
        context_expr = owner_to_context(owner) # "context.scene"

        default = p.get("default", "")
        default_code = python_literal(default)

        prop_ctx = {
            "id": p["id"],
            "owner": owner,
            "owner_bpy": owner_bpy,
            "context_expr": context_expr,
            "attr": p["attr"],
            "func_name": func_name,
            "name": p.get("name", p["attr"]),
            "description": p.get("description", ""),
            "default_code": default_code,
        }
        properties.append(prop_ctx)
        props_by_id[p["id"]] = prop_ctx

    prop_imports = sorted(prop_imports_set)

    # ───── Operators ─────
    ops_by_idname = {}
    operators = []

    for op_spec in spec.get("operators", []):
        idname = op_spec["idname"]
        class_name = operator_idname_to_class(idname)
        options = op_spec.get("options", [])
        if not options:
            options_code = "set()"
        else:
            # e.g. {"REGISTER", "UNDO"}
            opts = ", ".join(f'"{o}"' for o in options)
            options_code = "{" + opts + "}"

        op_ctx = {
            "idname": idname,
            "label": op_spec["label"],
            "description": op_spec.get("description", ""),
            "class_name": class_name,
            "options_code": options_code,
        }
        operators.append(op_ctx)
        ops_by_idname[idname] = op_ctx

    # ───── Panels ─────
    panels = []

    for p in spec.get("panels", []):
        idname = p["idname"]
        class_name = panel_idname_to_class(idname)

        # Attach operator info for panel
        panel_ops = []
        for pop in p.get("operators", []):
            op_idname = pop["idname"]
            # label for button: explicit label or operator label
            label = pop.get("label") or ops_by_idname.get(op_idname, {}).get("label", op_idname)
            panel_ops.append({
                "idname": op_idname,
                "label": label,
            })

        # Attach properties for this panel
        panel_props = []
        for prop_id in p.get("properties", []):
            prop_ctx = props_by_id.get(prop_id)
            if prop_ctx is None:
                continue
            panel_props.append({
                "context_expr": prop_ctx["context_expr"],
                "attr": prop_ctx["attr"],
            })

        panel_ctx = {
            "idname": idname,
            "label": p["label"],
            "space_type": p.get("space_type", "SEQUENCE_EDITOR"),
            "region_type": p.get("region_type", "UI"),
            "category": p.get("category", addon.get("tab_name", "Tools")),
            "class_name": class_name,
            "operators": panel_ops,
            "properties": panel_props,
        }
        panels.append(panel_ctx)

    ctx = {
        "addon": addon,
        "properties": properties,
        "prop_imports": prop_imports,
        "operators": operators,
        "panels": panels,
    }
    return ctx


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    here = Path(__file__).parent
    # spec_path = here / "panel_spec.toml"
    spec_path = here.parent.parent / "panel_spec.toml"
    tmpl_dir = here / "templates"
    # output_path = here / "my_panel_addon.py"  # Single-file Blender add-on
    output_path = here.parent.parent / "scripts" / "addons" / "my_panel_addon.py"  # Single-file Blender add-on

    spec = load_spec(spec_path)
    ctx = prepare_context(spec)

    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("addon_single.jinja2")
    code = template.render(**ctx)

    output_path.write_text(code, encoding="utf-8")
    print(f"Generated add-on: {output_path}")


if __name__ == "__main__":
    main()
