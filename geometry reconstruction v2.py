# -*- coding: utf-8 -*-
"""
Geometry reconstruction for orthodontic FEM simulation
Reconstructs STL files from nodal positions exported from Ansys Mechanical.

Inputs:
  - 4 CSV files with columns: Node Number | New X position | New Y position | New Z position
  - 1 Ansys APDL mesh file (.cdb) with NBLOCK and EBLOCK

Outputs:
  - tooth_final.stl, tooth_initial.stl
  - pdl_final.stl,   pdl_initial.stl
"""

import os, re, struct
from collections import defaultdict
import pandas as pd
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# =============================================================================
# MATERIAL ASSIGNMENT
# Edit these if your material numbering changes between iterations.
# =============================================================================
MAT_TOOTH = 1
MAT_PDL   = 2

# =============================================================================
# READ POSITION CSV FILES
# =============================================================================

def read_pos_csv(filename):
    """Read a position CSV and return {node_id: (x, y, z)}."""
    df = pd.read_csv(
        filename, sep=None, engine='python', decimal=",",
        dtype={"Node Number":   int,
               "New X position": float,
               "New Y position": float,
               "New Z position": float}
    )
    return {int(r["Node Number"]): (r["New X position"],
                                     r["New Y position"],
                                     r["New Z position"])
            for _, r in df.iterrows()}

pos_tooth_final = read_pos_csv("disp_info_tab_tooth_final.txt")
pos_tooth_init  = read_pos_csv("disp_info_tab_tooth_initial.txt")
pos_pdl_final   = read_pos_csv("disp_info_tab_pdl_final.txt")
pos_pdl_init    = read_pos_csv("disp_info_tab_pdl_initial.txt")

print(f"CSV loaded — tooth: {len(pos_tooth_final)} nodes, PDL: {len(pos_pdl_final)} nodes")

# =============================================================================
# READ CDB FILE
# =============================================================================

with open("final_mesh.cdb", 'r', encoding='latin-1') as f:
    lines = f.readlines()

print(f"CDB lines: {len(lines)}")

# Regex to extract scientific-notation coordinates that may be written
# without spaces between them, e.g. "-1.6006E+001-3.4054E+001"
RE_COORD = re.compile(r'[+-]?\d+\.\d+[Ee][+-]\d+')

# =============================================================================
# PARSE NBLOCK AND EBLOCK
# A single sequential pass manages the index exclusively here.
#
# NBLOCK format (fixed columns):
#   cols  0-8  : node ID
#   cols 27+   : X Y Z in scientific notation (may be adjacent, no spaces)
#
# EBLOCK format (19i10 — each field is 10 characters wide):
#   cols   0- 9 : MAT
#   cols 110-119: node 1 (corner)
#   cols 120-129: node 2
#   cols 130-139: node 3
#   cols 140-149: node 4
#   line 2      : mid-side nodes (ignored)
# =============================================================================

nodes    = {}   # {node_id: (x, y, z)}
elements = []   # [{'mat': int, 'nodes': [n1, n2, n3, n4]}]

i = 0
while i < len(lines):
    line    = lines[i]
    stripped = line.strip().upper()

    # ------------------------------------------------------------------
    # NBLOCK
    # ------------------------------------------------------------------
    if stripped.startswith('NBLOCK') and 'SFEBLOCK' not in stripped:
        i += 2   # skip the format line e.g. "(3i9,6e21.13e3)"
        while i < len(lines):
            raw = lines[i].strip()

            # End of block: "-1" sentinel or next APDL keyword
            if re.match(r'^-1\b', raw):
                i += 1
                break
            if re.match(r'^[A-Z]', raw.upper()):
                # Do not consume this line — let the outer loop handle it
                break

            try:
                node_id = int(lines[i][0:9])
                coords  = RE_COORD.findall(lines[i][27:])
                if len(coords) >= 3:
                    nodes[node_id] = (float(coords[0]),
                                      float(coords[1]),
                                      float(coords[2]))
            except (ValueError, IndexError):
                pass
            i += 1
        print(f"NBLOCK parsed: {len(nodes)} nodes")
        continue   # index already positioned correctly

    # ------------------------------------------------------------------
    # EBLOCK
    # ------------------------------------------------------------------
    if stripped.startswith('EBLOCK,') and 'SFEBLOCK' not in stripped:
        i += 2   # skip the format line "(19i10)"
        while i < len(lines):
            raw = lines[i].rstrip('\n\r')

            # End of block
            if lines[i].strip().startswith('-1'):
                i += 1
                break

            # Element lines are exactly 191 chars (19 fields × 10 chars + \n).
            # We require at least 150 chars to safely read the 4 corner nodes.
            if len(raw) >= 150:
                try:
                    mat = int(raw[0:10])
                    n1  = int(raw[110:120])
                    n2  = int(raw[120:130])
                    n3  = int(raw[130:140])
                    n4  = int(raw[140:150])
                    elements.append({'mat': mat, 'nodes': [n1, n2, n3, n4]})
                    i += 2   # skip the mid-side node line (n9, n10)
                    continue
                except ValueError:
                    pass
            i += 1
        print(f"EBLOCK parsed: {len(elements)} elements")
        continue   # index already positioned correctly

    i += 1

