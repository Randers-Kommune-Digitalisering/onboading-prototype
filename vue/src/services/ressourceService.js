import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const createRessource = (data) => {
    return apiRequest({ method: 'post', url: `${API_URL}/ressource`, data });
};

export const getRessourcesByOpgaveID = (opgaveID) => {
    return apiRequest({ method: 'get', url: `${API_URL}/ressource/opgave/${opgaveID}` });
};

export const deleteRessource = (ressourceID) => {
    return apiRequest({ method: 'delete', url: `${API_URL}/ressource/${ressourceID}` });
};

export const updateRessource = (ressourceID, data) => {
    return apiRequest({ method: 'put', url: `${API_URL}/ressource/${ressourceID}`, data });
};

export const getRessourcesByOpgaveskabelonID = (opgaveskabelonID) => {
    return apiRequest({ method: 'get', url: `${API_URL}/ressource/opgaveskabelon/${opgaveskabelonID}` });
};

export const getRessourceById = (ressourceID) => {
    return apiRequest({ method: 'get', url: `${API_URL}/ressource/${ressourceID}` });
};
