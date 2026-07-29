import time
import numpy as np
import math
import numpy as np
from shard.loaders.helpers import compute_tangents, build_interleaved

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

def load_models(locations):
    vertices, normals, tangents, bitangents, uv_coords, indices, normal_indices, uv_indices = parse_objs(locations)
    return build_interleaved(vertices, normals, tangents, bitangents, uv_coords, indices, normal_indices, uv_indices)