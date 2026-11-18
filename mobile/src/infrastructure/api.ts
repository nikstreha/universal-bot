import type {ApiPort} from '../application/ports';
import type {Session, StoredFile} from '../domain/models';
import {NativeModules} from 'react-native';

export class ApiError extends Error {constructor(readonly code: string, message: string) {super(message);}}
export class HttpApi implements ApiPort {
  private session: Session|null = null;
  setSession(session: Session|null) {this.session=session;}
  async request<T>(path: string, body?: unknown, method='GET', headers: Record<string,string>={}): Promise<T> {
    if(!this.session) throw new ApiError('AUTH_REQUIRED','Войдите через Telegram');
    const session=this.session;
    try {
      const result=await NativeModules.StorageBridge.request(path,method,body===undefined?null:JSON.stringify(body),headers,session.localId);
      if(this.session!==session)throw new ApiError('SESSION_CHANGED','Сессия изменилась');
      return JSON.parse(result) as T;
    } catch(error) {
      if(this.session!==session)throw new ApiError('SESSION_CHANGED','Сессия изменилась');
      if(error instanceof ApiError)throw error;
      const failure=error as {code?:string;message?:string};
      throw new ApiError(failure.code||'HTTP_ERROR',failure.message||'Ошибка сервера');
    }
  }
  mediaSource(file: StoredFile, thumbnail=false) {
    if(!this.session) throw new ApiError('AUTH_REQUIRED','Войдите через Telegram');
    return {uri:`${this.session.baseUrl}/api/v1/files/${encodeURIComponent(file.id)}/${thumbnail?'thumbnail':'content?disposition=inline'}`,headers:{}};
  }
}
