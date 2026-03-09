import { apiRequest } from './apiRequest';

let CACHED_USER_INFO = null;
let IN_FLIGHT_USER_INFO_PROMISE = null;

const ROLE_ADMIN = 'Admin';
const ROLE_NY_MEDARBEJDER = 'Ny medarbejder';
const ROLE_PUBLIC = 'Public';

function toArray(value) {
    return Array.isArray(value) ? value : [];
}

function defaultPublicUserInfo() {
    return {
        roles: [ROLE_PUBLIC],
        isAdmin: false,
        isMedarbejder: false,
    };
}

function normalizeUserInfo(rawUserInfo) {
    let roles = toArray(rawUserInfo?.roles);
    if (roles.length === 0 && rawUserInfo) {
        roles = [ROLE_NY_MEDARBEJDER];
    }

    const isAdmin = roles.includes(ROLE_ADMIN);
    const isPublic = roles.includes(ROLE_PUBLIC);

    // Treat any authenticated, non-admin user as a medarbejder even if Keycloak
    // doesn't explicitly assign the role.
    if (rawUserInfo && !isAdmin && !isPublic && !roles.includes(ROLE_NY_MEDARBEJDER)) {
        roles = [...roles, ROLE_NY_MEDARBEJDER];
    }

    const isMedarbejder = roles.includes(ROLE_NY_MEDARBEJDER) || (!isAdmin && !isPublic);

    return {
        ...(rawUserInfo ?? {}),
        roles,
        isAdmin,
        isMedarbejder,
    };
}

export const getUserInfoFromBackend = () => {
    // Leading slash avoids route-relative requests like /forloeb-overview/api/userinfo
    return apiRequest({ method: 'get', url: '/api/userinfo' });
};

export async function getUserInfo() {
    if (CACHED_USER_INFO) {
        return CACHED_USER_INFO;
    }

    if (IN_FLIGHT_USER_INFO_PROMISE) {
        return IN_FLIGHT_USER_INFO_PROMISE;
    }

    IN_FLIGHT_USER_INFO_PROMISE = (async () => {
        console.log('Fetching user info from backend...');
        try {
            const response = await getUserInfoFromBackend();
            const normalized = normalizeUserInfo(response?.data);
            CACHED_USER_INFO = normalized;
            return normalized;
        } catch (error) {
            console.warn('No user info:', error);
            const fallback = defaultPublicUserInfo();
            CACHED_USER_INFO = fallback;
            return fallback;
        } finally {
            IN_FLIGHT_USER_INFO_PROMISE = null;
        }
    })();

    return IN_FLIGHT_USER_INFO_PROMISE;
}