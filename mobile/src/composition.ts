import {StorageClient} from './application/StorageClient';
import {HttpApi} from './infrastructure/api';
import {device} from './infrastructure/native';
export const storage = new StorageClient(new HttpApi(),device);
