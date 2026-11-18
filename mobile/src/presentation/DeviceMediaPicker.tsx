import React, {useEffect, useMemo, useRef, useState} from 'react';
import {ActivityIndicator, AppState, FlatList, Linking, PermissionsAndroid, Platform, Pressable, StyleSheet, Text, View} from 'react-native';
import {storage} from '../composition';
import {GridControls, MediaGrid, type GridPalette} from './MediaGrid';
import type {DeviceAlbum, DeviceFile, DeviceMedia} from '../domain/models';


type Access='checking'|'full'|'partial'|'denied';

export function DeviceMediaPicker({sessionId,color,columns,onColumnsChange,onBack,onSelected}: {
  sessionId:string;color:GridPalette;columns:number;onColumnsChange:(value:number)=>void;onBack:()=>void;onSelected:(files:DeviceFile[])=>void;
}) {
  const [access,setAccess]=useState<Access>('checking');
  const [albums,setAlbums]=useState<DeviceAlbum[]>([]),[album,setAlbum]=useState(''),[showAlbums,setShowAlbums]=useState(false);
  const [items,setItems]=useState<DeviceMedia[]>([]),[cursor,setCursor]=useState<string|null>(null);
  const [selected,setSelected]=useState<Map<string,DeviceMedia>>(new Map());
  const [loading,setLoading]=useState(false),[submitting,setSubmitting]=useState(false),[error,setError]=useState('');
  const [revision,setRevision]=useState(0);
  const generation=useRef(0),busy=useRef(false),live=useRef(true);
  const version=Number(Platform.Version),permission=PermissionsAndroid.PERMISSIONS;
  const required=version>=34?[permission.READ_MEDIA_IMAGES,permission.READ_MEDIA_VIDEO,permission.READ_MEDIA_VISUAL_USER_SELECTED]:version>=33?[permission.READ_MEDIA_IMAGES,permission.READ_MEDIA_VIDEO]:[permission.READ_EXTERNAL_STORAGE];
  const checkAccess=async():Promise<Access>=>{
    const results=await Promise.all(required.map(p=>PermissionsAndroid.check(p)));
    if(version<33)return results[0]?'full':'denied';
    // Images or videos can be granted independently.
    if(results[0]&&results[1])return 'full';
    return results.some(Boolean)?'partial':'denied';
  };
  const requestAccess=async()=>{
    try{
      await PermissionsAndroid.requestMultiple(required);
      const next=await checkAccess();
      if(live.current){setAccess(next);setSelected(new Map());setRevision(v=>v+1);}
    }catch{if(live.current)setError('Не удалось получить доступ к медиатеке.');}
  };
  useEffect(()=>{
    live.current=true;
    void requestAccess();
    const listener=AppState.addEventListener('change',state=>{
      if(state==='active')void checkAccess().then(next=>{
        if(live.current){setAccess(next);setSelected(new Map());setRevision(v=>v+1);}
      }).catch(()=>{if(live.current)setAccess('denied');});
    });
    return()=>{live.current=false;generation.current++;listener.remove();};
  },[sessionId]);
  const load=async(more=false)=>{
    if(busy.current||access==='checking'||access==='denied'||more&&!cursor)return;
    const id=generation.current;busy.current=true;setLoading(true);setError('');
    try{
      const page=await storage.device.deviceMedia(album,more?cursor||'':'',sessionId);
      if(!live.current||generation.current!==id)return;
      setItems(old=>more?[...old,...page.items.filter(file=>!old.some(item=>item.uri===file.uri))]:page.items);
      setCursor(page.next_cursor);
    }catch{if(live.current&&generation.current===id)setError('Не удалось прочитать медиатеку. Проверьте разрешения и повторите.');}
    finally{if(live.current&&generation.current===id){busy.current=false;setLoading(false);}}
  };
  useEffect(()=>{
    generation.current++;busy.current=false;setItems([]);setCursor(null);setLoading(false);
    void load();
  },[album,access,revision,sessionId]);
  useEffect(()=>{
    if(access==='checking'||access==='denied'){setAlbums([]);return;}
    let current=true;
    storage.device.deviceAlbums(sessionId).then(rows=>{if(current)setAlbums(rows);}).catch(()=>{if(current)setAlbums([]);});
    return()=>{current=false;};
  },[access,revision,sessionId]);
  const submit=async()=>{
    if(submitting||!selected.size)return;
    setSubmitting(true);setError('');
    try{
      const files=await storage.device.selectDeviceMedia([...selected.keys()],sessionId);
      if(live.current)onSelected(files);
    }catch{if(live.current)setError('Один из файлов стал недоступен. Обновите медиатеку и выберите файлы заново.');}
    finally{if(live.current)setSubmitting(false);}
  };
  const gridItems=useMemo(()=>items.map(file=>({id:file.uri,uri:file.uri,label:file.name,video:file.kind==='video'})),[items]);
  const selectedIds=useMemo(()=>[...selected.keys()],[selected]);
  const updateSelection=(ids:string[])=>setSelected(previous=>{
    const available=new Map([...previous,...items.map(file=>[file.uri,file] as const)]);
    return new Map(ids.flatMap(id=>{const file=available.get(id);return file?[[id,file] as const]:[];}));
  });
  const text={color:color.ink};
  return <View style={styles.fill}>
    <View style={styles.header}>
      <Pressable accessibilityRole="button" accessibilityLabel="Назад" onPress={onBack} style={({pressed})=>[styles.icon,{backgroundColor:color.surface,borderColor:color.line,opacity:pressed?0.65:1}]}><Text style={[text,{fontSize:30}]}>‹</Text></Pressable>
      <Text numberOfLines={1} style={[text,styles.title]}>С устройства</Text>
      <Text style={{color:color.muted}}>{selected.size} / 1000</Text>
    </View>
    <Pressable accessibilityRole="button" onPress={()=>setShowAlbums(v=>!v)} style={({pressed})=>[styles.album,{borderColor:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]}>
      <Text style={text}>{showAlbums?'Альбомы':albums.find(a=>a.id===album)?.name||'Все фото и видео'} {showAlbums?'⌃':'⌄'}</Text>
    </Pressable>
    <GridControls columns={columns} onChange={onColumnsChange} color={color}/>
    <Text style={{color:color.muted,paddingHorizontal:16,paddingBottom:8,fontSize:12}}>Два пальца — сетка. Удержание и проведение — выделение.</Text>
    {access==='partial'?<View style={styles.notice}><Text style={{color:color.muted}}>Показаны только разрешённые фото и видео.</Text><Pressable onPress={()=>void requestAccess()} accessibilityRole="button" style={({pressed})=>[styles.link,{borderWidth:1,borderRadius:5,borderColor:color.line,backgroundColor:color.surface,paddingHorizontal:12,marginTop:6,opacity:pressed?0.65:1}]}><Text style={{color:color.accent}}>Изменить доступ</Text></Pressable></View>:null}
    {access==='denied'?<View style={styles.notice}><Text style={text}>Разрешите доступ к фото и видео, чтобы выбрать файлы здесь.</Text><Pressable onPress={()=>void requestAccess()} accessibilityRole="button" style={({pressed})=>[styles.link,{borderWidth:1,borderRadius:5,borderColor:color.line,backgroundColor:color.surface,paddingHorizontal:12,marginTop:6,opacity:pressed?0.65:1}]}><Text style={{color:color.accent}}>Разрешить доступ</Text></Pressable><Pressable onPress={()=>void Linking.openSettings()} accessibilityRole="button" style={({pressed})=>[styles.link,{borderWidth:1,borderRadius:5,borderColor:color.line,backgroundColor:color.surface,paddingHorizontal:12,marginTop:6,opacity:pressed?0.65:1}]}><Text style={{color:color.accent}}>Настройки Android</Text></Pressable></View>:null}
    {error?<Pressable onPress={()=>{setSelected(new Map());setRevision(v=>v+1);}} style={styles.notice}><Text style={{color:color.accent}}>{error} Повторить</Text></Pressable>:null}
    {showAlbums?<FlatList data={[{id:'',name:'Все фото и видео',count:albums.reduce((sum,a)=>sum+a.count,0)},...albums]} keyExtractor={item=>item.id} renderItem={({item})=><Pressable accessibilityRole="button" onPress={()=>{setAlbum(item.id);setShowAlbums(false);}} style={({pressed})=>[styles.album,{borderColor:color.line,backgroundColor:pressed?color.surface:color.bg}]}><Text style={{color:album===item.id?color.accent:color.ink}}>{item.name}</Text><Text style={{color:color.muted}}>{item.count} ›</Text></Pressable>}/>:<MediaGrid items={gridItems} catalogKey={album+access+revision} columns={columns} onColumnsChange={onColumnsChange} color={color}
      selectedIds={selectedIds} onSelectionChange={updateSelection} hasMore={!!cursor} loading={loading||access==='checking'}
      onLoadMore={()=>void load(true)} onRefresh={()=>{setSelected(new Map());setRevision(v=>v+1);}}
      emptyText={access==='denied'?'Разрешите доступ к медиатеке.':'В этом альбоме нет доступных фото и видео.'}/>}
    <View style={[styles.footer,{borderColor:color.line,backgroundColor:color.bg}]}>
      <Pressable accessibilityRole="button" disabled={!selected.size||submitting} onPress={()=>setSelected(new Map())} style={({pressed})=>[styles.clear,{borderColor:color.line,backgroundColor:color.surface,opacity:!selected.size?0.4:pressed?0.65:1}]}><Text style={text}>Снять</Text></Pressable>
      <Pressable accessibilityRole="button" disabled={!selected.size||submitting} onPress={()=>void submit()} style={({pressed})=>[styles.button,{flex:1,borderWidth:1,borderColor:selected.size?color.accent:color.line,backgroundColor:selected.size?color.accent:color.surface,opacity:pressed?0.65:1}]}><Text style={{color:selected.size?color.buttonInk:color.muted,fontWeight:'600'}}>{submitting?'Подготовка…':`Продолжить · ${selected.size}`}</Text></Pressable>
    </View>
  </View>;
}

const styles=StyleSheet.create({
  fill:{flex:1,minHeight:0},header:{flexDirection:'row',alignItems:'center',gap:8,paddingHorizontal:16,paddingVertical:12},
  icon:{minWidth:48,minHeight:48,borderWidth:1,borderRadius:5,alignItems:'center',justifyContent:'center'},title:{fontSize:24,fontWeight:'600',flex:1,minWidth:0},
  album:{paddingHorizontal:16,minHeight:54,flexDirection:'row',alignItems:'center',justifyContent:'space-between',borderBottomWidth:StyleSheet.hairlineWidth},
  notice:{paddingHorizontal:16,paddingVertical:12},link:{minHeight:44,justifyContent:'center'},
  footer:{flexDirection:'row',gap:8,padding:16,borderTopWidth:1},clear:{minWidth:80,minHeight:48,borderWidth:1,borderRadius:6,alignItems:'center',justifyContent:'center'},
  button:{minHeight:48,alignItems:'center',justifyContent:'center',borderRadius:5},
});
