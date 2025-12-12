import os
from pathlib import Path
import tomllib  # Python 3.11+
from jinja2 import Environment, FileSystemLoader
from . import get_template_path


# ─────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────

def operator_idname_to_class(idname: str) -> str:
    parts = idname.split(".")
    if len(parts) == 2:
        prefix, name = parts
        return f"{prefix.upper()}_OT_{name}"
    return idname.replace(".", "_").upper()


def panel_idname_to_class(idname: str) -> str:
    return idname


def owner_to_bpy(owner: str) -> str:
    return f"bpy.types.{owner}"


def owner_to_context(owner: str) -> str:
    return f"context.{owner.lower()}"


def python_literal(value):
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, bool):
        return "True" if value else "False"
    return repr(value)


# ─────────────────────────────────────────
# Spec loading and context prep
# ─────────────────────────────────────────

def load_spec(path: Path) -> dict:
    print(f"[panelgen] Loading TOML from: {path}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def prepare_context(spec: dict) -> dict:
    addon = spec["addon"]

    # ───── Properties ─────
    properties = []
    prop_imports_set = set()
    props_by_id = {}

    for p in spec.get("properties", []):
        p_type = p["type"]  # e.g. "StringProperty", "IntProperty", "EnumProperty"
        func_name = p_type
        prop_imports_set.add(p_type)

        owner = p["owner"]          # "Scene"
        owner_bpy = owner_to_bpy(owner)
        context_expr = owner_to_context(owner)

        default = p.get("default", "")
        default_code = python_literal(default)

        # Extra args: min/max etc for Int/Float; items for Enum
        extra_args = []

        if p_type in ("IntProperty", "FloatProperty"):
            for key in ("min", "max", "soft_min", "soft_max", "step"):
                if key in p:
                    extra_args.append(f"{key}={python_literal(p[key])}")

        if p_type == "EnumProperty":
            items = p.get("items", [])
            if items:
                tuple_strs = []
                for item in items:
                    ident = item["identifier"]
                    name = item.get("name", ident)
                    desc = item.get("description", "")
                    tuple_strs.append(f'("{ident}", "{name}", "{desc}")')
                items_code = "[" + ", ".join(tuple_strs) + "]"
                extra_args.append(f"items={items_code}")

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
            "extra_args": extra_args,
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
            opts = ", ".join(f'"{o}"' for o in options)
            options_code = "{" + opts + "}"

        body = op_spec.get("body")

        if not body:
            # Default body if none provided
            body = (
                f"self.report({{'INFO'}}, \"Operator {idname} executed.\")\n"
                "return {'FINISHED'}"
            )

        op_ctx = {
            "idname": idname,
            "label": op_spec["label"],
            "description": op_spec.get("description", ""),
            "class_name": class_name,
            "options_code": options_code,
            "body": body,
        }
        operators.append(op_ctx)
        ops_by_idname[idname] = op_ctx

    # ───── Panels ─────
    panels = []

    for p in spec.get("panels", []):
        idname = p["idname"]
        class_name = panel_idname_to_class(idname)

        # Panel operators
        panel_ops = []
        for pop in p.get("operators", []):
            op_idname = pop["idname"]
            label = pop.get("label") or ops_by_idname.get(op_idname, {}).get("label", op_idname)
            panel_ops.append({
                "idname": op_idname,
                "label": label,
            })

        # Panel properties
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

    print(
        f"[panelgen] Prepared context: "
        f"{len(properties)} properties, {len(operators)} operators, {len(panels)} panels"
    )
    return ctx


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    # here = Path(__file__).resolve().parent       # .../src/panelgen1
    # project_root = here.parent.parent            # .../panelgen1
    project_root = Path(os.getcwd())            # .../panelgen1
    spec_path = project_root / "panel_spec.toml"

    spec = load_spec(spec_path)
    ctx = prepare_context(spec)
    mod_name = ctx["addon"]["module_name"]

    tmpl_dir = get_template_path()

    addons_dir = project_root / "scripts" / "addons" / mod_name
    addons_dir.mkdir(parents=True, exist_ok=True)

    output_path = addons_dir / mod_name / "__init__.py"

    print(f"[panelgen] project_root = {project_root}")
    print(f"[panelgen] tmpl_dir     = {tmpl_dir}")
    print(f"[panelgen] spec_path    = {spec_path}")
    print(f"[panelgen] output_path  = {output_path}")

    # spec = load_spec(spec_path)
    # ctx = prepare_context(spec)

    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("addon_single.jinja2")
    code = template.render(**ctx)

    print(f"[panelgen] Rendered code length: {len(code)} chars")

    if not code.strip():
        raise RuntimeError("[panelgen] Template rendered empty code. Check template and context.")

    output_path.write_text(code, encoding="utf-8")
    print(f"[panelgen] Generated add-on: {output_path}")


if __name__ == "__main__":
    main()
