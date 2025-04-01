import axios from 'axios';

const API_URL = 'api';

export const createOpgaveskabelon = (data) => {
    return axios.post(`${API_URL}/opgaveskabelon`, data);
};
  
export const getOpgaveskabeloner = () => {
    return axios.get(`${API_URL}/opgaveskabelon`);
};

export const getOpgaveskabelonById = (opgaveskabelon_id) => {
    return axios.get(`${API_URL}/opgaveskabelon/${opgaveskabelon_id}`);
};

export const updateOpgaveskabelon = (opgaveskabelon_id, data) => {
    return axios.put(`${API_URL}/opgaveskabelon/${opgaveskabelon_id}`, data);
};

export const deleteOpgaveskabelon = (opgaveskabelon_id) => {
    return axios.delete(`${API_URL}/opgaveskabelon/${opgaveskabelon_id}`);
};