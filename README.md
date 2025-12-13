
# PanelGen — Blender Add-on Generator  
### User Manual

PanelGen is a lightweight CLI tool that generates Blender add-ons from a simple, human-friendly TOML specification.  
With PanelGen, you can create complex Blender UI panels, operators, and properties **without writing boilerplate**, and regenerate the add-on instantly as your UI evolves.

---
# 0. Requirement
You need to have python installed. Since you are running blender and be building a Blender add-on, most likely you already have python. You also need to have `uv` package manager instlled. You may use other package managers or `pip` but I have only tested it with `uv`.


# 1. Installation

If you have older version installed you need to remove it first. To remove it via `uv`:
```bash
uv tool uninstall panelgen1
```

To install it via `uv`:

```bash
uv tool -n install git+https://github.com/kkibria/panelgen1.git
```

PanelGen works like any Python CLI tool. Once installed, run it as following:

```bash
panelgen <command>
```

---

# 2. Commands

PanelGen provides two primary commands:

## 2.1 `init <directory>`

Creates a new project directory with:

```
<directory>/
  panel_spec.toml   # Main configuration
  scripts/
    addons/         # Generated add-on will appear here
```

Example:

```bash
panelgen init my_overlay_addon
```

---

## 2.2 `gen`

Generates the Blender add-on using the current working directory as the project root.

The command:

```bash
panelgen gen [--toml-file <toml_file>]
```

Reads:

```
./panel_spec.toml
```

Writes:

```
./scripts/addons/my_panel_addon.py
```

This file can be installed in Blender via:

**Edit → Preferences → Add-ons → Install…**

---

# 3. Project Structure

A typical PanelGen project looks like:

```
my_project/
  panel_spec.toml
  scripts/
    addons/
      my_panel_addon/ ← same as module_name in toml
        __init__.py  ← Generated file (overwrite every run)
      another_my_panel_addon/ ← same as module_name in toml
        __init__.py  ← Generated file (overwrite every run)
```

You should **not edit** `my_panel_addon.py` manually.
Instead, modify `panel_spec.toml` and regenerate.

---

# 4. Overview of spec toml file
The default toml file is `panel_spec.toml`. You can have more toml files for additional
add-ons.

The TOML file describes:

* Add-on metadata
* Properties (Blender data fields)
* Operators (buttons)
* Panels (UI sections in the VSE sidebar)

Here is the structure at a glance:

```toml
[addon]
... metadata ...

[[properties]]
... defines a Blender property ...

[[panels]]
... describes a UI panel ...

  [[panels.operators]]
  ... operators shown in this panel ...

[[operators]]
... defines the behavior of each operator ...
```

Let’s go through each section in detail.

---

# 5. `[addon]` Section

Describes core metadata for Blender.

```toml
[addon]
module_name = "my_panel_addon"
bl_name = "My Panel Add-on"
author = "You"
version = [0, 0, 1]
blender_min = [5, 0, 0]
category = "Sequencer"
location = "VSE > Sidebar > My Panels"
tab_name = "MyPanel"
```

### Fields:

| Field         | Description                                         |
| ------------- | --------------------------------------------------- |
| `module_name` | Name of the generated Python add-on file.           |
| `bl_name`     | Human-readable name shown in Blender’s add-on list. |
| `author`      | Your name or org.                                   |
| `version`     | The add-on version tuple.                           |
| `blender_min` | Minimum supported Blender version.                  |
| `location`    | Description shown in Blender add-on preferences.    |
| `category`    | Add-on category in Blender.                         |
| `tab_name`    | Name of the sidebar tab in the Sequencer.           |

---

# 6. `[[properties]]` Section

Properties become Blender editable fields stored on `bpy.types.Scene`,
visible in panels using `layout.prop()`.

Example:

```toml
[[properties]]
id = "scene.main_label"
owner = "Scene"
attr = "my_main_label"
type = "StringProperty"
name = "Main Label"
description = "Main label text for overlays"
default = "Hello from TOML"
```

### Required Fields

| Field   | Example            | Meaning                                      |
| ------- | ------------------ | -------------------------------------------- |
| `id`    | `scene.main_label` | Unique reference used inside panels.         |
| `owner` | `Scene`            | Blender data-block (currently Scene only).   |
| `attr`  | `my_main_label`    | Attribute name created on `bpy.types.Scene`. |
| `type`  | `StringProperty`   | Blender property type.                       |

### Optional Fields

