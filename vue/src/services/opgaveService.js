import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const createOpgave = (data) => {
  return apiRequest({ method: 'post', url: `${API_URL}/opgave`, data });
};

export const getOpgaverByForloebIDAdmin = (forloebID) => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave/forloeb/admin/${forloebID}` });
};

export const getOpgaverByForloebID = (forloebID, config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave/forloeb/${forloebID}`, config });
};

export const getOpgaverByForloebIDExternal = (forloebID, accessKey) => {
  return apiRequest({
    method: 'get',
    url: `${API_URL}/external/opgave/forloeb/${forloebID}`,
    config: {
      headers: {
        'X-External-Access-Key': accessKey || '',
      },
    },
  });
};

export const getOpgaverByAnsvarligEmail = (config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave/admin`, config });
};

export const getOpgaverByForloebsskabelonID = (forloebsskabelonID, config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave/forloebsskabelon/admin/${forloebsskabelonID}`, config });
};

export const getOpgaveById = (opgaveID) => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave/${opgaveID}` });
};
  
export const deleteOpgave = (opgaveID) => {
    return apiRequest({ method: 'delete', url: `${API_URL}/opgave/${opgaveID}` });
};
  
export const updateOpgave = (opgaveID, data) => {
    return apiRequest({ method: 'put', url: `${API_URL}/opgave/${opgaveID}`, data });
};

export const getOpgaver = () => {
  return apiRequest({ method: 'get', url: `${API_URL}/opgave` });
};

export const createOpgaveWithOpgaveskabelon = (data) => {
  return apiRequest({ method: 'post', url: `${API_URL}/opgave/opgaveskabelon`, data });
};