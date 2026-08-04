import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const getUsers = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/users` });
};

export const getEmail = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/users/email` });
};
  
  export const getDQ = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/users/dq` });
};

export const getAdminData = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/users/admin` });
};

export const getAnvarligNames = () => {
    return apiRequest({ method: 'get', url: `${API_URL}/users/fullname` });
};
