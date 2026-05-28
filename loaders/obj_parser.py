import time
import numpy as np
from maths.vector import Vec3, Vec2

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
                vertices.append(Vec3(x, y, z))
                tangents.append(Vec3(0,0,0))
                bitangents.append(Vec3(0,0,0))

            # Normals
            if line.startswith("vn "):
                x, y, z = map(float, line.strip().split()[1:])
                normals.append(Vec3(x, y, z))

            # UV Coords
            if line.startswith("vt "):
                x, y = map(float, line.strip().split()[1:])
                uv_coords.append(Vec2(x, y))

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
                
                    # Generate Tangents
                    if face_uv_coords[0] == -1 or face_uv_coords[i] == -1 or face_uv_coords[i+1] == -1:
                        continue
                    
                    i0, i1, i2 = face_vertices[0], face_vertices[i], face_vertices[i+1]
                    v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
                    uv0 = uv_coords[face_uv_coords[0]]
                    uv1 = uv_coords[face_uv_coords[i]]
                    uv2 = uv_coords[face_uv_coords[i+1]]
                    
                    e1 = v1-v0
                    e2 = v2-v0

                    du1 = uv1.x - uv0.x
                    dv1 = uv1.y - uv0.y
                    du2 = uv2.x - uv0.x
                    dv2 = uv2.y - uv0.y

                    denom = du1 * dv2 - du2 * dv1
                    if denom == 0:
                        continue

                    f = 1.0 / denom

                    tangent = Vec3(
                        f * (dv2 * e1.x - dv1 * e2.x),
                        f * (dv2 * e1.y - dv1 * e2.y),
                        f * (dv2 * e1.z - dv1 * e2.z)
                    )

                    bitangent = Vec3(
                        f * (-du2 * e1.x + du1 * e2.x),
                        f * (-du2 * e1.y + du1 * e2.y),
                        f * (-du2 * e1.z + du1 * e2.z)
                    )

                    tangents[i0] += tangent
                    tangents[i1] += tangent
                    tangents[i2] += tangent

                    bitangents[i0] += bitangent
                    bitangents[i1] += bitangent
                    bitangents[i2] += bitangent

    print(f"Generated {tot} triangles from:")
    if tris > 0:
        print(f"  - Tris: {tris}")
    if quads_split > 0:
        print(f"  - Quads: {quads_split}")
    if ngons_triangulated > 0:
        print(f"  - N-gons: {ngons_triangulated}")

    # Correct tangents
    for i in range(len(tangents)):
        if tangents[i].length() == 0:
            continue

        if i >= len(normals):
            continue

        n = normals[i]
        t = tangents[i]

        # Orthagonalize
        EPSILON = 1e-8

        t = t - n * t.dot(n)

        if t.length() < EPSILON:
            continue

        t = t.normalize()
        tangents[i] = t

        # Rebuild bitangents
        b = n.cross(t)

        # Handedness
        if b.dot(bitangents[i]) < 0.0:
            t = t * -1.0
            b = n.cross(t)

        tangents[i] = t
        bitangents[i] = b

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
                u, v = uv.x, uv.y
            else:
                u, v = 0.0, 0.0

            # Normal
            if n_i != -1:
                norm = normals[n_i]
                nx, ny, nz = norm.x, norm.y, norm.z
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            t = tangents[v_i]

            packed.extend([
                pos.x, pos.y, pos.z,
                u, v,
                nx, ny, nz,
                t.x, t.y, t.z
            ])

            vertex_map[key] = len(vertex_map)

        new_indices.append(vertex_map[key])

    return (
        np.array(packed, dtype="f4"),
        np.array(new_indices, dtype="i4")
    )