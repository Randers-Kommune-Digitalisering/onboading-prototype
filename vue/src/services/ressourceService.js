import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createRessource = (data) => {
    return axios.post(`${API_URL}/ressource`, data);
};

export const getRessourcesByOpgaveID = (opgaveID) => {
    return axios.get(`${API_URL}/ressource/opgave/${opgaveID}`);
};

export const deleteRessource = (ressourceID) => {
    return axios.delete(`${API_URL}/ressource/${ressourceID}`);
};

export const updateRessource = (ressourceID, data) => {
    return axios.put(`${API_URL}/ressource/${ressourceID}`, data);
};

export const getRessourcesByOpgaveskabelonID = (opgaveskabelonID) => {
    return axios.get(`${API_URL}/ressource/opgaveskabelon/${opgaveskabelonID}`);
};