| Field                  | Applies To  | Description           |
| ---------------------- | ----------- | --------------------- |
| `name`                 | all         | UI display label.     |
| `description`          | all         | Tooltip text.         |
| `default`              | all         | Default value.        |
| `min`, `max`           | Int / Float | Numeric constraints.  |
| `soft_min`, `soft_max` | Int / Float | Soft UI boundaries.   |
| `step`                 | Int / Float | Slider step amount.   |
| `items`                | Enum        | List of enum entries. |

### Enum Example

```toml
[[properties]]
id = "scene.mode"
owner = "Scene"
attr = "my_mode"
type = "EnumProperty"
name = "Mode"
default = "OPT_A"

  [[properties.items]]
  identifier = "OPT_A"
  name = "Option A"
  description = "First option"

  [[properties.items]]
  identifier = "OPT_B"
  name = "Option B"
  description = "Second option"
```

---

# 7. `[[panels]]` Section

Defines a UI panel appearing in Blender’s Video Sequencer sidebar (`N` panel).

```toml
[[panels]]
idname = "MYADDON_PT_main"
label = "Main Panel"
space_type = "SEQUENCE_EDITOR"
region_type = "UI"
category = "MyPanel"
properties = ["scene.main_label", "scene.show_debug"]

  [[panels.operators]]
  idname = "myaddon.dummy_operator"
  label = "Run Dummy"
```

### Required Fields

| Field    | Description                      |
| -------- | -------------------------------- |
| `idname` | Pipeline ID for the panel class. |
| `label`  | Human-readable name in UI.       |

### Optional

| Field         | Default               | Meaning                           |
| ------------- | --------------------- | --------------------------------- |
| `space_type`  | `SEQUENCE_EDITOR`     | UI space type.                    |
| `region_type` | `UI`                  | Panel region.                     |
| `category`    | From `addon.tab_name` | Sidebar tab name.                 |
| `properties`  | none                  | Properties to show in this panel. |

### Nesting Operators in Panels

Operators displayed inside this panel:

```toml
[[panels.operators]]
idname = "myaddon.dummy_operator"
label = "Run Dummy"
```

---

# 8. `[[operators]]` Section

Defines custom operator classes (buttons).

```toml
[[operators]]
idname = "myaddon.dummy_operator"
label = "Dummy Operator"
description = "Prints debug info"
options = ["REGISTER"]
body = """
        scene = context.scene
        self.report({'INFO'}, f"Main label = {scene.my_main_label}")
        return {'FINISHED'}
"""
```

### Required:

| Field    | Meaning                                           |
| -------- | ------------------------------------------------- |
| `idname` | Blender operator name (`addon.namespace.action`). |
| `label`  | UI button label.                                  |

### Optional:

| Field         | Meaning                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------- |
| `description` | Tooltip.                                                                                    |
| `options`     | Operator flags like `"REGISTER"`.                                                           |
| `body`        | Python code inside `execute(self, context)` — **indentation is the user's responsibility**. |

### Operator Body

The `body` text is inserted **verbatim** into the generated class:

```python
def execute(self, context):
    <body goes here exactly>
```

This keeps behavior predictable and fully under your control.

---

# 9. Workflow Example

### 1. Create a new project

```bash
panelgen init text_overlay
cd text_overlay
```

### 2. Edit `panel_spec.toml`

Add your properties, panels, and operators.

### 3. Generate add-on

```bash
panelgen gen
```

This writes:

```
scripts/addons/my_panel_addon.py
```

### 4. Load in Blender

* Edit → Preferences → Add-ons → Install…
* Select the generated file
* Enable it
* Open the Sequencer (`N` panel) to view your UI

---

# 10. General Notes & Best Practices

### ✔ PanelGen-generated code is **not meant to be edited manually**

Edit TOML instead.

### ✔ Operator bodies should be indented correctly inside the TOML

PanelGen includes the code literally.

### ✔ The generator overwrites output every time

Keep your custom logic in TOML, not in the generated file.

### ✔ Keep panel IDs unique

Blender requires unique class names & IDs.

### ✔ The tool currently centers around Scene properties

Support for more data-blocks may be added later.

---

# 11. Troubleshooting

### **“Module not found” when loading add-on in Blender**

* Ensure you installed the correct `my_panel_addon.py`.
* Ensure it is inside `scripts/addons/` and regenerated.

### **Operator indentation errors**

The operator body must have correct indentation in TOML.

### **Enum not showing dropdown**

Check:

* `default` matches an enum identifier
* Each enum entry has unique `identifier`

### **Property not shown in a panel**

Make sure its `id` is listed under the panel’s:

```toml
properties = ["scene.prop_id", ...]
```

---

