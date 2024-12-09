import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createOpgave = (data) => {
  return axios.post(`${API_URL}/opgave`, data);
};

export const createForloeb = (data) => {
  return axios.post(`${API_URL}/forloeb`, data);
};

export const getOpgaverByForloebID = (forloebID) => {
  return axios.get(`${API_URL}/opgave/forloeb/${forloebID}`);
};

export const getOpgaverByForloebsskabelonID = (forloebsskabelonID) => {
  return axios.get(`${API_URL}/opgave/forloebsskabelon/${forloebsskabelonID}`);
};

export const updateOpgaveResult = (opgaveID, result) => {
  return axios.put(`${API_URL}/opgave/result/${opgaveID}`, { result });
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

export const getOpgaver = () => {
  return axios.get(`${API_URL}/opgave`);
};

export const getOpgaveskabeloner = () => {
  return axios.get(`${API_URL}/opgaveskabelon`);
};

export const getForloebsskabelonerWithOpgavers = () => {
  return axios.get(`${API_URL}/forlobsskabelon/opgaver`);
};

export const deleteOpgave = (opgaveID) => {
  return axios.delete(`${API_URL}/opgave/${opgaveID}`);
}
