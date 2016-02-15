from collections import defaultdict
from scipy.stats import norm
import numpy as np
import scipy.stats


def rmse(predictions, targets):
    """
    :param predictions: (batch_size, 1)
    :param targets: (batch_size, 1)
    :return: RMSE (mean over batch)
    """
    return np.sqrt(np.mean((predictions - targets) ** 2))


def crps(prediction_cdf, target_cdf):
    """
    Use it with batch_size of 1
    :param prediction_cdf: (batch_size, 600)
    :param target_cdf: (batch_size, 600)
    :return: CRPS mean over batch
    """
    return np.mean((prediction_cdf - target_cdf) ** 2)


def real_to_cdf(y, sigma=1e-10):
    cdf = np.zeros((y.shape[0], 600))
    for i in range(y.shape[0]):
        cdf[i] = norm.cdf(np.linspace(0, 599, 600), y[i], sigma)
    return cdf


def heaviside_function(x):
    return np.float32((np.linspace(0, 599, 600) - x) >= 0)


def get_patient_average_heaviside_predictions(batch_predictions, batch_patient_ids, mean='arithmetic'):
    """

    :param batch_predictions: volume prediction per slice
    :param batch_patient_ids: patient id per slice
    :param mean: type of averaging, default is arithmetic mean
    :return:
    """
    nbatches = len(batch_predictions)
    npredictions = len(batch_predictions[0])

    patient_ids = []
    for i in xrange(nbatches):
        patient_ids += batch_patient_ids[i]

    patient2idxs = defaultdict(list)
    for i, pid in enumerate(patient_ids):
        patient2idxs[pid].append(i)

    patient2cdf = defaultdict(list)  # list[0] -systole cdf, list[1] - diastole cdf
    for i in xrange(npredictions):
        # collect predictions over batches
        p = []
        for j in xrange(nbatches):
            p.append(batch_predictions[j][i])
        p = np.vstack(p)

        # average predictions over patient's predictions
        for patient_id, patient_idxs in patient2idxs.iteritems():
            prediction_cdfs = heaviside_function(p[patient_idxs])
            if mean == 'geometric':
                avg_prediction_cdf = scipy.stats.gmean(prediction_cdfs, axis=0)
            elif mean == 'harmonic':
                avg_prediction_cdf = scipy.stats.hmean(prediction_cdfs, axis=0)
            else:
                # arithmetic mean
                avg_prediction_cdf = np.mean(prediction_cdfs, axis=0)

            patient2cdf[patient_id].append(avg_prediction_cdf)

    return patient2cdf


def get_patient_average_cdf_predictions(batch_predictions, batch_patient_ids, mean='arithmetic'):
    nbatches = len(batch_predictions)
    npredictions = len(batch_predictions[0])

    patient_ids = []
    for i in xrange(nbatches):
        patient_ids += batch_patient_ids[i]

    patient2idxs = defaultdict(list)
    for i, pid in enumerate(patient_ids):
        patient2idxs[pid].append(i)

    patient2cdf = defaultdict(list)  # list[0] -systole cdf, list[1] - diastole cdf
    for i in xrange(npredictions):
        # collect predictions over batches
        p = []
        for j in xrange(nbatches):
            p.append(batch_predictions[j][i])
        p = np.vstack(p)

        # average predictions over patient's predictions
        for patient_id, patient_idxs in patient2idxs.iteritems():
            prediction_cdfs = p[patient_idxs]
            if mean == 'geometric':
                avg_prediction_cdf = scipy.stats.gmean(prediction_cdfs, axis=0)
            elif mean == 'harmonic':
                avg_prediction_cdf = scipy.stats.hmean(prediction_cdfs, axis=0)
            else:
                # arithmetic mean
                avg_prediction_cdf = np.mean(prediction_cdfs, axis=0)
            patient2cdf[patient_id].append(avg_prediction_cdf)

    return patient2cdf
