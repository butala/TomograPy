"""
Generate Shepp-Logan phantoms.
"""
import numpy as np

# define ellipsoid parameters
#default_dict = dict('A': , 'a':, 'b': , 'c':,
#                    'x0':, 'y0': , 'z0':,
#                    'phi': , 'theta': , 'psi': ),

parameters_tuple = ['A', 'a', 'b', 'c', 'x0', 'y0', 'z0', 'phi', 'theta', 'psi']

modified_shepp_logan_array = [
    [  1,  .6900,  .920,  .810,    0.,       0.,      0.,     0.,     0.,      0.],
    [-.8,  .6624,  .874,  .780,    0.,   -.0184,      0.,     0.,     0.,      0.],
    [-.2,  .1100,  .310,  .220,    .22,      0.,      0.,    -18,     0.,     10,],
    [-.2,  .1600,  .410,  .280,   -.22,      0.,      0.,     18,     0.,     10,],
    [ .1,  .2100,  .250,  .410,     0.,     .35,    -.15,     0.,     0.,     0.,],
    [ .1,  .0460,  .046,  .050,     0.,      .1,     .25,     0.,     0.,     0.,],
    [ .1,  .0460,  .046,  .050,     0.,     -.1,     .25,     0.,     0.,     0.,],
    [ .1,  .0460,  .023,  .050,   -.08,   -.605,      0.,     0.,     0.,     0.,],
    [ .1,  .0230,  .023,  .020,     0.,   -.606,      0.,     0.,     0.,     0.,],
    [ .1,  .0230,  .046,  .020,    .06,   -.605,      0.,     0.,     0.,     0.,]]

def _array_to_parameters(array):
    array = np.asarray(array).T
    out = []
    for j in xrange(array.shape[1]):
        tmp = dict()
        for k, i in zip(parameters_tuple, xrange(array.shape[0])):
            tmp[k] = array[i, j]
        out.append(tmp)
    return out

modified_shepp_logan_parameters = _array_to_parameters(modified_shepp_logan_array)

def phantom(shape, parameters_list, dtype=np.float64):
    """
    Generate a cube of given shape using a list of ellipsoid
    parameters
    """
    # instantiate ndarray cube
    cube = np.zeros(shape, dtype=dtype)
    # define coordinates
    coordinates = define_coordinates(shape)
    # recursively add ellipsoids to cube
    for parameters in parameters_list:
        ellipsoid(parameters, out=cube, coordinates=coordinates)
    return cube

def ellipsoid(parameters, shape=None, out=None, coordinates=None):
    """
    Generate a cube containing an ellipsoid defined by its parameters.
    If out is given, fills the given cube instead of creating a new
    one.
    """
    # handle inputs
    if shape is None and out is None:
        raise ValueError("You need to set shape or out")
    if out is None:
        out = np.zeros(shape)
    if shape is None:
        shape = out.shape
    if coordinates is None:
        coordinates = define_coordinates(shape)
    # rotate coordinates
    coordr = rotate(coordinates, parameters)
    # center coordinates
    coordc = center(coordr, parameters)
    # scale coordinates
    coords = scale(coordc, parameters)
    # recast as ndarray
    coords = [np.asarray(u) for u in coords]
    # reshape coordinates
    x, y, z = coords
    x.resize(shape)
    y.resize(shape)
    z.resize(shape)
    # fill ellipsoid with value
    out[(x ** 2 + y ** 2 + z ** 2) <= 1.] += parameters['A']
    return out

def rotation_matrix(p):
    """
    Defines an Euler rotation matrix from ellipsoid parameters
    """
    cphi = np.cos(np.radians(p['phi']))
    sphi = np.sin(np.radians(p['phi']))
    ctheta = np.cos(np.radians(p['theta']))
    stheta = np.sin(np.radians(p['theta']))
    cpsi = np.cos(np.radians(p['psi']))
    spsi = np.sin(np.radians(p['psi']))
    alpha = [[cpsi * cphi - ctheta * sphi * spsi,
              cpsi * sphi + ctheta * cphi * spsi,
              spsi * stheta],
             [-spsi * cphi - ctheta * sphi * cpsi,
               -spsi * sphi + ctheta * cphi * cpsi,
               cpsi * stheta],
             [stheta * sphi,
              -stheta * cphi,
              ctheta]]
    return np.asarray(alpha)

def define_coordinates(shape):
    mgrid = np.lib.index_tricks.nd_grid()
    cshape = np.asarray(1j) * shape
    x, y, z = mgrid[-1:1:cshape[0], -1:1:cshape[1], -1:1:cshape[1]]
    return x, y, z

def rotate(coordinates, parameters):
    alpha = rotation_matrix(parameters)
    x, y, z = coordinates
    xo, yo, zo = [], [], []
    for xi, yi, zi in zip(x.flat, y.flat, z.flat):
        xt, yt, zt = np.dot(alpha, np.asarray([xi, yi, zi]))
        xo.append(xt)
        yo.append(yt)
        zo.append(zt)
    return xo, yo, zo

def center(coordinates, p):
    x, y, z = coordinates
    xo, yo, zo = [], [], []
    for xi, yi, zi in zip(x, y, z):
        xo.append(xi - p['x0'])
        yo.append(yi - p['y0'])
        zo.append(zi - p['z0'])
    return xo, yo, zo

def scale(coordinates, p):
    x, y, z = coordinates
    xo, yo, zo = [], [], []
    for xi, yi, zi in zip(x, y, z):
        xo.append(xi / p['a'])
        yo.append(yi / p['b'])
        zo.append(zi / p['c'])
    return xo, yo, zo
