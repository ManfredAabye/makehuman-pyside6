"""
binary file operations on object3d
"""

import numpy as np
import os
from obj3d.fops_wavefront import importWaveFront

def exportObj3dBinary(filename, path, obj):

    content = {}

    # binary structure
    # first header

    lname = len(obj.name)
    header_type = np.dtype({'names':('objname', 'numverts', 'prnt', 'fcnt', 'ucnt'), 'formats':('|S'+str(lname), 'i4', 'i4', 'i4', 'i4')})
    content["header"] = np.array([(obj.name, obj.n_origverts, obj.prim, obj.n_faces, obj.n_fuvs)], dtype=header_type)

    # then all names of the groups
    #
    content["grpNames"] = obj.npGrpNames

    # the xyz coordinates of vertices
    # then uv-coordinates
    #
    content["coord"] = obj.coord
    content["uvs"] = obj.uvs

    # now the overflowbuffer to help OpenGL
    #
    content["overflow"] = obj.overflow 
    ngroups = len(obj.npGrpNames)

    # now the more complex calculation of the faces as
    # index-buffer groups (i4) Element-Start, (i4) NumFaces, and a bool)
    #
    groupinfo = np.zeros(ngroups, dtype=np.dtype('i4,i4,?'))
    allvertnums = 0
    allfaces = 0
    for num, npelem in enumerate (obj.npGrpNames):
        cnt = 0
        elem = npelem.decode("utf-8")
        group = obj.loadedgroups[elem]
        faces = group["v"]
        lfaces = len(faces)
        for face in faces:
            cnt += len(face)
        groupinfo[num] = tuple([allvertnums, lfaces, group["uv"]])
        allvertnums += cnt
        allfaces += lfaces
    
    # relative positions where the faces start
    # and flat array for the vertnumbers itself
    #
    vertsperface = np.zeros(allfaces, dtype=np.dtype('i4'))
    faceverts = np.zeros(allvertnums, dtype=np.dtype('i4'))
    finfocnt = 0
    fvertcnt = 0
    for num, npelem in enumerate (obj.npGrpNames):
        pos = 0
        elem = npelem.decode("utf-8")
        group = obj.loadedgroups[elem]
        faces = group["v"]
        for face in faces:
            for vert in face:
                faceverts[fvertcnt] = vert
                fvertcnt += 1
            vertsperface[finfocnt] = len(face)
            pos += len(face)
            finfocnt += 1

    content["groupinfo"] = groupinfo
    content["vertsperface"] = vertsperface
    content["faceverts"] = faceverts

    if filename.endswith(".obj"):
        filename = filename[:-3] + "npz"
    else:
        filename += ".npz"

    # check if npzip directory exists, if not create it
    # if not possible no zip file + message
    #
    outdir = os.path.join(path, "npzip")
    if not os.path.isdir(outdir):
        print ("Need to create " + outdir)
        obj.env.logLine(8, "Create directory: " + outdir)
        outerr = None
        try:
            os.mkdir(outdir)
        except OSError as error:
            return (False, str(error))

    outfile = os.path.join(outdir, filename)
    obj.env.logLine(8, "Save compressed: " + outfile)
    try:
        f = open(outfile, "wb")
        np.savez_compressed(f, **content)
    except OSError as error:
        return (False, str(error))
    finally:
        f.close()

    return(True, None)


def importObj3dBinary(path, obj):
    print ("read binary " + path)
    npzfile = np.load(path)
    for elem in ['header', 'grpNames', 'coord', 'uvs', 'overflow', 'groupinfo', 'vertsperface', 'faceverts']:
        if elem not in npzfile:
            error =  "Malformed file, missing component " + elem
            return (False, error)

    # now get data from binary, header
    #
    header = list(npzfile['header'][0])
    obj.name        = header[0].decode("utf-8")
    (obj.n_origverts, prim, fcnt, ucnt) = header[1:]

    # next stuff is identical to npz file, number of elements is mostly added
    #
    obj.npGrpNames = npzfile['grpNames']
    obj.n_groups = len(obj.npGrpNames)

    # xyz coordinates of vertices, uvs and OpenGL overflow buffer
    #
    obj.coord    = npzfile["coord"]
    obj.n_verts = len(obj.coord)
    obj.uvs      = npzfile["uvs"]
    obj.n_uvs   = len(obj.uvs)
    obj.overflow = npzfile["overflow"]

    # regenerate groups from groupinfo, vertsperface, faceverts
    # index-buffer groups (Start, NumFaces, bool)
    #
    verts = npzfile["faceverts"]
    fsize = npzfile["vertsperface"]
    groups = {}
    j = 0
    for num, elem in enumerate(npzfile["groupinfo"]):
        start = elem[0]
        faces = elem[1]
        f = []
        fs = start
        for i in range(faces):
            v = []
            for k in range(0, fsize[j]):
                v.append(verts[fs+k])
            f.append(v)
            fs += fsize[j]
            j += 1

        group =  obj.npGrpNames[num].decode("utf-8")
        groups[group] = { "v": f, "uv": elem[2] }

    obj.createGLFaces(fcnt, ucnt, prim, groups)

    return (True, None)

def importObjFromFile(path, obj):
    """
    check if binary file exists, directory in inside subdirectory named npzip
    """
    obj.dir_loaded  = os.path.dirname(path)
    obj.name_loaded = os.path.basename(path)

    if obj.name_loaded.endswith(".obj"):
        binfile = os.path.join(obj.dir_loaded, "npzip", obj.name_loaded[:-3] + "npz")
        if os.path.isfile(binfile):
            return(importObj3dBinary(binfile, obj))

    # only ASCII
    #
    obj.env.logLine(8, "Load: " + path)
    return(importWaveFront(path, obj))

