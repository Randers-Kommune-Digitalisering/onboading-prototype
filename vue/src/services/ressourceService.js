import axios from 'axios';

const API_URL = 'api';

export const createRessource = (data) => {
    return axios.post(`${API_URL}/ressource`, data);
};

export const getRessourcesByOpgaveID = async (opgaveID) => {
    try {
        const response = await axios.get(`${API_URL}/ressource/opgave/${opgaveID}`);
        return response;
      } catch (error) {
        if (error.response && error.response.status === 404) {
          return { data: [] }; // Return an empty array or any other custom response
        }
        //throw error; // Re-throw the error if it's not a 404
      }
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

export const getRessourceById = (ressourceID) => {
    return axios.get(`${API_URL}/ressource/${ressourceID}`);
};
