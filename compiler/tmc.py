#!/usr/bin/env python3
"""
Term3D Map Compiler
Compiles .tm JSON maps to .tmc binary format.
"""
import json
import struct
import sys
import os
import marshal


def compile_map(tm_file, tmc_file):
    """Compile a .tm JSON map to .tmc binary format."""
    with open(tm_file, 'r') as f:
        data = json.load(f)

    with open(tmc_file, 'wb') as f:
        f.write(b'TMC1')

        name = data.get('name', 'Unnamed')
        name_bytes = name.encode('utf-8')
        f.write(struct.pack('<I', len(name_bytes)))
        f.write(name_bytes)

        ps = data.get('player_start', {'x': 0, 'y': 1.7, 'z': 8})
        f.write(struct.pack('<fff', ps['x'], ps['y'], ps['z']))

        ground = data.get('ground', {'width': 60, 'depth': 60})
        f.write(struct.pack('<ff', ground['width'], ground['depth']))

        objects = data.get('objects', [])
        f.write(struct.pack('<I', len(objects)))
        for obj in objects:
            obj_type = obj.get('type', 'cube')
            type_bytes = obj_type.encode('utf-8')
            f.write(struct.pack('<I', len(type_bytes)))
            f.write(type_bytes)
            f.write(struct.pack('<fff', obj.get('x', 0), obj.get('y', 0.5), obj.get('z', 0)))
            f.write(struct.pack('<f', obj.get('size', 1.0)))
            color = obj.get('color', [120, 100, 80])
            f.write(struct.pack('<BBB', color[0], color[1], color[2]))
            f.write(struct.pack('<B', 1 if obj.get('solid', True) else 0))
            f.write(struct.pack('<B', 1 if obj.get('physics', False) else 0))

        mods = data.get('mods', [])
        f.write(struct.pack('<I', len(mods)))
        for mod in mods:
            mod_name = mod.get('name', 'unnamed')
            mod_name_bytes = mod_name.encode('utf-8')
            f.write(struct.pack('<I', len(mod_name_bytes)))
            f.write(mod_name_bytes)

            mod_file = mod.get('file', '')
            if mod_file and os.path.exists(mod_file):
                with open(mod_file, 'rb') as mf:
                    tmm_data = mf.read()
                if tmm_data.startswith(b'TMM1'):
                    try:
                        name_len = struct.unpack('<I', tmm_data[4:8])[0]
                        offset = 8 + name_len
                        mod_len = struct.unpack('<I', tmm_data[offset:offset+4])[0]
                        offset += 4
                        obfuscated = tmm_data[offset:offset+mod_len]
                        f.write(struct.pack('<I', len(obfuscated)))
                        f.write(obfuscated)
                    except Exception:
                        f.write(struct.pack('<I', 0))
                else:
                    f.write(struct.pack('<I', 0))
            else:
                f.write(struct.pack('<I', 0))


def main():
    if len(sys.argv) < 3:
        print("Usage: tmc_compile.py input.tm output.tmc")
        sys.exit(1)
    compile_map(sys.argv[1], sys.argv[2])
    print(f"Compiled {sys.argv[1]} to {sys.argv[2]}")


if __name__ == '__main__':
    main()
