import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const getEmail = () => {
    return axios.get(`${API_URL}/users/email`);
};
  
  export const getDQ = () => {
    return axios.get(`${API_URL}/users/dq`);
};

export const getAdminNames = () => {
    return axios.get(`${API_URL}/users/admin`);
};

export const getAnvarligNames = () => {
    return axios.get(`${API_URL}/users/fullname`);
}
  
  