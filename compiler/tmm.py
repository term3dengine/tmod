#!/usr/bin/env python3
"""
Term3D Mod Compiler
Compiles .py mod files to .tmm binary format.
"""
import struct
import sys
import os
import marshal


def compile_mod(py_file, tmm_file):
    """Compile a .py mod file to .tmm binary format."""
    with open(py_file, 'r') as f:
        code = f.read()

    bytecode = compile(code, py_file, 'exec')
    mod_bytes = marshal.dumps(bytecode)
    key = b'TMM1'
    obfuscated = bytes([b ^ key[i % len(key)] for i, b in enumerate(mod_bytes)])

    with open(tmm_file, 'wb') as f:
        f.write(b'TMM1')
        mod_name = os.path.basename(py_file).replace('.py', '')
        name_bytes = mod_name.encode('utf-8')
        f.write(struct.pack('<I', len(name_bytes)))
        f.write(name_bytes)
        f.write(struct.pack('<I', len(obfuscated)))
        f.write(obfuscated)


def main():
    if len(sys.argv) < 3:
        print("Usage: tmm_compile.py input.py output.tmm")
        sys.exit(1)
    compile_mod(sys.argv[1], sys.argv[2])
    print(f"Compiled {sys.argv[1]} to {sys.argv[2]}")


if __name__ == '__main__':
    main()
