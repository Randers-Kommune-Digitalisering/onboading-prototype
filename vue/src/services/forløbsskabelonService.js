import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createForloebsskabelon = (data) => {
    return axios.post(`${API_URL}/forlobsskabelon`, data);
};

export const getForloebsskabeloner = () => {
    return axios.get(`${API_URL}/forlobsskabelon`);
};

export const getForloebsskabelonById = (id) => {
    return axios.get(`${API_URL}/forlobsskabelon/${id}`);
};

export const getForloebsskabelonerWithOpgavers = () => {
    return axios.get(`${API_URL}/forlobsskabelon/opgaver`);
};

export const updateForloebsskabelon = (forloebsskabelon_id, data) => {
    return axios.put(`${API_URL}/forlobsskabelon/${forloebsskabelon_id}`, data);
};