import axios from 'axios';

var USER_INFO = null;

export const getUserInfoFromBackend = () => {
    return axios.get(`api/userinfo`);
};

export async function getUserInfo() {
    if (!USER_INFO) {
      console.log('Fetching user info from backend...');
      const res = await getUserInfoFromBackend();
      USER_INFO = res.data;
    }
    return USER_INFO;
}