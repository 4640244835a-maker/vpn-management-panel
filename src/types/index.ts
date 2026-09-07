export type ProtocolType = 'vless' | 'vmess' | 'trojan' | 'shadowsocks';
export type UserStatus = 'active' | 'disabled' | 'limited' | 'expired';

export interface Admin {
  id: number;
  username: string;
  is_sudo: boolean;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  proxiesUuid: string;
  status: UserStatus;
  dataLimit: number | null;
  usedTraffic: number;
  expireDate: string | null;
  subToken: string;
  inboundTags: string[];
}