import type {ApiPort} from '../application/ports';
import type {Session, StoredFile} from '../domain/models';

export class ApiError extends Error {constructor(readonly code: string, message: string) {super(message);}}
export class HttpApi implements ApiPort {
  private session: Session|null = null;
  setSession(session: Session|null) {this.session=session;}
  async request<T>(path: string, body?: unknown, method='GET', headers: Record<string,string>={}): Promise<T> {
    if(!this.session) throw new ApiError('AUTH_REQUIRED','Войдите через Telegram');
    const response = await fetch(this.session.baseUrl+'/api/v1'+path, {method, redirect:'error', headers:{Authorization:'Bearer '+this.session.token,'Content-Type':'application/json',...headers}, ...(body!==undefined?{body:JSON.stringify(body)}:{})});
    if(response.status===204) return undefined as T;
    const result = await response.json();
    if(!response.ok) throw new ApiError(result.error?.code||'HTTP_ERROR',result.error?.message||'Ошибка сервера');
    return result as T;
  }
  mediaSource(file: StoredFile, thumbnail=false) {
    if(!this.session) throw new ApiError('AUTH_REQUIRED','Войдите через Telegram');
    return {uri:`${this.session.baseUrl}/api/v1/files/${file.id}/${thumbnail?'thumbnail':'content?disposition=inline'}`,headers:{Authorization:'Bearer '+this.session.token}};
  }
}
