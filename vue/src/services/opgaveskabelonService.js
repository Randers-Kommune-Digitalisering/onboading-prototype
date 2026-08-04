import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const createOpgaveskabelon = (data) => {
    return apiRequest({ method: 'post', url: `${API_URL}/opgaveskabelon`, data });
};
  
export const getOpgaveskabeloner = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/opgaveskabelon` });
};

export const getOpgaveskabelonById = (opgaveskabelon_id) => {
    return apiRequest({ method: 'get', url: `${API_URL}/opgaveskabelon/${opgaveskabelon_id}` });
};

export const updateOpgaveskabelon = (opgaveskabelon_id, data) => {
    return apiRequest({ method: 'put', url: `${API_URL}/opgaveskabelon/${opgaveskabelon_id}`, data });
};

export const deleteOpgaveskabelon = (opgaveskabelon_id) => {
    return apiRequest({ method: 'delete', url: `${API_URL}/opgaveskabelon/${opgaveskabelon_id}` });
};