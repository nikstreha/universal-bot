import type {DeviceFile, Session, StoredFile, Transfer} from '../domain/models';
export interface ApiPort {
  request<T>(path: string, body?: unknown, method?: string, headers?: Record<string,string>): Promise<T>;
  setSession(session: Session|null): void;
  mediaSource(file: StoredFile, thumbnail?: boolean): {uri: string; headers: Record<string,string>};
}
export interface DevicePort {
  getSession(): Promise<Session|null>;
  beginLogin(baseUrl: string): Promise<{authorization_url: string; login_code: string}>;
  pollLogin(): Promise<{state: string; access_request_status?: string; session?: Session}>;
  requestAccess(): Promise<{status: string}>;
  logout(): Promise<void>;
  pickFiles(): Promise<DeviceFile[]>;
  enqueue(files: DeviceFile[], mode: 'copy'|'move'): Promise<void>;
  download(file: StoredFile): Promise<void>;
  transfers(): Promise<Transfer[]>;
  action(id: string, action: 'pause'|'resume'|'cancel'): Promise<void>;
  canManageMedia(): Promise<boolean>;
  requestManageMedia(): Promise<void>;
  immersive(enabled: boolean): void;
  preferences(): Promise<{theme: string; columns: number; baseUrl: string}>;
  preference(key: string, value: string): void;
}