# 12. Future Extensions

PanelGen is designed to grow. Possible future versions may include:

* Multi-file add-on scaffolding
* Template operators (e.g., “add image strip”)
* External dependencies bundling
* Advanced UI widgets (menus, lists, popovers)
* Built-in TOML validation

---

# 13. Summary

PanelGen streamlines Blender add-on creation by letting you focus on **what your UI should do**, not on repetitive Python boilerplate.

Write your UI once in a clear TOML file, regenerate instantly, and keep your workflow clean, reproducible, and fast.

Happy hacking 🎨🐍


# 14. Reference: Acceptable Values for Each TOML Entry

This section defines **all valid values** for each part of the PanelGen schema.

---

# 14.1 Property Types (`type = ""`)

PanelGen supports any Blender property type that can be attached to `bpy.types.Scene`.

### **Valid values for `type`**

| Property Type | Blender Equivalent | Notes |
|--------------|-------------------|-------|
| `"StringProperty"` | `bpy.props.StringProperty` | Text fields. |
| `"BoolProperty"` | `bpy.props.BoolProperty` | Checkbox. |
| `"IntProperty"` | `bpy.props.IntProperty` | Integer spinner. Supports min/max. |
| `"FloatProperty"` | `bpy.props.FloatProperty` | Decimal number. Supports min/max. |
| `"EnumProperty"` | `bpy.props.EnumProperty` | Dropdown menu. Requires `[[properties.items]]`. |

### Additional types you **may** add later (PanelGen will support them easily):

| Potential Type | Usage |
|----------------|-------|
| `"FloatVectorProperty"` | Colors, vectors, XYZ triples |
| `"IntVectorProperty"` | Integer triples |
| `"PointerProperty"` | Linking to objects or collections |

---

# 14.2 Property Specification: Full Field Reference

```toml
[[properties]]
id = "scene.example"            # REQUIRED
owner = "Scene"                 # REQUIRED
attr = "my_property"            # REQUIRED
type = "StringProperty"         # REQUIRED
name = "Example"                # OPTIONAL (UI label)
description = "Tooltip"         # OPTIONAL
default = "Hello"               # OPTIONAL
min = 0                         # For Int/Float
max = 100                       # For Int/Float
soft_min = 1                    # For Int/Float
soft_max = 99                   # For Int/Float
step = 1                        # For Int/Float
````

### **Rules**

* `id` must be unique across all properties.
* `id` must follow `scene.something` (for now).
* Default values must match the property type:

  * String → `"text"`
  * Bool → `true` / `false`
  * Int → `10`
  * Float → `3.14`
  * Enum → identifier string like `"OPT_A"`

---

# 14.3 Enum Property Items

Example:

```toml
[[properties]]
id = "scene.mode"
attr = "my_mode"
owner = "Scene"
type = "EnumProperty"
name = "Mode"
default = "OPT_A"

  [[properties.items]]
  identifier = "OPT_A"
  name = "Option A"
  description = "AAA mode"

  [[properties.items]]
  identifier = "OPT_B"
  name = "Option B"
  description = "BBB mode"
```

### **Valid fields in `[[properties.items]]`**

| Field         | Required | Meaning           |
| ------------- | -------- | ----------------- |
| `identifier`  | ✔        | Internal enum key |
| `name`        | ✔        | Friendly UI label |
| `description` | ✔        | Tooltip           |

### **Rules**

* Identifiers must be unique inside the enum.
* Default must match one of them.

---

# 15. Examples for EACH Property Type

## 15.1 String Property

```toml
[[properties]]
id = "scene.title"
owner = "Scene"
attr = "my_title"
type = "StringProperty"
name = "Title"
default = "Untitled"
```

---

## 15.2 Bool Property (Checkbox)

```toml
[[properties]]
id = "scene.enable_feature"
owner = "Scene"
attr = "my_enable_feature"
type = "BoolProperty"
name = "Enable Feature"
default = false
```

---

## 15.3 Int Property (With Constraints)

```toml
[[properties]]
id = "scene.repeat"
owner = "Scene"
attr = "my_repeat"
type = "IntProperty"
name = "Repeat Count"
default = 3
min = 0
max = 10
step = 1
```

---

## 15.4 Float Property

```toml
[[properties]]
id = "scene.scale"
owner = "Scene"
attr = "my_scale"
type = "FloatProperty"
name = "Scale"
default = 1.0
min = 0.1
max = 10.0
```

---

## 15.5 Enum Property (Dropdown)

```toml
[[properties]]
id = "scene.render_mode"
owner = "Scene"
attr = "my_render_mode"
type = "EnumProperty"
name = "Render Mode"
default = "FAST"

  [[properties.items]]
  identifier = "FAST"
  name = "Fast"
  description = "Fast render mode"

  [[properties.items]]
  identifier = "QUALITY"
  name = "High Quality"
  description = "Slower, better quality"
