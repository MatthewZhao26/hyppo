import numpy as np
from hyppo.conditional_independence import FCIT

from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression

dim = 1
n = 100000
np.random.seed(12)
"""
z -> sample n x d from multivariate gaussian
"""

# independent

z1 = np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n))


"""
A -> dim x dim 
"""

A1 = np.random.normal(loc=0, scale=1, size=dim * dim).reshape(dim, dim)
B1 = np.random.normal(loc=0, scale=1, size=dim * dim).reshape(dim, dim)

x1 = (
    A1 @ z1.T
    + np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n)).T
)
y1 = (
    B1 @ z1.T
    + np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n)).T
)

# dependent

np.random.seed(12)
z2 = np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n))

A2 = np.random.normal(loc=0, scale=1, size=dim * dim).reshape(dim, dim)
B2 = np.random.normal(loc=0, scale=1, size=dim * dim).reshape(dim, dim)

x2 = (
    A2 @ z2.T
    + np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n)).T
)
y2 = (
    B2 @ x2
    + np.random.multivariate_normal(mean=np.zeros(dim), cov=np.eye(dim), size=(n)).T
)


model = DecisionTreeRegressor()
k = None
cv_grid = {"min_samples_split": [2, 8, 64, 512, 1e-2, 0.2, 0.4]}

np.random.seed(122)
print(FCIT(model=model, cv_grid=cv_grid).test(x1.T, y1.T, z1))


np.random.seed(122)
print(FCIT(model=model, cv_grid=cv_grid).test(x2.T, y2.T, z2))
