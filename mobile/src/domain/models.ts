export type Theme = 'system' | 'light' | 'dark';
export type Collection = 'media' | 'files';
export interface Session {baseUrl: string; token: string; userId: string}
export interface StoredFile {
  id: string; original_name: string; size_bytes: number; sha256: string;
  storage_date: string; archive_path: string; media_kind: 'photo'|'video'|'audio'|'other';
  mime_type: string; state: string; thumbnail_state: string;
  integrity: {status: string; checked_at: string}; purge_after?: string;
}
export interface Page<T> {items: T[]; next_cursor: string|null}
export interface DateBucket {storage_date: string; file_count: number; size_bytes: number}
export interface DeviceFile {uri: string; name: string; size: number; mime: string}
export interface Transfer {
  id: string; name: string; state: string; mode: 'copy'|'move'; direction: 'upload'|'download';
  size: number; progress: number; error: string; file_id: string;
}
export interface Profile {id: string; name: string; volumes: Record<string, number>; archive_date: string; limits: {max_file_bytes: number}}
