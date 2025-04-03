import axios from 'axios';

const API_URL = 'api';

export const getUsers = () => {
    return axios.get(`${API_URL}/users`);
};

export const getEmail = () => {
    return axios.get(`${API_URL}/users/email`);
};
  
  export const getDQ = () => {
    return axios.get(`${API_URL}/users/dq`);
};

export const getAdminData = () => {
    return axios.get(`${API_URL}/users/admin`);
};

export const getAnvarligNames = () => {
    return axios.get(`${API_URL}/users/fullname`);
};  
