import numpy as np
from scipy import stats
from backend.app.utils import utility


class TreeModel(object):
    """
    A decision tree model that uses random feature selection for splitting nodes.
    The model uses median values for splitting and mode for leaf node predictions.

    Parameters
    ----------
    leaf_size : int, optional
        The maximum number of samples to be aggregated at a leaf node, defaults to 1
    """

    def __init__(self, leaf_size=1):
        """
        Initialize the random decision tree model.
        """
        self.tree_array = None
        self.leaf_size = leaf_size

    def add_evidence(self, data_x, data_y):
        """
        Train the model using the provided data.

        Parameters
        ----------
        data_x : numpy.ndarray
            Feature values used for training
        data_y : numpy.ndarray
            Target values to predict
        """
        data = np.hstack((data_x, np.atleast_2d(data_y).T))
        self.tree_array = self.build_tree(data)

    def query(self, points):
        """
        Make predictions for new data points.

        Parameters
        ----------
        points : numpy.ndarray
            Feature values to predict for

        Returns
        -------
        numpy.ndarray
            Predicted values for each input point
        """
        ret_arr = np.empty(points.shape[0])
        idx = 0
        for point in points:
            ret_arr[idx] = self.predict_y(point, 0)
            idx = idx + 1
        return ret_arr

    def predict_y(self, point, root):
        """
        Recursively traverse the tree to make a prediction for a single point.

        Parameters
        ----------
        point : numpy.ndarray
            Feature values for a single point
        root : int
            Index of the current node in the tree array

        Returns
        -------
        float
            Predicted value for the input point
        """
        if self.tree_array[root, 0] == -1:
            return self.tree_array[root, 1]
        else:
            feature_idx = int(self.tree_array[root, 0])
            feature_val = point[feature_idx]
            if feature_val <= self.tree_array[root, 1]:
                return self.predict_y(point, root + 1)
            else:
                return self.predict_y(point, int(root + self.tree_array[root, -1]))

    def build_tree(self, data):
        """
        Recursively build the decision tree.

        Parameters
        ----------
        data : numpy.ndarray
            Combined feature and target data

        Returns
        -------
        numpy.ndarray
            Tree structure where each row represents a node:
            - Column 0: Feature index (-1 for leaf nodes)
            - Column 1: Split value or prediction value
            - Column 2: Left child index
            - Column 3: Right child index
        """
        data_x = data[:, 0:-1]
        data_y = data[:, -1]
        if data_x.shape[0] <= self.leaf_size:
            mode_result = stats.mode(data_y)
            return np.array([[-1, mode_result.mode, -1, -1]])
        elif utility.all_y_same(data_y):
            return np.array([[-1, data_y[-1], -1, -1]])
        else:
            feature_idx = np.random.randint(data_x.shape[1])
            split_val = np.median(data[:, feature_idx])

            split_idx_left = np.where(data[:, feature_idx] <= split_val)
            split_idx_right = np.where(data[:, feature_idx] > split_val)

            # Handle edge case: can't split into two groups
            if (split_idx_left[0].size == 0) or (split_idx_right[0].size == 0):
                mode_result = stats.mode(data_y)
                return np.array([[-1, mode_result.mode, -1, -1]])

            left_tree = self.build_tree(data[split_idx_left])
            right_tree = self.build_tree(data[split_idx_right])
            root = np.array([feature_idx, split_val, 1, left_tree.shape[0] + 1])

            ret = np.append([root], left_tree, axis=0)
            ret = np.append(ret, right_tree, axis=0)

            return ret
