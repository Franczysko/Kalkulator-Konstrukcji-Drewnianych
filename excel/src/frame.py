"""Independent numeric reference for linear 3D Euler–Bernoulli frames; N, mm."""
import numpy as np


def rotation(a, b):
    x = np.asarray(b, float) - np.asarray(a, float)
    length = np.linalg.norm(x)
    if length <= 1e-8:
        raise ValueError('Zero member length')
    x /= length
    y = np.array([-x[1], x[0], 0.0])
    if np.linalg.norm(y) < 1e-10:
        y = np.array([1., 0., 0.])
    y /= np.linalg.norm(y)
    r = np.array([x, y, np.cross(x, y)])
    return length, r, np.kron(np.eye(4), r)


def local_stiffness(length, e, g, area, iy, iz, torsion):
    k = np.zeros((12, 12))
    for idx, factor in [([0, 6], e*area/length), ([3, 9], g*torsion/length)]:
        k[np.ix_(idx, idx)] = factor*np.array([[1., -1.], [-1., 1.]])
    l = length
    for idx, inertia, sign in [([1, 5, 7, 11], iz, 1), ([2, 4, 8, 10], iy, -1)]:
        block = np.array([[12, sign*6*l, -12, sign*6*l],
                          [sign*6*l, 4*l*l, -sign*6*l, 2*l*l],
                          [-12, -sign*6*l, 12, -sign*6*l],
                          [sign*6*l, 2*l*l, -sign*6*l, 4*l*l]])
        k[np.ix_(idx, idx)] = e*inertia/l**3 * block
    return k


def consistent(q, length):
    x, y, z = np.asarray(q, float)
    l = length
    return np.array([x*l/2, y*l/2, z*l/2, 0, -z*l*l/12, y*l*l/12,
                     x*l/2, y*l/2, z*l/2, 0, z*l*l/12, -y*l*l/12])


def solve(nodes, members, supports, properties, line_loads, nodal_loads=None):
    """members: (i,j,active); properties per member (b,h,E,G); line loads N/mm global."""
    k = np.zeros((36, 36)); f = np.zeros(36)
    if nodal_loads is not None:
        f += np.asarray(nodal_loads).reshape(36)
    elements = []
    for m, (i, j, active) in enumerate(members):
        if not active:
            elements.append(None); continue
        b, h, e, g = properties[m]
        area = b*h; iy = b*h**3/12; iz = h*b**3/12
        aa, bb = max(b, h), min(b, h)
        # Saint-Venant rectangular torsion: convergent Fourier series (25 odd terms).
        torsion = aa*bb**3/3*(1-192*bb/(np.pi**5*aa)*sum(
            np.tanh(n*np.pi*aa/(2*bb))/n**5 for n in range(1, 50, 2)))
        l, r, t = rotation(nodes[i], nodes[j])
        kl = local_stiffness(l, e, g, area, iy, iz, torsion)
        dofs = np.r_[np.arange(i*6, i*6+6), np.arange(j*6, j*6+6)]
        fl = consistent(r@line_loads[m], l)
        k[np.ix_(dofs, dofs)] += t.T@kl@t
        f[dofs] += t.T@fl
        elements.append((kl, t, fl, dofs))
    free = np.flatnonzero(np.asarray(supports).reshape(36) == 0)
    uf = np.linalg.solve(k[np.ix_(free, free)], f[free])
    u = np.zeros(36); u[free] = uf
    reactions = k@u-f
    forces = [np.zeros(12) if el is None else el[0]@el[1]@u[el[3]]-el[2]
              for el in elements]
    return u, reactions, forces, k, f
