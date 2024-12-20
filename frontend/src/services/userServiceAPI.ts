class UserServiceAPI {
    private static instance: UserServiceAPI;

    private constructor() { }

    public static getInstance(): UserServiceAPI {

        if (!UserServiceAPI.instance) {
            UserServiceAPI.instance = new UserServiceAPI();
        }

        return UserServiceAPI.instance;
    }
}

export default UserServiceAPI;