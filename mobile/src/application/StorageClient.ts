import type {ApiPort, DevicePort} from './ports';
import type {Collection, DateBucket, DeviceFile, Page, Profile, Session, StoredFile} from '../domain/models';

export class StorageClient {
  constructor(readonly api: ApiPort, readonly device: DevicePort) {}
  async restoreSession() {const session = await this.device.getSession(); this.api.setSession(session); return session;}
  loginResult() {return this.device.pollLogin();}
  profile() {return this.api.request<Profile>('/me');}
  catalog(collection: Collection, q='', date='', cursor='', trash=false) {
    const params = new URLSearchParams({collection, state: trash?'trashed':'active', q, cursor, limit:'100'});
    if(date) {params.set('date_from',date); params.set('date_to',date);}
    return this.api.request<Page<StoredFile>>('/files?'+params.toString());
  }
  dates(collection: Collection) {return this.api.request<Page<DateBucket>>('/files/dates?collection='+collection);}
  trashCatalog(cursor='') {return this.api.request<Page<StoredFile>>('/files?state=trashed&limit=100&cursor='+encodeURIComponent(cursor));}
  async verify(file: StoredFile) {
    const key=String(Date.now())+'-'+Math.random().toString(36).slice(2);
    let check=await this.api.request<{id:string;state:string;integrity:string}>(`/files/${file.id}/verifications`,{},'POST',{'Idempotency-Key':key});
    while(check.state==='queued'||check.state==='running') {await new Promise<void>(resolve=>setTimeout(()=>resolve(),1500));check=await this.api.request<{id:string;state:string;integrity:string}>(`/files/${file.id}/verifications/${check.id}`);}
    return check.state==='succeeded'?'Копия проверена. Размер и SHA-256 совпадают.':'Не удалось подтвердить целостность копии.';
  }
  trash(file: StoredFile) {return this.api.request<StoredFile>(`/files/${file.id}/trash`,{},'POST');}
  restore(file: StoredFile) {return this.api.request<StoredFile>(`/files/${file.id}/restore`,{},'POST');}
  upload(files: DeviceFile[], mode: 'copy'|'move') {return this.device.enqueue(files,mode);}
  async logout() {this.api.setSession(null);await this.device.logout();}
  sessions() {return this.api.request<Page<{id:string;device_name:string;is_current:boolean;last_seen_at:string}>>('/sessions');}
  revokeSession(id: string) {return this.api.request(`/sessions/${id}`,undefined,'DELETE');}
}
