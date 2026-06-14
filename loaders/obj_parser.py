import time
import numpy as np
import math
from numba import njit
import numpy as np

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )

def length(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def normalize(v):
    l = length(v)
    if l == 0:
        return (0.0, 0.0, 0.0)
    inv = 1.0 / l
    return (v[0]*inv, v[1]*inv, v[2]*inv)

def sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def mul(v, s):
    return (v[0]*s, v[1]*s, v[2]*s)

@njit
def compute_tangents(vertices, uvs, indices, uv_indices):
    n_verts = vertices.shape[0]

    tangents = np.zeros((n_verts, 3), dtype=np.float32)
    bitangents = np.zeros((n_verts, 3), dtype=np.float32)

    for t in range(indices.shape[0]):

        i0 = indices[t, 0]
        i1 = indices[t, 1]
        i2 = indices[t, 2]

        uv0_i = uv_indices[t, 0]
        uv1_i = uv_indices[t, 1]
        uv2_i = uv_indices[t, 2]

        if uv0_i < 0 or uv1_i < 0 or uv2_i < 0:
            continue

        v0x, v0y, v0z = vertices[i0]
        v1x, v1y, v1z = vertices[i1]
        v2x, v2y, v2z = vertices[i2]

        uv0x, uv0y = uvs[uv0_i]
        uv1x, uv1y = uvs[uv1_i]
        uv2x, uv2y = uvs[uv2_i]

        e1x = v1x - v0x
        e1y = v1y - v0y
        e1z = v1z - v0z

        e2x = v2x - v0x
        e2y = v2y - v0y
        e2z = v2z - v0z

        du1 = uv1x - uv0x
        dv1 = uv1y - uv0y
        du2 = uv2x - uv0x
        dv2 = uv2y - uv0y

        denom = du1 * dv2 - du2 * dv1
        if abs(denom) < 1e-8:
            continue

        f = 1.0 / denom

        tx = f * (dv2 * e1x - dv1 * e2x)
        ty = f * (dv2 * e1y - dv1 * e2y)
        tz = f * (dv2 * e1z - dv1 * e2z)

        bx = f * (-du2 * e1x + du1 * e2x)
        by = f * (-du2 * e1y + du1 * e2y)
        bz = f * (-du2 * e1z + du1 * e2z)

        tangents[i0, 0] += tx
        tangents[i0, 1] += ty
        tangents[i0, 2] += tz

        tangents[i1, 0] += tx
        tangents[i1, 1] += ty
        tangents[i1, 2] += tz

        tangents[i2, 0] += tx
        tangents[i2, 1] += ty
        tangents[i2, 2] += tz

        bitangents[i0, 0] += bx
        bitangents[i0, 1] += by
        bitangents[i0, 2] += bz

        bitangents[i1, 0] += bx
        bitangents[i1, 1] += by
        bitangents[i1, 2] += bz

        bitangents[i2, 0] += bx
        bitangents[i2, 1] += by
        bitangents[i2, 2] += bz

    return tangents, bitangents

def parse_obj(location):
    start = time.perf_counter()
    vertices = []
    normals = []
    tangents = []
    bitangents = []
    uv_coords = []
    indices = []
    normal_indices = []
    uv_indices = []

    tot = 0
    tris = 0
    quads_split = 0
    ngons_triangulated = 0

    with open(location, "r") as model:
        for line in model:
            # Vertices
            if line.startswith("v "):
                x, y, z = map(float, line.strip().split()[1:])
                vertices.append((x, y, z))
                tangents.append((0,0,0))
                bitangents.append((0,0,0))

            # Normals
            if line.startswith("vn "):
                x, y, z = map(float, line.strip().split()[1:])
                normals.append((x, y, z))

            # UV Coords
            if line.startswith("vt "):
                x, y = map(float, line.strip().split()[1:])
                uv_coords.append((x, y))

            # Indices
            if line.startswith("f "):
                parts = line.strip()[2:].split()

                face_vertices = []
                face_normals = []
                face_uv_coords = []

                for item in parts:
                    split = item.split('/')

                    v = int(split[0])
                    if v < 0:
                        v = len(vertices) + v
                    else:
                        v -= 1
                    face_vertices.append(v)

                    if len(split) > 1 and split[1] != '':
                        uv = int(split[1])
                        if uv < 0:
                            uv = len(uv_coords) + uv
                        else:
                            uv -= 1
                    else:
                        uv = -1
                    face_uv_coords.append(uv)

                    if len(split) > 2 and split[2] != '':
                        n = int(split[2])
                        if n < 0:
                            n = len(normals) + n
                        else:
                            n -= 1
                    else:
                        n = -1
                    face_normals.append(n)

                    face_size = len(face_vertices)

                    if face_size == 3:
                        tris += 1
                    elif face_size == 4:
                        quads_split += 1 
                    elif face_size > 4:
                        ngons_triangulated += 1

                # Triangluate with fan method
                for i in range(1, len(face_vertices) - 1):
                    indices.extend([
                        face_vertices[0],
                        face_vertices[i],
                        face_vertices[i+1]
                    ])

                    normal_indices.extend([
                        face_normals[0],
                        face_normals[i],
                        face_normals[i+1]
                    ])

                    uv_indices.extend([
                        face_uv_coords[0],
                        face_uv_coords[i],
                        face_uv_coords[i+1]
                    ])
                    tot += 1
                         
    print(f"Generated {tot} triangles from:")
    if tris > 0:
        print(f"  - Tris: {tris}")
    if quads_split > 0:
        print(f"  - Quads: {quads_split}")
    if ngons_triangulated > 0:
        print(f"  - N-gons: {ngons_triangulated}")

    # Correct tangents
    for i in range(len(tangents)):
        if length(tangents[i]) == 0:
            continue

        if i >= len(normals):
            continue

        n = normals[i]
        t = tangents[i]

        # Orthagonalize
        EPSILON = 1e-8

        t = sub(t, mul(n, dot(t, n)))

        if length(t) < EPSILON:
            continue

        t = normalize(t)
        tangents[i] = t

        # Rebuild bitangents
        b = cross(n, t)

        # Handedness
        if dot(b, bitangents[i]) < 0.0:
            t = mul(t, -1.0)
            b = cross(n, t)

        tangents[i] = t
        bitangents[i] = b

    vertices = np.array(vertices, dtype=np.float32)
    normals = np.array(normals, dtype=np.float32)
    uv_coords = np.array(uv_coords, dtype=np.float32)

    indices = np.array(indices, dtype=np.int32)
    uv_indices = np.array(uv_indices, dtype=np.int32)
    normal_indices = np.array(normal_indices, dtype=np.int32)
    tangents, bitangents = compute_tangents(
        vertices,
        uv_coords,
        indices.reshape(-1, 3),
        uv_indices.reshape(-1, 3)
    )

    print(f"Parsed {location.split('/')[-1]} in {(time.perf_counter()-start)*1000:.1f}ms")
    return vertices, normals, tangents, bitangents, uv_coords, indices, normal_indices, uv_indices

def parse_objs(locations):
    all_vertices = []
    all_normals = []
    all_tangents = []
    all_bitangents = []
    all_uv_coords = []
    all_indices = []
    all_normal_indices = []
    all_uv_indices = []

    vertex_offset = 0
    normal_offset = 0
    uv_offset = 0
    for location in locations:
        verts, norms, tans, bitans, uvs, inds, n_inds, uv_inds = parse_obj(location)

        all_vertices.extend(verts)
        all_normals.extend(norms)
        all_tangents.extend(tans)
        all_bitangents.extend(bitans)
        all_uv_coords.extend(uvs)

        all_indices.extend([i + vertex_offset for i in inds])
        all_normal_indices.extend([i + normal_offset for i in n_inds])
        all_uv_indices.extend([i+uv_offset for i in uv_inds])

        vertex_offset += len(verts)
        normal_offset += len(norms)
        uv_offset += len(uvs)

    return all_vertices, all_normals, all_tangents, all_bitangents, all_uv_coords, all_indices, all_normal_indices, all_uv_indices

def build_interleaved(vertices, normals, tangents, bitangents, uvs,
                      indices, normal_indices, uv_indices):

    vertex_map = {}
    packed = []
    new_indices = []

    for i in range(len(indices)):
        v_i = indices[i]
        n_i = normal_indices[i]
        uv_i = uv_indices[i]

        key = (v_i, n_i, uv_i)

        if key not in vertex_map:
            pos = vertices[v_i]

            # UV
            if uv_i != -1:
                uv = uvs[uv_i]
                u, v = uv[0], uv[1]
            else:
                u, v = 0.0, 0.0

            # Normal
            if n_i != -1:
                norm = normals[n_i]
                nx, ny, nz = norm[0], norm[1], norm[2]
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            t = tangents[v_i]

            packed.extend([
                pos[0], pos[1], pos[2],
                u, v,
                nx, ny, nz,
                t[0], t[1], t[2]
            ])

            vertex_map[key] = len(vertex_map)

        new_indices.append(vertex_map[key])

    return (
        np.array(packed, dtype="f4"),
        np.array(new_indices, dtype="i4")
    )