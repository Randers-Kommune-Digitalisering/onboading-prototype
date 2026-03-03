import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const createForloeb = (data) => {
  return apiRequest({ method: 'post', url: `${API_URL}/forloeb`, data });
};

export const startForloeb = (data) => {
  return apiRequest({ method: 'post', url: `${API_URL}/forloeb-start`, data });
};

export const createForloebPreparation = (data) => {
  return apiRequest({ method: 'post', url: `${API_URL}/forloeb-preparation`, data });
};

export const getForloebByAdmin = (config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/forloeb`, config });
};

export const getForloebByEmail = (config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/mitforloeb`, config });
};

export const getForloebById = (id, config) => {
  return apiRequest({ method: 'get', url: `${API_URL}/forloeb/${id}`, config });
};

export const getAllForloeb = () => {
  return apiRequest({ method: 'get', url: `${API_URL}/forloeb` });
};

export const getForloebWithOpgaver = () => {
  return apiRequest({ method: 'get', url: `${API_URL}/forloeb/opgaver` });
};

export const updateForloeb = (forloeb_id, data) => {
  return apiRequest({ method: 'put', url: `${API_URL}/forloeb/${forloeb_id}`, data });
};

export const completeForloeb = (forloeb_id) => {
  return apiRequest({ method: 'put', url: `${API_URL}/forloeb/complete/${forloeb_id}` });
};

export const deleteForloeb = (forloeb_id) => {
  return apiRequest({ method: 'delete', url: `${API_URL}/forloeb/${forloeb_id}` });
};