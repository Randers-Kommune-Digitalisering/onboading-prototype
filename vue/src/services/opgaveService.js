import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

export const createOpgave = (data) => {
  return axios.post(`${API_URL}/opgave`, data);
};

export const getOpgaverByForloebID = (forloebID) => {
    return axios.get(`${API_URL}/opgave/forloeb/${forloebID}`);
};
  
  export const getOpgaverByForloebsskabelonID = (forloebsskabelonID) => {
    return axios.get(`${API_URL}/opgave/forloebsskabelon/${forloebsskabelonID}`);
};
  
  export const deleteOpgave = (opgaveID) => {
    return axios.delete(`${API_URL}/opgave/${opgaveID}`);
};
  
  export const updateOpgave = (opgaveID, data) => {
    return axios.put(`${API_URL}/opgave/${opgaveID}`, data);
};

  export const getOpgaver = () => {
    return axios.get(`${API_URL}/opgave`);
};

export const createOpgaveWithOpgaveskabelon = (data) => {
  return axios.post(`${API_URL}/opgave/opgaveskabelon`, data);
};