# =============================================================================
# MATERIAL SUMMARY
# =============================================================================

mats       = sorted(set(e['mat'] for e in elements))
mat_counts = {m: sum(1 for e in elements if e['mat'] == m) for m in mats}
print(f"\nMaterials found: {mats}")
for m, c in mat_counts.items():
    print(f"  MAT {m}: {c} elements")
print(f"\nMAT_TOOTH = {MAT_TOOTH} ({mat_counts.get(MAT_TOOTH, 0)} elements)")
print(f"MAT_PDL   = {MAT_PDL} ({mat_counts.get(MAT_PDL, 0)} elements)")

# =============================================================================
# SPLIT ELEMENTS BY MATERIAL
# =============================================================================

elems_tooth = [e for e in elements if e['mat'] == MAT_TOOTH]
elems_pdl   = [e for e in elements if e['mat'] == MAT_PDL]
print(f"\nTooth: {len(elems_tooth)} elements | PDL: {len(elems_pdl)} elements")

# =============================================================================
# SURFACE FACE EXTRACTION
# A triangular face is on the free surface if and only if it belongs to
# exactly one tetrahedral element (boundary face criterion).
# =============================================================================

def get_surface_faces(elements_subset):
    """
    Extract free-surface triangles from a list of tetrahedral elements.
    Each tet has 4 triangular faces defined by the 4 combinations of
    its corner nodes. A face shared by two tets is internal; a face
    belonging to only one tet is on the surface.

    Returns a list of [n1, n2, n3] node lists (original winding order).
    """
    face_count  = defaultdict(int)
    face_orient = {}
    combos = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    for elem in elements_subset:
        ns = elem['nodes']
        for a, b, c in combos:
            # Canonical key (sorted) for shared-face detection
            key = tuple(sorted([ns[a], ns[b], ns[c]]))
            face_count[key]  += 1
            face_orient[key]  = [ns[a], ns[b], ns[c]]
    surface = [face_orient[k] for k, cnt in face_count.items() if cnt == 1]
    print(f"  Surface faces: {len(surface)}")
    return surface

faces_tooth = get_surface_faces(elems_tooth)
faces_pdl   = get_surface_faces(elems_pdl)

# =============================================================================
# BINARY STL EXPORT
# =============================================================================

def export_stl(faces, pos_dict, filename):
    """
    Export a binary STL file.

    Parameters
    ----------
    faces    : list of [n1, n2, n3]  — surface triangles (node IDs)
    pos_dict : {node_id: (x, y, z)} — nodal positions to use
    filename : output path

    Notes
    -----
    - Faces with any node absent from pos_dict are skipped.
    - Normals are oriented outward using a global centroid test.
    - Coordinates are stored as float32 (standard STL precision).
    """
    valid   = [f for f in faces if all(n in pos_dict for n in f)]
    missing = len(faces) - len(valid)
    if missing:
        print(f"  WARNING: {missing} faces skipped (nodes absent from CSV)")
    if not valid:
        print(f"  ERROR: no valid faces for {filename}")
        return

    # Global centroid used to consistently orient all normals outward
    centroid = np.mean([pos_dict[f[0]] for f in valid], axis=0)

    with open(filename, 'wb') as fh:
        fh.write(b'\0' * 80)                        # 80-byte header
        fh.write(struct.pack('<I', len(valid)))      # triangle count (uint32)
        for face in valid:
            pts = np.array([pos_dict[n] for n in face], dtype=np.float64)
            v1, v2 = pts[1] - pts[0], pts[2] - pts[0]
            normal   = np.cross(v1, v2)
            norm_len = np.linalg.norm(normal)
            if norm_len > 0:
                normal /= norm_len
            # Flip normal and vertex winding if pointing inward
            if np.dot(normal, pts.mean(axis=0) - centroid) < 0:
                normal = -normal
                pts    = pts[[0, 2, 1]]
            fh.write(struct.pack('<3f', *normal.astype(np.float32)))
            for pt in pts:
                fh.write(struct.pack('<3f', *pt.astype(np.float32)))
            fh.write(struct.pack('<H', 0))           # attribute byte count

    print(f"  Exported -> {filename}  ({len(valid)} triangles)")

# =============================================================================
# EXPORT ALL 4 STL FILES
# =============================================================================

print("\nExporting STL files:")
export_stl(faces_tooth, pos_tooth_final, "tooth_final.stl")
export_stl(faces_pdl,   pos_pdl_final,   "pdl_final.stl")
export_stl(faces_tooth, pos_tooth_init,  "tooth_initial.stl")
export_stl(faces_pdl,   pos_pdl_init,    "pdl_initial.stl")

print("\nDone — 4 STL files exported.")