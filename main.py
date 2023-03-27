import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

def gravity_model(gym_data, population_data, competition_data=None):
    """
    Estimates the demand for gym memberships using the gravity model.

    Parameters
    ----------
    gym_data : pandas.DataFrame
        A DataFrame containing information about the gyms, including their attractiveness score
        and their location coordinates.
    population_data : pandas.DataFrame
        A DataFrame containing information about the local populations, including their population
        count and their location coordinates.
    competition_data : pandas.DataFrame, optional
        A DataFrame containing information about the competing gyms, including their attractiveness
        score and location coordinates. If not provided, assumes that there are no competing gyms.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the demand for gym memberships for each gym.
    """
    # Calculate the distance matrix between gyms and local populations
    gym_coords = gym_data[['x', 'y']].values
    pop_coords = population_data[['x', 'y']].values
    distances = cdist(gym_coords, pop_coords, metric='euclidean')

    # Calculate the competition distance matrix
    if competition_data is not None:
        comp_coords = competition_data[['x', 'y']].values
        competition_distances = cdist(gym_coords, comp_coords, metric='euclidean')
    else:
        competition_distances = None

    # Calculate the demand matrix using the gravity model
    attractiveness = gym_data['attractiveness'].values.reshape(-1, 1)
    population_count = population_data['population_count'].values.reshape(1, -1)
    demand_matrix = gravity_model_func(attractiveness, distances, population_count, competition_data, competition_distances)

    # Aggregate the demand by gym
    demand_by_gym = np.sum(demand_matrix, axis=1)

    # Create a DataFrame of demand by gym
    demand_data = pd.DataFrame({'gym_name': gym_data['gym_name'], 'demand': demand_by_gym})

    return demand_data

def gravity_model_func(attractiveness, distance, population_count, competition_data=None, competition_distance=None):
    """
    Implements the gravity model to estimate the demand for gym memberships.

    Parameters
    ----------
    attractiveness : numpy.ndarray
        A 2D array containing the attractiveness score for each gym.
    distance : numpy.ndarray
        A 2D array containing the distance between each gym and each local population.
    population_count : numpy.ndarray
        A 2D array containing the population count for each local population.
    competition_data : pandas.DataFrame, optional
        A DataFrame containing information about the competing gyms, including their attractiveness
        score and location coordinates. If not provided, assumes that there are no competing gyms.
    competition_distance : numpy.ndarray, optional
        A 2D array containing the distance between each gym and each competing gym. Only used if
        competition_data is provided.

    Returns
    -------
    numpy.ndarray
        A 2D array containing the demand for gym memberships for each gym and each local population.
    """
    # Calculate the competition factor
    if competition_data is not None:
        competition_attractiveness = competition_data['attractiveness'].values.reshape(-1, 1)
        competition_factor = competition_attractiveness / competition_distance**2
    else:
        competition_factor = 0

    # Calculate the demand using the gravity model
    demand = attractiveness * population_count / distance**2
    competition_demand = competition_factor * population_count / competition_distance**2
    net_demand = demand - competition_demand

    return net_demand