```

---

# 16. Operator Specification

Operators define Blender actions (buttons).
Each operator must be listed under `[[operators]]`.

Example:

```toml
[[operators]]
idname = "myaddon.print_info"
label = "Print Info"
description = "Prints debug info"
options = ["REGISTER"]
body = """
        scene = context.scene
        print("Title:", scene.my_title)
        return {'FINISHED'}
"""
```

---

## 16.1 Valid Fields for Operators

| Field         | Required | Description                                                  |
| ------------- | -------- | ------------------------------------------------------------ |
| `idname`      | ✔        | Must be lowercase prefix + action, e.g. `"myaddon.do_thing"` |
| `label`       | ✔        | UI button name                                               |
| `description` | ✖        | Tooltip                                                      |
| `options`     | ✖        | Blender operator flags (list of strings)                     |
| `body`        | ✔        | Literal Python code inserted under `execute()`               |

---

## 16.2 Allowed Operator Option Flags

| Flag         | What it Means                            |
| ------------ | ---------------------------------------- |
| `"REGISTER"` | Operator appears in Blender’s redo panel |
| `"UNDO"`     | Makes action undoable                    |
| `"FINISHED"` | Standard return value                    |

Example:

```toml
options = ["REGISTER", "UNDO"]
```

---

## 16.3 Operator Body Rules

* The *entire block* is pasted directly under `def execute(self, context):`
* **Indentation is the user's responsibility**
* Must end with:

```python
return {'FINISHED'}
```

---

# 16.4 Operator Examples

### Basic Operator

```toml
[[operators]]
idname = "myaddon.hello"
label = "Say Hello"
body = """
        print("Hello from Blender!")
        return {'FINISHED'}
"""
```

### Operator modifying scene

```toml
[[operators]]
idname = "myaddon.increment"
label = "Increment"
body = """
        scene = context.scene
        scene.my_repeat += 1
        return {'FINISHED'}
"""
```

### Operator inserting image strip into VSE

```toml
[[operators]]
idname = "myaddon.add_strip"
label = "Add Image Strip"
body = """
        bpy.ops.sequencer.image_strip_add(
            filepath="/tmp/example.png",
            frame_start=context.scene.frame_current
        )
        return {'FINISHED'}
"""
```

### Operator calling external Python module

```toml
[[operators]]
idname = "myaddon.call_external"
label = "Run External"
body = """
        from .external.my_lib import hello
        hello()
        return {'FINISHED'}
"""
```

---

# 17. Panel Specification — Acceptable Values

Panels define what users see in the Blender UI.

Basic example:

```toml
[[panels]]
idname = "MYADDON_PT_controls"
label = "Controls"
space_type = "SEQUENCE_EDITOR"
region_type = "UI"
category = "MyPanel"
properties = ["scene.my_title", "scene.my_repeat"]

  [[panels.operators]]
  idname = "myaddon.hello"
  label = "Say Hello"
```

### 17.1 Valid Values

| Field         | Acceptable Values         | Notes                            |
| ------------- | ------------------------- | -------------------------------- |
| `idname`      | Must end with `_PT_*`     | Blender naming rule              |
| `space_type`  | `"SEQUENCE_EDITOR"`       | Default                          |
| `region_type` | `"UI"`                    | Default                          |
| `category`    | Any tab name              | Usually matches add-on           |
| `properties`  | List of property IDs      | Must refer to existing props     |
| `operators`   | List of operator mappings | Must refer to existing operators |

---

# 18. Example: Complete Minimal Working TOML

```toml
[addon]
module_name = "simple_addon"
bl_name = "Simple Addon"
author = "User"
version = [1, 0, 0]
blender_min = [5, 0, 0]
tab_name = "SimpleTab"

[[properties]]
id = "scene.greeting"
owner = "Scene"
attr = "my_greeting"
type = "StringProperty"
default = "Hello!"

[[operators]]
idname = "simple.say_hi"
label = "Say Hi"
body = """
        print(context.scene.my_greeting)
        return {'FINISHED'}
"""

[[panels]]
idname = "SIMPLE_PT_main"
label = "Main Panel"
properties = ["scene.greeting"]

  [[panels.operators]]
  idname = "simple.say_hi"
  label = "Say Hello"
```

