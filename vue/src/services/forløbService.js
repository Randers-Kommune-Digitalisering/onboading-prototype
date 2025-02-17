import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createForloeb = (data) => {
  return axios.post(`${API_URL}/forloeb`, data);
};

export const getForloebByEmail = (config) => {
  return axios.get(`${API_URL}/mitforloeb`, config);
};

export const getAllForloeb = () => {
  return axios.get(`${API_URL}/forloeb`);
};

export const getForloebWithOpgaver = () => {
  return axios.get(`${API_URL}/forloeb/opgaver`);
};
