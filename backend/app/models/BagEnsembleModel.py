import numpy as np
from scipy import stats


class BagEnsembleModel(object):
    """
    A bagging ensemble model that combines multiple base models to improve prediction accuracy.
    Each model in the ensemble is trained on a bootstrap sample of the training data.

    Parameters
    ----------
    model : class
        The base model class to be used in the ensemble
    kwargs : dict, optional
        Keyword arguments to be passed to the base model constructor
    bags : int, optional
        Number of models in the ensemble, defaults to 20
    """

    def __init__(self, model, kwargs={"argument1": 1, "argument2": 2}, bags=20):
        """
        Initialize the bagging ensemble model.
        """
        self.models = []
        for i in range(0, bags):
            self.models.append(model(**kwargs))

    def add_evidence(self, data_x, data_y):
        """
        Train the ensemble model using the provided data.

        Parameters
        ----------
        data_x : numpy.ndarray
            Feature values used for training
        data_y : numpy.ndarray
            Target values to predict
        """
        for model in self.models:
            index_random = np.random.randint(
                low=0, high=data_x.shape[0], size=data_x.shape[0]
            )
            model.add_evidence(data_x[index_random], data_y[index_random])

    def query(self, points):
        """
        Make predictions using the ensemble model.

        Parameters
        ----------
        points : numpy.ndarray
            Feature values to predict for

        Returns
        -------
        numpy.ndarray
            Predicted values for each input point, determined by majority voting
            across all models in the ensemble
        """
        ret = []
        for model in self.models:
            ret.append(model.query(points))
        return stats.mode(ret).mode
