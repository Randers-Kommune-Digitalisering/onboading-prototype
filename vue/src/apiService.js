import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createForloeb = (data) => {
  return axios.post(`${API_URL}/forloeb`, data);
};

export const createRessource = (data) => {
  return axios.post(`${API_URL}/ressource`, data);
};

export const createForloebsskabelon = (data) => {
  return axios.post(`${API_URL}/forlobsskabelon`, data);
};

export const createOpgaveskabelon = (data) => {
  return axios.post(`${API_URL}/opgaveskabelon`, data);
};

export const getForloebsskabeloner = () => {
  return axios.get(`${API_URL}/forlobsskabelon`);
};

export const getOpgaveskabeloner = () => {
  return axios.get(`${API_URL}/opgaveskabelon`);
};

export const getForloebsskabelonerWithOpgavers = () => {
  return axios.get(`${API_URL}/forlobsskabelon/opgaver`);
};

export const updateOpgave = (opgaveID, data) => {
  return axios.put(`${API_URL}/opgave/${opgaveID}`, data);
};