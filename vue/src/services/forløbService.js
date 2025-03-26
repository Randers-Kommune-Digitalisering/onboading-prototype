import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createForloeb = (data) => {
  return axios.post(`${API_URL}/forloeb`, data);
};

export const getForloebByAdmin = (config) => {
  return axios.get(`${API_URL}/forloeb`, config);
};

export const getForloebByEmail = (config) => {
  return axios.get(`${API_URL}/mitforloeb`, config);
};

export const getForloebById = (id, config) => {
  return axios.get(`${API_URL}/forloeb/${id}`, config);
};

export const getAllForloeb = () => {
  return axios.get(`${API_URL}/forloeb`);
};

export const getForloebWithOpgaver = () => {
  return axios.get(`${API_URL}/forloeb/opgaver`);
};

export const updateForloeb = (forloeb_id, data) => {
  return axios.put(`${API_URL}/forloeb/${forloeb_id}`, data);
};

export const completeForloeb = (forloeb_id) => {
  return axios.put(`${API_URL}/forloeb/complete/${forloeb_id}`);
};

export const deleteForloeb = (forloeb_id) => {
  return axios.delete(`${API_URL}/forloeb/${forloeb_id}`);
};