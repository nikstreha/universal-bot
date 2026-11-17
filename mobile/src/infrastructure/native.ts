import {NativeModules} from 'react-native';
import type {DevicePort} from '../application/ports';
const bridge = NativeModules.StorageBridge;
async function call(name: string, ...args: unknown[]) {return JSON.parse(await bridge[name](...args));}
export const device: DevicePort = {
  getSession:()=>call('getSession'), beginLogin:url=>call('beginLogin',url), pollLogin:()=>call('pollLogin'),
  requestAccess:()=>call('requestAccess'), logout:()=>call('logout'), pickFiles:()=>call('pickFiles'),
  enqueue:(files,mode)=>call('enqueue',files,mode), download:file=>call('download',file),
  transfers:()=>call('transfers'), action:(id,action)=>call('action',id,action),
  canManageMedia:()=>call('canManageMedia'), requestManageMedia:()=>call('requestManageMedia'),
  immersive:enabled=>bridge.immersive(enabled), preferences:()=>call('preferences'),
  preference:(key,value)=>bridge.preference(key,value),
};
