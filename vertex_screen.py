import numpy as np


def build_rotate_matrix(r, a, b):
    """
    (a,b) = (0,1) (0,2) (1,2)
    (cos,-sin)
    (sin,cos)
    :param r: vector of radius of rotation
    :param a: xyz
    :param b: xyz
    :return: (n,4,4) rotation matrix
    """
    n_frames = r.shape[0]
    c1 = np.cos(r)
    s1 = np.sin(r)
    mat = np.zeros((n_frames, 4, 4), dtype=np.float64)
    mat[:, 0, 0] = 1
    mat[:, 1, 1] = 1
    mat[:, 2, 2] = 1
    mat[:, 3, 3] = 1
    mat[:, a, a] = c1
    mat[:, b, b] = c1
    mat[:, b, a] = s1
    mat[:, a, b] = -s1
    return mat


def build_transition_matrix(t):
    """
    (1,0,0,t[0])
    (0,1,0,t[1])
    (0,0,1,t[2])
    (0,0,0,1)
    :param t: (n,3)
    :return:  (n,4,4)
    """
    n_frames = t.shape[0]
    mat = np.zeros((n_frames, 4, 4), dtype=np.float64)
    mat[:, 0, 0] = 1
    mat[:, 1, 1] = 1
    mat[:, 2, 2] = 1
    mat[:, 3, 3] = 1
    mat[:, 0, 3] = t[:, 0]
    mat[:, 1, 3] = t[:, 1]
    mat[:, 2, 3] = t[:, 2]
    return mat


a_proj = np.array([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, -1, -0.01],
                   [0, 0, -1, 0]], dtype=np.float64)


def build_projection_matrix(f):
    """

    :param f: float32
    :return: (4,4)
    """
    mat = a_proj.copy()
    mat[0, 0] = f
    mat[1, 1] = f
    return mat


def rt(v, tx, ty, tz, r1, r2, r3):
    m_t = build_transition_matrix(np.array([tx, ty, tz], dtype=np.float64).reshape(1, 3))
    m_r1 = build_rotate_matrix(np.full(1, r1, np.float32), 0, 1)
    m_r2 = build_rotate_matrix(np.full(1, r2, np.float32), 0, 2)
    m_r3 = build_rotate_matrix(np.full(1, r3, np.float32), 1, 2)
    m = (m_t @ m_r1 @ m_r2 @ m_r3)[0] @ v
    return m

def rt_matrix(r3t3):
    m_r1 = build_rotate_matrix(r3t3[:, 0], 0, 1)
    m_r2 = build_rotate_matrix(r3t3[:, 1], 0, 2)
    m_r3 = build_rotate_matrix(r3t3[:, 2], 1, 2)
    m_t = build_transition_matrix(r3t3[:, 3:6])
    return m_t @ m_r1 @ m_r2 @ m_r3


def rt_multiframe(vertexes, r3t3, f):
    """

    :param vertexes: size(n_frames * n_vertex_per_frame * 3)
    :param r3t3: shape(n_frames, 6)   6 = [r1,r2,r3,tx,ty,tz]
    :param f: focus_length (assume aspect ratio 1)
    :return: size(n_frames * n_vertex_per_frame * 2)
    """
    n_frames = r3t3.shape[0]
    vertexes = vertexes.reshape((n_frames, -1, 3))
    vertexes = np.concatenate([vertexes, np.ones((vertexes.shape[0], vertexes.shape[1], 1))], axis=2)

    # build transform matrix

    m_rt = rt_matrix(r3t3)
    m_proj = build_projection_matrix(f)

    mat = m_proj @ m_rt
    vertexes = np.transpose(vertexes, (0, 2, 1))
    vertexes = mat @ vertexes
    vertexes = np.transpose(vertexes, (0, 2, 1))
    vertexes = vertexes[:, :, 0:2] / vertexes[:, :, 3][:, :, None]
    return vertexes


def proj(v, f):
    m_proj = build_projection_matrix(f)
    return m_proj @ v
