import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const createForloebsskabelon = (data) => {
    return apiRequest({ method: 'post', url: `${API_URL}/forlobsskabelon`, data });
};

export const getForloebsskabeloner = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/forlobsskabelon` });
};

export const getForloebsskabelonById = (id) => {
    return apiRequest({ method: 'get', url: `${API_URL}/forlobsskabelon/${id}` });
};

export const getForloebsskabelonerWithOpgavers = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/forlobsskabelon/opgaver` });
};

export const updateForloebsskabelon = (forloebsskabelon_id, data) => {
    return apiRequest({ method: 'put', url: `${API_URL}/forlobsskabelon/${forloebsskabelon_id}`, data });
};

export const deleteForloebsskabelon = (forloebsskabelon_id) => {
    return apiRequest({ method: 'delete', url: `${API_URL}/forlobsskabelon/${forloebsskabelon_id}` });
};