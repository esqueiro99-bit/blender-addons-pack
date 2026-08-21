# Blender Add-ons Pack

[![License: GPL v2+](https://img.shields.io/badge/License-GPLv2+-blue.svg)](https://www.gnu.org/licenses/gpl-2.0)
[![Blender](https://img.shields.io/badge/Blender-3.0%2B%20%7C%205.0-orange?logo=blender)](https://www.blender.org)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen)]()

A curated collection of Blender add-ons focused on **rigging**, **constraints management**, and **animation workflows** for Roblox and general game development pipelines.

---

## 📦 Add-ons Included

### 1. Dynamic Parent
> **Author:** Roman Volodin & wzrd | **Version:** 2.1.0 | **Blender:** 5.0+

Allows creating, enabling, and disabling animated **Child Of** constraints with a single click. Ideal for prop handoffs, camera parenting, and complex constraint-driven animation workflows.

**Location:** `View3D > Sidebar (N-Panel) > Animation / Item / Tool`

**Features:**
- Create animated Child Of constraints instantly
- Toggle constraints on/off with automatic keyframing
- Clean workflow for object parenting during animations
- PEP8 compliant, Blender 5.0 API ready

---

### 2. Rig Constraints Manager
> **Author:** Real Antigravity | **Version:** 1.1.0 | **Blender:** 3.0+

Manages **Copy Transforms** constraints between two rigs, creates foot bones for Roblox **R6** characters, and batch-cleans constraints.

**Location:** `View3D > Sidebar > Rig Constraints`

**Features:**
- Manage Copy Transforms between source and target rigs
- Auto-create foot bones for R6 rig pipelines
- Batch-clear all constraints from a rig
- Armature-aware object filtering
- Uses `bpy` and `mathutils` — no external dependencies

---

## 🚀 Installation

Each add-on can be installed individually:

1. Download the `.py` file for the add-on you want from the [`addons/`](addons/) folder
2. In Blender: **Edit → Preferences → Add-ons → Install from Disk...**
3. Select the `.py` file
4. Enable the add-on by checking its checkbox

> **Tip:** On Blender 4.2+ use **Get Extensions → Install from Disk** instead.

---

## 🏗️ Project Structure

```
blender-addons-pack/
├── addons/
│   ├── dynamic_parent/
│   │   ├── __init__.py
│   │   └── dynamic_parent.py
│   └── rig_constraints_manager/
│       ├── __init__.py
│       └── rig_constraints_manager.py
├── docs/
│   ├── dynamic_parent.md
│   └── rig_constraints_manager.md
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Bug reports and pull requests are welcome!

## 📄 License

- `dynamic_parent.py` — **GNU GPL v2 or later** (original license by Roman Volodin)
- `rig_constraints_manager.py` — **GNU GPL v3.0**

See [LICENSE](LICENSE) for full text.
