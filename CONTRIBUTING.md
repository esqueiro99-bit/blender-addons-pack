# Contributing to Blender Add-ons Pack

## Reporting Bugs

Open a GitHub Issue with:
- Which add-on has the bug (Dynamic Parent or Rig Constraints Manager)
- Your Blender version
- Steps to reproduce
- Expected vs actual behavior

## Adding a New Add-on

Want to include your add-on in this pack?

1. The add-on must be compatible with **Blender 3.6+** or **5.0+**
2. It must include a proper `bl_info` dict
3. It must be licensed under **GPL-2.0+** or **GPL-3.0**
4. No external pip dependencies (Blender's built-in Python only)
5. Open a Pull Request with the `.py` file and a short description in the PR body

## Code Style

- Follow **PEP 8**
- Use Blender's idiomatic patterns (`bpy.props`, `bpy.types.Operator`, `bpy.types.Panel`)
- Add docstrings to all operators and panel classes
- Test on **Blender 3.6 LTS**, **4.2 LTS**, and **5.0**

## License

By contributing you agree to license your code under **GPL-3.0** (or GPL-2.0+ for extensions of existing GPL-2.0 code).
