import numpy as np
from numba import float64, bool_
from skglm.penalties.base import BasePenalty
from skglm.penalties.separable import prox_MCP, value_MCP

class MCP_plus_L2(BasePenalty):
    """MCP + L2 penalty for stabilizing coordinate descent under collinearity."""
    def __init__(self, alpha, gamma, mu, positive=False):
        self.alpha = alpha
        self.gamma = gamma
        self.mu = mu
        self.positive = positive

    def get_spec(self):
        spec = (
            ('alpha', float64),
            ('gamma', float64),
            ('mu', float64),
            ('positive', bool_)
        )
        return spec

    def params_to_dict(self):
        return dict(alpha=self.alpha,
                    gamma=self.gamma,
                    mu=self.mu,
                    positive=self.positive)

    def value(self, w):
        val = value_MCP(w, self.alpha, self.gamma)
        val += self.mu / 2.0 * np.sum(w ** 2)
        return val

    def prox_1d(self, value, stepsize, j):
        denom = 1.0 + stepsize * self.mu
        val_prime = value / denom
        stepsize_prime = stepsize / denom
        return prox_MCP(val_prime, stepsize_prime, self.alpha, self.gamma, self.positive)

    def subdiff_distance(self, w, grad, ws):
        subdiff_dist = np.zeros_like(grad)
        for idx, j in enumerate(ws):
            if self.positive and w[j] < 0:
                subdiff_dist[idx] = np.inf
            elif self.positive and w[j] == 0:
                subdiff_dist[idx] = max(0, - grad[idx] - self.alpha)
            else:
                if w[j] == 0:
                    subdiff_dist[idx] = max(0, np.abs(grad[idx]) - self.alpha)
                elif np.abs(w[j]) < self.alpha * self.gamma:
                    subdiff_dist[idx] = np.abs(
                        grad[idx] + self.alpha * np.sign(w[j]) - w[j] / self.gamma + self.mu * w[j])
                else:
                    subdiff_dist[idx] = np.abs(grad[idx] + self.mu * w[j])
        return subdiff_dist

    def is_penalized(self, n_features):
        return np.ones(n_features, bool_)

    def generalized_support(self, w):
        return w != 0

    def alpha_max(self, gradient0):
        return np.max(np.abs(gradient0))
