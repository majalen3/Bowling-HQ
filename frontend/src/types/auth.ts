export type UserCreate = {
  email: string;
  display_name: string;
  password: string;
};

export type UserLogin = {
  email: string;
  password: string;
};

export type Token = {
  access_token: string;
  token_type: string;
};

export type UserResponse = {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
};
