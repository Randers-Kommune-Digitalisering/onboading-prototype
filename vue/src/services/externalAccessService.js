import { apiRequest } from './apiRequest';

const API_URL = 'api';

export const requestExternalAccess = (forloebId) => {
  return apiRequest({
    method: 'post',
    url: `${API_URL}/external/request-access`,
    data: { forloebId },
  });
};

export const getExternalUserInfo = (forloebId, accessKey) => {
  return apiRequest({
    method: 'get',
    url: `${API_URL}/external/userinfo?forloebId=${forloebId}`,
    config: {
      headers: {
        'X-External-Access-Key': accessKey || '',
      },
    },
  });
};
