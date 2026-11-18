import React, {useEffect, useMemo, useRef, useState} from 'react';
import {
  ActivityIndicator, Alert, AppState, BackHandler, FlatList, Image, Linking,
  PanResponder, PermissionsAndroid, Platform, Pressable, ScrollView, StatusBar,
  StyleSheet, Text, TextInput, useColorScheme, View, requireNativeComponent,
  type ViewProps,
} from 'react-native';
import {SafeAreaProvider, useSafeAreaInsets} from 'react-native-safe-area-context';
import {storage} from '../composition';
import {DeviceMediaPicker} from './DeviceMediaPicker';
import {ActionSheet, type ActionSheetModel} from './ActionSheet';
import {GridControls, MediaGrid, type MediaGridItem, type GridAnchor} from './MediaGrid';
import type {Collection, DeviceFile, Profile, Session, StoredFile, Theme, Transfer} from '../domain/models';

type Screen='gallery'|'files'|'queue'|'settings'|'trash'|'picker'|'device'|'viewer';
const Video=requireNativeComponent<ViewProps & {source:{uri:string;headers:Record<string,string>}}>('StorageVideo');
const bytes=(value:number)=>value>=1024**3?(value/1024**3).toFixed(1)+' ГБ':value>=1024**2?(value/1024**2).toFixed(1)+' МБ':Math.round(value/1024)+' КБ';
const dateLabel=(value:string)=>new Date(value+'T12:00:00').toLocaleDateString('ru-RU',{day:'numeric',month:'long',year:'numeric'});
const stateLabel:Record<string,string>={queued:'В очереди',preparing:'Подготовка',uploading:'Передача',verifying:'Проверяем копию',done:'Готово',waiting_network:'Ожидаем соединения',waiting_auth:'Войдите повторно',access_revoked:'Доступ отозван',needs_source:'Нет доступа к исходнику',awaiting_foreground:'Откройте приложение для завершения',awaiting_permission:'Нужно разрешение удаления',removing_server:'Убираем серверную копию',deleting:'Удаляем оригинал',kept_local:'Оригинал оставлен',paused:'Пауза',cancelled:'Отменено',failed:'Ошибка'};
const finished=new Set(['done','kept_local','cancelled']);

export default function App(){return <SafeAreaProvider><StorageApp/></SafeAreaProvider>;}
function StorageApp(){
  const insets=useSafeAreaInsets(),system=useColorScheme();
  const [theme,setTheme]=useState<Theme>('system'),[columns,setColumns]=useState(3);
  const dark=theme==='dark'||theme==='system'&&system==='dark';
  const color=useMemo(()=>dark?{bg:'#171717',surface:'#202020',ink:'#F2F2F2',muted:'#A5A5A5',line:'#363636',accent:'#FF9138',buttonInk:'#171717'}:{bg:'#FFFFFF',surface:'#F5F5F5',ink:'#202020',muted:'#777777',line:'#E3E3E3',accent:'#CE3036',buttonInk:'#FFFFFF'},[dark]);
  const [session,setSession]=useState<Session|null>(null),[booting,setBooting]=useState(true),[screen,setScreen]=useState<Screen>('gallery');
  const [baseUrl,setBaseUrl]=useState(''),[loginCode,setLoginCode]=useState(''),[attempt,setAttempt]=useState(false),[denied,setDenied]=useState(false),[requestStatus,setRequestStatus]=useState('not_requested');
  const [profile,setProfile]=useState<Profile|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(false),[catalogDirty,setCatalogDirty]=useState(false);
  const [media,setMedia]=useState<StoredFile[]>([]),[documents,setDocuments]=useState<StoredFile[]>([]),[trash,setTrash]=useState<StoredFile[]>([]);
  const [queries,setQueries]=useState({media:'',files:''}),[dates,setDates]=useState({media:'',files:''}),[kind,setKind]=useState('all');
  const [cursor,setCursor]=useState<string|null>(null),[revision,setRevision]=useState(0),[transfers,setTransfers]=useState<Transfer[]>([]);
  const [picked,setPicked]=useState<DeviceFile[]>([]),[selection,setSelection]=useState<Set<string>>(new Set()),[mode,setMode]=useState<'copy'|'move'>('copy');
  const [viewer,setViewer]=useState(0),[viewerControls,setViewerControls]=useState(true),[zoom,setZoom]=useState(1),[pan,setPan]=useState({x:0,y:0});
  const [serverSelected,setServerSelected]=useState<Map<string,StoredFile>>(new Map()),[serverSelecting,setServerSelecting]=useState(false),[bulkBusy,setBulkBusy]=useState(false),[pendingShare,setPendingShare]=useState<string|null>(null);
  const [sheet,setSheet]=useState<ActionSheetModel|null>(null);
  const list=useRef<FlatList<any>>(null),positions=useRef<Record<string,number>>({}),lastScreen=useRef<Screen>('gallery'),catalogKey=useRef(''),completed=useRef<string|null>(null),requestGeneration=useRef(0),polling=useRef(false);
  const pickerOrigin=useRef<Screen>('gallery');
  const galleryAnchor=useRef<GridAnchor|undefined>(undefined);
  const currentSession=useRef(session);currentSession.current=session;
  const collection:Collection=screen==='files'?'files':'media';
  const active=media[viewer];
  const notify=(e:unknown)=>Alert.alert('storage',e instanceof Error?e.message:'Не удалось выполнить действие');
  const safe=(action:()=>Promise<unknown>)=>{action().catch(notify);};
  const go=(next:Screen)=>{if(next!=='gallery'){setServerSelected(new Map());setServerSelecting(false);}if(next==='settings')lastScreen.current=screen;setScreen(next);setSheet(null);};

  useEffect(()=>{(async()=>{const prefs=await storage.device.preferences();setTheme(prefs.theme as Theme);setColumns(Math.max(2,Math.min(6,prefs.columns)));setBaseUrl(prefs.baseUrl);const restored=await storage.restoreSession();setSession(restored);})().catch(notify).finally(()=>setBooting(false));},[]);
  useEffect(()=>{
    requestGeneration.current++;catalogKey.current='';completed.current=null;positions.current={};galleryAnchor.current=undefined;
    setMedia([]);setDocuments([]);setTrash([]);setTransfers([]);setProfile(null);
    setPicked([]);setSelection(new Set());setCursor(null);setSheet(null);setError('');
    setScreen('gallery');setViewer(0);setLoading(false);setCatalogDirty(false);setServerSelected(new Map());setServerSelecting(false);setBulkBusy(false);setPendingShare(null);
  },[session?.localId]);
  useEffect(()=>{
    if(!session)return;
    let live=true;
    storage.profile().then(result=>{if(live)setProfile(result);}).catch((e:unknown)=>{
      if(!live)return;
      const code=(e as {code?:string}).code||'';
      if(code.includes('SESSION')||code==='AUTH_REQUIRED'||code==='ACCESS_REVOKED'){
        setSession(null);storage.logout().catch(()=>{});
      }else setError(e instanceof Error?e.message:'Сервер недоступен');
    });
    return()=>{live=false;};
  },[session,revision]);
  useEffect(()=>{
    if(!attempt||session)return;
    let live=true;
    const timer=setInterval(async()=>{if(polling.current||AppState.currentState!=='active')return;polling.current=true;
      try{const result=await storage.loginResult();if(!live)return;if(result.session){storage.api.setSession(result.session);setSession(result.session);setAttempt(false);setDenied(false);catalogKey.current='';}else if(result.state==='denied'){setDenied(true);setRequestStatus(result.access_request_status||'not_requested');setAttempt(false);}}
      catch(e){if(live){setError(e instanceof Error?e.message:'Ошибка входа');setAttempt(false);}}finally{polling.current=false;}},2000);
    return()=>{live=false;clearInterval(timer);};
  },[attempt,session]);
  useEffect(()=>{
    if(!session)return;
    let live=true,busy=false;
    const refresh=async()=>{
      if(busy||AppState.currentState!=='active')return;
      busy=true;
      try{
        const rows=await storage.device.transfers();if(!live)return;
        // Progress must not re-render the gallery or restart the video player.
        if(screen==='queue')setTransfers(previous=>JSON.stringify(previous)===JSON.stringify(rows)?previous:rows);
        const doneRows=rows.filter(r=>r.state==='done'||r.state==='kept_local');const done=doneRows.map(r=>r.id);
        const previous=completed.current===null?null:new Set(completed.current.split(','));
        if(previous&&doneRows.some(row=>!previous.has(row.id)&&(row.direction==='upload'||row.server_removed)))setCatalogDirty(true);
        completed.current=done.join(',');
      }catch{}finally{busy=false;}
    };
    refresh();const timer=setInterval(refresh,1500);
    const listener=AppState.addEventListener('change',state=>{if(state==='active')void refresh();});
    return()=>{live=false;clearInterval(timer);listener.remove();};
  },[session,screen]);
  const load=async(more=false)=>{
    if(!session||!['gallery','files','trash'].includes(screen))return;
    const id=++requestGeneration.current;setLoading(true);setError('');
    try {
      const result=screen==='trash'?await storage.trashCatalog(more?cursor||'':''):await storage.catalog(collection,queries[collection],dates[collection],more?cursor||'':'');
      if(id!==requestGeneration.current)return;
      if(screen==='gallery')setMedia(old=>more?[...old,...result.items]:result.items);
      else if(screen==='files')setDocuments(old=>more?[...old,...result.items]:result.items);
      else setTrash(old=>more?[...old,...result.items]:result.items);
      setCursor(result.next_cursor);if(!more)setCatalogDirty(false);
    }catch(e){if(id===requestGeneration.current)setError(e instanceof Error?e.message:'Сервер недоступен');}finally{if(id===requestGeneration.current)setLoading(false);}
  };
  useEffect(()=>{
    if(!session||!['gallery','files','trash'].includes(screen))return;
    const key=JSON.stringify([screen,queries[collection],dates[collection],revision]);
    if(catalogKey.current===key)return;
    catalogKey.current=key;const timer=setTimeout(()=>{load();},250);return()=>clearTimeout(timer);
  },[session,screen,queries,dates,revision]);
  useEffect(()=>{storage.device.immersive(screen==='viewer');if(screen==='viewer'){setZoom(1);setPan({x:0,y:0});setViewerControls(true);}return()=>storage.device.immersive(false);},[screen]);
  useEffect(()=>{const event=BackHandler.addEventListener('hardwareBackPress',()=>{if(sheet){setSheet(null);return true;}if(screen==='gallery'&&serverSelecting){setServerSelected(new Map());setServerSelecting(false);return true;}if(screen==='viewer'){setScreen('gallery');return true;}if(screen==='settings'){setScreen(lastScreen.current);return true;}if(screen==='device'||screen==='picker'){setScreen(pickerOrigin.current);return true;}if(!['gallery','files','queue'].includes(screen)){setScreen('gallery');return true;}return false;});return()=>event.remove();},[screen,sheet,serverSelecting]);

  const chooseTheme=(value:Theme)=>{setTheme(value);storage.device.preference('theme',value);setSheet(null);};
  const changeColumns=(value:number)=>{const next=Math.max(2,Math.min(6,value));if(next===columns)return;setColumns(next);storage.device.preference('columns',String(next));};
  const chooseDate=()=>safe(async()=>{const result=await storage.dates(collection);setSheet({title:'По дате загрузки',items:[{label:'Все даты',action:()=>{setDates(old=>({...old,[collection]:''}));setSheet(null);}},...result.items.map(row=>({label:`${dateLabel(row.storage_date)} · ${row.file_count}`,action:()=>{setDates(old=>({...old,[collection]:row.storage_date}));setSheet(null);}}))]});});
  const acceptPicked=(chosen:DeviceFile[])=>{if(chosen.length){setPicked(chosen);setSelection(new Set(chosen.map(f=>f.uri)));setMode('copy');go('picker');}};
  const pick=()=>{pickerOrigin.current=screen==='files'?'files':'gallery';if(screen==='gallery'){go('device');return;}safe(async()=>acceptPicked(await storage.device.pickFiles()));};
  const ensureMedia=async()=>{
    if(await storage.device.canManageMedia())return;
    const permissions=Number(Platform.Version)>=34?[PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES,PermissionsAndroid.PERMISSIONS.READ_MEDIA_VIDEO,PermissionsAndroid.PERMISSIONS.READ_MEDIA_VISUAL_USER_SELECTED]:Number(Platform.Version)>=33?[PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES,PermissionsAndroid.PERMISSIONS.READ_MEDIA_VIDEO]:[PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE];
    const granted=await Promise.all(permissions.map(permission=>PermissionsAndroid.check(permission)));
    if(!granted.some(Boolean))await PermissionsAndroid.requestMultiple(permissions);
    await storage.device.requestManageMedia();
  };
  const enqueue=()=>{
    const chosen=picked.filter(f=>selection.has(f.uri));if(!chosen.length)return;
    const moving=mode==='move';
    Alert.alert(moving?'Перенести файлы?':'Скопировать файлы?',`Вы уверены, что хотите ${moving?'перенести':'скопировать'} выбранные файлы (${chosen.length}) на сервер?\n\nКаталог: ${profile?.archive_date.replaceAll('-',' / ')||'по дате сервера'}\n\n${moving?'После проверки копий оригиналы удалятся с устройства. Если постоянное разрешение не выдано, Android запросит подтверждение удаления.':'Оригиналы останутся на устройстве.'}`,[{text:'Отмена',style:'cancel'},{text:moving?'Да, перенести':'Да, скопировать',onPress:()=>safe(async()=>{if(Number(Platform.Version)>=33)await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS);if(moving)await ensureMedia();if(currentSession.current?.localId!==session?.localId)return;await storage.upload(chosen,mode);go('queue');})}]);
  };
  const cancelAll=()=>{
    if(!session)return;
    const current=session;
    const message='Остановить все незавершённые передачи? Готовые серверные копии сохранятся.'+(transfers.some(t=>t.state==='deleting')?' Если системный запрос удаления ещё открыт, нажмите в нём «Отмена».':'');
    Alert.alert('Отменить все передачи?',message,[{text:'Назад',style:'cancel'},{text:'Отменить все',style:'destructive',onPress:()=>safe(async()=>{
      await storage.device.cancelAllTransfers(current.localId);
      const rows=await storage.device.transfers();if(currentSession.current?.localId===current.localId)setTransfers(rows);
    })}]);
  };
  const clearServerSelection=()=>{setServerSelected(new Map());setServerSelecting(false);};
  const ensureNotifications=async()=>{if(Number(Platform.Version)>=33)await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS);};
  const confirmDownload=(files:StoredFile[],operation:'copy'|'move')=>{
    if(!session||!files.length||bulkBusy)return;
    const current=session;
    const move=operation==='move';
    Alert.alert(move?'Вернуть файлы на телефон?':'Скопировать файлы на устройство?',`${files.length} файлов · ${bytes(files.reduce((sum,file)=>sum+file.size_bytes,0))}\n\n${move?'После скачивания и проверки копий серверные оригиналы попадут в корзину на 30 дней.':'Серверные оригиналы сохранятся.'}`,[{text:'Отмена',style:'cancel'},{text:move?'Вернуть':'Копировать',onPress:()=>safe(async()=>{
      setBulkBusy(true);
      try{await ensureNotifications();if(currentSession.current?.localId!==current.localId)return;await storage.device.downloadFiles(files,operation,current.localId);if(currentSession.current?.localId===current.localId){clearServerSelection();go('queue');}}
      finally{if(currentSession.current?.localId===current.localId)setBulkBusy(false);}
    })}]);
  };
  const download=(file:StoredFile)=>confirmDownload([file],'copy');
  const share=(files:StoredFile[])=>safe(async()=>{
    if(!session||bulkBusy||!files.length)return;
    if(files.length>100){Alert.alert('Поделиться','Выберите не больше 100 файлов для одной отправки.');return;}
    const current=session;setBulkBusy(true);
    try{await ensureNotifications();if(currentSession.current?.localId!==current.localId)return;
      const result=await storage.device.shareFiles(files,current.localId);
      if(currentSession.current?.localId===current.localId){setPendingShare(result.batch_id);clearServerSelection();go('queue');}
    }finally{if(currentSession.current?.localId===current.localId)setBulkBusy(false);}
  });
  const trashSelected=(files:StoredFile[])=>{
    if(!session||bulkBusy||!files.length)return;
    const current=session;
    Alert.alert('Убрать с сервера?',`${files.length} файлов попадут в корзину на 30 дней. Копии на устройстве сохранятся.`,[{text:'Отмена',style:'cancel'},{text:'В корзину',style:'destructive',onPress:()=>safe(async()=>{
      setBulkBusy(true);const removed=new Set<string>();let failures=0;
      try{for(const file of files){if(currentSession.current?.localId!==current.localId)return;try{await storage.trash(file);removed.add(file.id);}catch{failures++;}}
        if(currentSession.current?.localId!==current.localId)return;
        setMedia(old=>old.filter(file=>!removed.has(file.id)));setDocuments(old=>old.filter(file=>!removed.has(file.id)));clearServerSelection();catalogKey.current='';setRevision(value=>value+1);
        if(failures)Alert.alert('Корзина',`Перемещено ${removed.size} из ${files.length}. Остальные файлы сохранены на сервере.`);
      }finally{if(currentSession.current?.localId===current.localId)setBulkBusy(false);}
    })}]);
  };
  const showSelectionActions=()=>{
    const files=[...serverSelected.values()];if(!files.length||bulkBusy)return;
    setSheet({title:`Выбрано ${files.length} · ${bytes(files.reduce((sum,file)=>sum+file.size_bytes,0))}`,items:[
      {label:'Копировать на устройство',action:()=>confirmDownload(files,'copy')},
      {label:'Вернуть на телефон',action:()=>confirmDownload(files,'move')},
      {label:'Убрать с сервера · в корзину',action:()=>trashSelected(files)},
      {label:'Поделиться файлами',action:()=>share(files)},
    ]});
  };
  const updateServerSelection=(ids:string[])=>{
    if(bulkBusy)return;
    if(ids.length)setServerSelecting(true);
    setServerSelected(previous=>{const available=new Map([...previous,...media.map(file=>[file.id,file] as const)]);return new Map(ids.flatMap(id=>{const file=available.get(id);return file?[[id,file] as const]:[];}));});
  };
  const serverSelectedIds=useMemo(()=>[...serverSelected.keys()],[serverSelected]);
  const shareGroups=useMemo(()=>{
    const groups=new Map<string,Transfer[]>();
    for(const transfer of transfers)if(transfer.purpose==='share'&&transfer.share_batch){const rows=groups.get(transfer.share_batch)||[];rows.push(transfer);groups.set(transfer.share_batch,rows);}
    return [...groups].map(([id,rows])=>({id,rows,ready:rows.every(row=>row.state==='done')})).filter(group=>!group.rows.every(row=>row.share_opened)&&Math.max(...group.rows.map(row=>row.share_expires_at||0))>Date.now());
  },[transfers]);
  useEffect(()=>{
    if(!pendingShare||!session||screen!=='queue'||AppState.currentState!=='active')return;
    if(!shareGroups.some(group=>group.id===pendingShare&&group.ready))return;
    const current=session;const batch=pendingShare;setPendingShare(null);
    storage.device.openShareBatch(batch,current.localId).catch(notify);
  },[pendingShare,shareGroups,session,screen]);
  const trashFile=(file:StoredFile)=>Alert.alert('В корзину на 30 дней?',`${file.original_name}\nКопия на устройстве останется.`,[{text:'Отмена',style:'cancel'},{text:'В корзину',style:'destructive',onPress:()=>safe(async()=>{await storage.trash(file);setMedia(old=>old.filter(f=>f.id!==file.id));setDocuments(old=>old.filter(f=>f.id!==file.id));catalogKey.current='';go(file.media_kind==='photo'||file.media_kind==='video'?'gallery':'files');setRevision(v=>v+1);})}]);
  const showInfo=(file:StoredFile)=>setSheet({title:file.original_name,items:[{label:`${bytes(file.size_bytes)} · ${file.archive_path}`},{label:'Копировать на устройство',action:()=>download(file)},{label:'Вернуть на телефон',action:()=>confirmDownload([file],'move')},{label:'Поделиться файлом',action:()=>share([file])},{label:'Проверить серверную копию',action:()=>safe(async()=>{const result=await storage.verify(file);Alert.alert('Проверка',result);})},{label:'Переместить в корзину',action:()=>{setSheet(null);trashFile(file);}}]});
  const next=(direction:number)=>{if(viewer+direction>=0&&viewer+direction<media.length){setViewer(viewer+direction);setZoom(1);setPan({x:0,y:0});}else if(direction>0&&cursor&&!loading){load(true);} };
  const gesture=useRef({x:0,y:0,zoom:1,pan:{x:0,y:0},distance:0,lastTap:0,pinched:false});
  const distance=(touches:readonly {pageX:number;pageY:number}[])=>{const [first,second]=touches;return first&&second?Math.hypot(first.pageX-second.pageX,first.pageY-second.pageY):0;};
  const viewerResponder=PanResponder.create({
    onStartShouldSetPanResponder:()=>active?.media_kind!=='video',
    onMoveShouldSetPanResponder:(_,g)=>active?.media_kind!=='video'&&Math.abs(g.dx)+Math.abs(g.dy)>5,
    onPanResponderGrant:()=>{gesture.current={...gesture.current,x:0,y:0,zoom,pan,distance:0,pinched:false};},
    onPanResponderMove:(event,g)=>{const t=event.nativeEvent.touches;if(t.length>=2){gesture.current.pinched=true;if(!gesture.current.distance)gesture.current.distance=distance(t);setZoom(Math.max(1,Math.min(5,gesture.current.zoom*distance(t)/gesture.current.distance)));}else if(zoom>1)setPan({x:gesture.current.pan.x+g.dx,y:gesture.current.pan.y+g.dy});},
    onPanResponderRelease:(_,g)=>{if(!gesture.current.pinched&&zoom===1&&Math.abs(g.dx)>60&&Math.abs(g.dx)>Math.abs(g.dy)){next(g.dx<0?1:-1);return;}if(Math.abs(g.dx)+Math.abs(g.dy)<10&&!gesture.current.pinched){if(Date.now()-gesture.current.lastTap<300){setZoom(zoom>1?1:2.5);setPan({x:0,y:0});gesture.current.lastTap=0;}else{setViewerControls(v=>!v);gesture.current.lastTap=Date.now();}}},
  });
  const ink={color:color.ink};
  const button=(label:string,onPress:()=>void,secondary=false)=><Pressable accessibilityRole="button" onPress={onPress} style={({pressed})=>[styles.button,{backgroundColor:secondary?color.surface:color.accent,borderWidth:1,borderColor:secondary?color.line:color.accent,opacity:pressed?0.65:1}]}><Text style={{color:secondary?color.ink:color.buttonInk,fontWeight:'600',fontSize:14}}>{label}</Text></Pressable>;
  const row=(label:string,value:string,onPress?:()=>void)=>{
    const content=<View style={{flex:1}}><Text style={[styles.text,ink]}>{label}</Text><Text style={[styles.small,{color:color.muted,marginTop:5}]}>{value}</Text></View>;
    if(!onPress)return <View style={[styles.row,{borderColor:color.line}]}>{content}</View>;
    return <Pressable accessibilityRole="button" onPress={onPress} style={({pressed})=>[styles.row,{borderColor:color.line,backgroundColor:color.surface,borderWidth:1,borderRadius:5,paddingHorizontal:12,marginVertical:5,opacity:pressed?0.65:1}]}>{content}<Text style={[ink,{fontSize:22}]}>›</Text></Pressable>;
  };
  const iconButton=[styles.iconButton,{backgroundColor:color.surface,borderColor:color.line}];
  const viewerIconButton=[styles.iconButton,{backgroundColor:'#242424',borderColor:'#555'}];
  const heading=(title:string,back?:()=>void,extra?:React.ReactNode)=><View style={styles.header}>{back&&<Pressable onPress={back} accessibilityLabel="Назад" style={iconButton}><Text style={[styles.icon,ink]}>‹</Text></Pressable>}<Text numberOfLines={1} style={[styles.title,ink]}>{title}</Text>{extra}{(['gallery','files','queue'].includes(screen)&&!(screen==='gallery'&&serverSelecting))&&<Pressable onPress={()=>go('settings')} accessibilityLabel="Настройки" style={iconButton}><Text style={[styles.icon,ink]}>⚙︎</Text></Pressable>}</View>;
  const input=(value:string,onChangeText:(text:string)=>void,placeholder:string)=><TextInput style={[styles.input,{color:color.ink,borderColor:color.line,backgroundColor:color.surface}]} value={value} onChangeText={onChangeText} placeholder={placeholder} placeholderTextColor={color.muted} autoCapitalize="none"/>;
  const documentRow=(file:StoredFile)=><Pressable key={file.id} style={[styles.row,{borderColor:color.line}]} onPress={()=>showInfo(file)}><Text style={[styles.icon,{color:color.muted,marginRight:15}]}>{file.media_kind==='audio'?'♪':'▤'}</Text><View style={{flex:1}}><Text numberOfLines={1} style={[styles.text,ink]}>{file.original_name}</Text><Text style={[styles.small,{color:color.muted,marginTop:5}]}>{bytes(file.size_bytes)} · {dateLabel(file.storage_date)}</Text></View></Pressable>;

  const gridItems=useMemo(()=>{
    const items:MediaGridItem[]=[];let currentDate='';
    for(const file of media){
      if(kind!=='all'&&file.media_kind!==kind)continue;
      if(file.storage_date!==currentDate){currentDate=file.storage_date;items.push({id:'date:'+currentDate,label:dateLabel(currentDate),heading:true});}
      items.push({id:file.id,label:file.original_name,uri:storage.api.mediaSource(file,true).uri,video:file.media_kind==='video'});
    }
    return items;
  },[media,kind,session]);
  const rows=useMemo(()=>{
    const items:({type:'date';id:string;date:string}|{type:'file';id:string;file:StoredFile})[]=[];let date='';
    for(const file of documents){if(file.storage_date!==date){date=file.storage_date;items.push({type:'date',id:'date:'+date,date});}items.push({type:'file',id:file.id,file});}
    return items;
  },[documents]);
  const initialOffset=useMemo(()=>({x:0,y:positions.current[screen]||0}),[screen]);

  if(booting)return <View style={[styles.fill,{backgroundColor:color.bg,justifyContent:'center'}]}><ActivityIndicator color={color.accent}/></View>;
  if(!session)return <View style={[styles.fill,{backgroundColor:color.bg,paddingTop:insets.top,paddingBottom:insets.bottom}]}><StatusBar barStyle={dark?'light-content':'dark-content'}/>{heading('storage')}<ScrollView contentContainerStyle={styles.content}><Text style={[styles.loginTitle,ink]}>{denied?'Доступ пока\nне открыт':'Вход\nчерез Telegram.'}</Text><Text style={[styles.text,{color:color.muted,lineHeight:24}]}>{denied?'Аккаунт подтверждён в боте. Доступ открывает администратор.':'Фото, видео и файлы на вашем сервере.'}</Text>{input(baseUrl,setBaseUrl,'https://server.example.com')}{loginCode&&attempt?<View style={[styles.info,{backgroundColor:color.surface}]}><Text style={[styles.text,ink]}>Код для сверки в боте</Text><Text selectable style={[styles.code,ink]}>{loginCode}</Text><Text style={{color:color.muted}}>Подтвердите вход в боте и вернитесь в storage.</Text></View>:null}{denied&&requestStatus!=='not_requested'?<Text style={[styles.text,{color:color.muted,marginVertical:20}]}>Запрос: {requestStatus==='pending'?'ожидает решения':requestStatus==='rejected'?'отклонён':'одобрен'}</Text>:null}{error?<Text style={styles.error}>{error}</Text>:null}</ScrollView><View style={styles.actions}>{denied&&requestStatus==='not_requested'?button('Запросить доступ у админа',()=>safe(async()=>{const result=await storage.device.requestAccess();setRequestStatus(result.status);})):null}{button(attempt?'Открыть Telegram':'Войти через Telegram',()=>safe(async()=>{setError('');setDenied(false);const result=await storage.device.beginLogin(baseUrl);setLoginCode(result.login_code);setAttempt(true);await Linking.openURL(result.authorization_url);}))}</View></View>;

  let body:React.ReactNode;
  if(screen==='device'){
    body=<DeviceMediaPicker sessionId={session.localId} color={color} columns={columns} onColumnsChange={changeColumns} onBack={()=>go(pickerOrigin.current)} onSelected={acceptPicked}/>;
  }else if(screen==='viewer'&&active){
    body=<View style={[styles.fill,{backgroundColor:'#050505'}]}><StatusBar hidden/><View style={[styles.viewerImage]} {...viewerResponder.panHandlers}>{active.media_kind==='video'?<Video source={storage.api.mediaSource(active)} style={styles.fill}/>:<Image source={storage.api.mediaSource(active)} resizeMode="contain" style={[styles.fill,{transform:[{translateX:pan.x},{translateY:pan.y},{scale:zoom}]}]}/>}</View>{viewerControls?<><View style={[styles.viewerTop,{paddingTop:Math.max(12,insets.top)}]}><Pressable onPress={()=>go('gallery')} style={viewerIconButton}><Text style={[styles.icon,{color:'#fff'}]}>‹</Text></Pressable><Text style={{color:'#fff'}}>{viewer+1} / {media.length}</Text><Pressable onPress={()=>showInfo(active)} style={viewerIconButton}><Text style={{color:'#fff',fontSize:24}}>ⓘ</Text></Pressable></View><View style={[styles.viewerBottom,{paddingBottom:Math.max(15,insets.bottom)}]}><Text style={{color:'#fff',fontSize:14}}>{active.original_name}</Text><View style={[styles.toolbar,{justifyContent:'space-between',marginTop:18}]}><Pressable onPress={()=>next(-1)} style={viewerIconButton}><Text style={{color:'#fff',fontSize:26}}>‹</Text></Pressable><Pressable onPress={()=>download(active)} style={viewerIconButton}><Text style={{color:'#fff',fontSize:24}}>↓</Text></Pressable><Pressable onPress={()=>trashFile(active)} style={viewerIconButton}><Text style={{color:'#fff',fontSize:24}}>⌫</Text></Pressable><Pressable onPress={()=>next(1)} style={viewerIconButton}><Text style={{color:'#fff',fontSize:26}}>›</Text></Pressable></View></View></>:null}</View>;
  }else if(screen==='picker'){
    const chosen=picked.filter(file=>selection.has(file.uri));
    body=<>{heading('Загрузка',()=>go(pickerOrigin.current))}
      <FlatList data={picked} extraData={selection} keyExtractor={file=>file.uri} contentContainerStyle={styles.content}
        renderItem={({item:file})=><Pressable accessibilityRole="checkbox" accessibilityState={{checked:selection.has(file.uri)}} onPress={()=>setSelection(old=>{const next=new Set(old);next.has(file.uri)?next.delete(file.uri):next.add(file.uri);return next;})} style={({pressed})=>[styles.row,{borderColor:color.line,backgroundColor:pressed?color.surface:color.bg}]}><Text style={[styles.text,{color:selection.has(file.uri)?color.accent:color.muted,marginRight:12}]}>{selection.has(file.uri)?'☑':'☐'}</Text><Text numberOfLines={1} style={[styles.text,ink,{flex:1}]}>{file.name}</Text></Pressable>}/>
      <View style={[styles.actions,{backgroundColor:color.surface,borderTopWidth:1,borderColor:color.line}]}>
        <Text style={[styles.text,ink,{fontWeight:'600',marginVertical:6}]}>Выбрано {selection.size} · {bytes(chosen.reduce((sum,file)=>sum+file.size,0))}</Text>
        <Text style={[styles.small,{color:color.muted,marginBottom:8}]}>Каталог на сервере: {profile?.archive_date.replaceAll('-',' / ')}</Text>
        <View accessibilityRole="radiogroup" style={styles.toolbar}>{(['copy','move'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{checked:mode===value}} onPress={()=>setMode(value)} style={({pressed})=>[styles.button,{flex:1,borderWidth:1,borderColor:mode===value?color.accent:color.line,backgroundColor:mode===value?color.accent:color.bg,opacity:pressed?0.65:1}]}><Text style={{color:mode===value?color.buttonInk:color.ink,fontWeight:'600'}}>{mode===value?'● ':'○ '}{value==='copy'?'Копировать':'Перенести'}</Text></Pressable>)}</View>
        <Text style={[styles.small,{color:color.muted,lineHeight:18,marginVertical:6}]}>{mode==='copy'?'Оригиналы останутся на устройстве.':'После проверки серверных копий Android запросит удаление оригиналов, если нет постоянного разрешения.'}</Text>
        {selection.size?button('Подтвердить '+(mode==='copy'?'копирование':'перенос'),enqueue):<View style={[styles.button,{backgroundColor:color.bg,borderWidth:1,borderColor:color.line}]}><Text style={{color:color.muted}}>Выберите файлы</Text></View>}
      </View>
    </>;
  }else if(screen==='settings'){
    body=<>{heading('Настройки',()=>go(lastScreen.current))}<ScrollView contentContainerStyle={styles.content}><Text style={[styles.text,ink]}>{profile?.name||'Telegram'}</Text>{row('Сервер',session.baseUrl)}{row('Корзина','Восстановление в течение 30 дней',()=>go('trash'))}{row('Тема приложения',{system:'Как в системе',light:'Светлая',dark:'Тёмная'}[theme],()=>setSheet({title:'Тема приложения',items:([{label:'Как в системе',action:()=>chooseTheme('system')},{label:'Светлая',action:()=>chooseTheme('light')},{label:'Тёмная',action:()=>chooseTheme('dark')}])}))}{row('Управление медиа','Для автоматического удаления после переноса',()=>safe(ensureMedia))}{row('Активные сессии','Ваши устройства',()=>safe(async()=>{const result=await storage.sessions();setSheet({title:'Сессии',items:result.items.map(item=>({label:item.device_name+(item.is_current?' · эта сессия':' · завершить'),action:()=>safe(async()=>{await storage.revokeSession(item.id);setSheet(null);if(item.is_current){await storage.device.logout();setSession(null);}})}))});}))}{row('Выйти','Остановить передачи этого аккаунта',()=>Alert.alert('Выйти?','Файлы сервера и оригиналы сохранятся.',[{text:'Отмена',style:'cancel'},{text:'Выйти',onPress:()=>safe(async()=>{setSession(null);setMedia([]);setDocuments([]);setTrash([]);setTransfers([]);setProfile(null);catalogKey.current='';await storage.logout();})}]))}</ScrollView></>;
  }else if(screen==='queue'){
    body=<>{heading('Передача')}{shareGroups.map(group=><View key={group.id} style={styles.actions}>{group.ready?button('Поделиться · '+group.rows.length,()=>safe(async()=>{if(session){await storage.device.openShareBatch(group.id,session.localId);const rows=await storage.device.transfers();if(currentSession.current?.localId===session.localId)setTransfers(rows);}})): <Text style={{color:color.muted}}>Подготовка отправки · {group.rows.filter(row=>row.state==='done').length} / {group.rows.length}</Text>}</View>)}{transfers.some(t=>!finished.has(t.state))?<View style={styles.actions}>{button('Отменить все',cancelAll,true)}</View>:null}<Text style={{color:color.muted,paddingHorizontal:16,paddingBottom:8}}>Завершённые и отменённые — за последние 7 дней</Text><FlatList data={transfers} keyExtractor={item=>item.id} contentContainerStyle={styles.content} ListEmptyComponent={<Text style={{color:color.muted}}>Выберите файлы, чтобы начать передачу.</Text>} renderItem={({item})=><View style={[styles.queueItem,{borderColor:color.line}]}><Text style={[styles.text,ink]}>{item.name}</Text><Text style={[styles.small,{color:color.muted,marginVertical:8}]}>{item.purpose==='share'?'Подготовка отправки':item.direction==='download'?item.mode==='move'?'Возврат на телефон':'Копирование на устройство':item.mode==='move'?'Перенос':'Копирование'} · {bytes(item.size)}</Text><View style={{height:3,backgroundColor:color.line}}><View style={{height:3,width:`${Math.max(0,Math.min(100,item.size?item.progress/item.size*100:0))}%`,backgroundColor:color.accent}}/></View><Text style={{color:color.accent,marginTop:10}}>{stateLabel[item.state]||item.state}</Text>{item.error?<Text style={styles.error}>{item.error}</Text>:null}{!finished.has(item.state)&&item.state!=='deleting'?<View style={styles.toolbar}>{button(item.state==='awaiting_permission'?'Разрешить удаление':item.state==='awaiting_foreground'?'Завершить перенос':item.state==='paused'||item.state==='failed'?'Продолжить':'Пауза',()=>safe(async()=>{if(item.state==='awaiting_permission')await ensureMedia();await storage.device.action(item.id,item.state==='paused'||item.state==='failed'||item.state.startsWith('awaiting')?'resume':'pause');}),true)}{button('Отмена',()=>safe(()=>storage.device.action(item.id,'cancel')),true)}</View>:null}</View>}/></>;
  }else if(screen==='trash'){
    body=<>{heading('Корзина',()=>go('settings'))}<FlatList data={trash} keyExtractor={item=>item.id} contentContainerStyle={styles.content} refreshing={loading} onRefresh={()=>load()} onEndReached={()=>{if(cursor&&!loading)load(true);}} ListHeaderComponent={<Text style={[styles.text,{color:color.muted,lineHeight:23,marginBottom:15}]}>Файлы удаляются окончательно через 30 дней. Восстановление вернёт файл в исходную дату.</Text>} renderItem={({item})=><View style={[styles.queueItem,{borderColor:color.line}]}><Text style={[styles.text,ink]}>{item.original_name}</Text><Text style={{color:color.muted,marginVertical:10}}>{bytes(item.size_bytes)}</Text>{button('Восстановить',()=>safe(async()=>{await storage.restore(item);setTrash(old=>old.filter(f=>f.id!==item.id));catalogKey.current='';}),true)}</View>}/></>;
  }else if(screen==='gallery'){
    body=<>{heading(serverSelecting?`Выбрано ${serverSelected.size}`:'Галерея',serverSelecting?clearServerSelection:undefined,serverSelecting?undefined:button('Выбрать',()=>setServerSelecting(true),true))}
      <View style={[styles.filters,{borderColor:color.line}]}>{(['all','photo','video'] as const).map(value=><Pressable key={value} accessibilityRole="button" accessibilityState={{selected:kind===value}} onPress={()=>setKind(value)} style={({pressed})=>[styles.filter,{flex:1,borderColor:kind===value?color.accent:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]}><Text numberOfLines={1} style={{color:kind===value?color.ink:color.muted,fontWeight:kind===value?'600':'400'}}>{{all:'Все',photo:'Фото',video:'Видео'}[value]}</Text></Pressable>)}</View>
      <Pressable accessibilityRole="button" style={({pressed})=>[styles.dateButton,{borderColor:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]} onPress={chooseDate}><Text numberOfLines={1} style={{color:color.ink,flex:1}}>{dates.media?dateLabel(dates.media):'Все даты'}</Text><Text style={{color:color.muted}}>⌄</Text></Pressable>
      <GridControls columns={columns} onChange={changeColumns} color={color}/>{catalogDirty?<Pressable accessibilityRole="button" onPress={()=>void load()} style={[styles.dateButton,{borderColor:color.accent,backgroundColor:color.surface}]}><Text style={{color:color.accent}}>Галерея изменилась · Обновить</Text></Pressable>:null}
      <MediaGrid items={gridItems} columns={columns} color={color} selectedIds={serverSelectedIds} onSelectionChange={updateServerSelection} selectionMode={serverSelecting} selectionLocked={bulkBusy} anchor={galleryAnchor.current} onPositionChange={value=>{galleryAnchor.current=value;}} catalogKey={kind+dates.media} onColumnsChange={changeColumns} hasMore={!!cursor} loading={loading}
        onLoadMore={()=>{if(cursor&&!loading)void load(true);}} onRefresh={()=>void load()}
        onOpen={id=>{const index=media.findIndex(file=>file.id===id);if(index>=0){setViewer(index);go('viewer');}}}/>
      <View style={[styles.actions,{borderTopWidth:1,borderColor:color.line}]}>{serverSelecting?<View style={styles.selectionActions}>{button('Снять',clearServerSelection,true)}<View style={{flex:1}}>{serverSelected.size&&!bulkBusy?button('Действия · '+serverSelected.size,showSelectionActions):<View style={[styles.button,{backgroundColor:color.surface,borderWidth:1,borderColor:color.line}]}><Text style={{color:color.muted}}>{bulkBusy?'Обработка…':'Выберите файлы'}</Text></View>}</View></View>:button('＋  Загрузить с устройства',pick)}</View>
    </>;
  }else{
    body=<>{heading('Файлы')}{input(queries.files,value=>setQueries(old=>({...old,files:value})),'Найти документ или аудио')}
      <Pressable accessibilityRole="button" style={({pressed})=>[styles.dateButton,{borderColor:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]} onPress={chooseDate}><Text style={{color:color.ink,flex:1}}>{dates.files?dateLabel(dates.files):'Все даты'}</Text><Text style={{color:color.muted}}>⌄</Text></Pressable>
      <FlatList ref={list} style={styles.fill} data={rows} keyExtractor={item=>item.id} contentContainerStyle={{paddingHorizontal:16,paddingBottom:16}} refreshing={loading} onRefresh={()=>void load()} onEndReached={()=>{if(cursor&&!loading)void load(true);}} onScroll={event=>{positions.current.files=event.nativeEvent.contentOffset.y;}} contentOffset={initialOffset} scrollEventThrottle={32}
        ListEmptyComponent={!loading?<Text style={{color:color.muted,paddingVertical:24}}>Нет файлов по выбранным условиям.</Text>:undefined}
        renderItem={({item})=>item.type==='date'?<Text style={[styles.dateTitle,ink]}>{dateLabel(item.date)}</Text>:documentRow(item.file)}/>
      <View style={[styles.actions,{borderTopWidth:1,borderColor:color.line}]}>{button('＋  Загрузить с устройства',pick)}</View>
    </>;
  }

  return <View style={[styles.fill,{backgroundColor:color.bg,paddingTop:screen==='viewer'?0:insets.top,paddingBottom:screen==='viewer'?0:insets.bottom}]}><StatusBar barStyle={dark?'light-content':'dark-content'}/>{body}{error&&screen!=='viewer'?<Pressable onPress={()=>load()} style={{padding:12}}><Text style={styles.error}>{error} · повторить</Text></Pressable>:null}{['gallery','files','queue'].includes(screen)?<View style={[styles.navigation,{borderColor:color.line}]}>{([['gallery','▦','Галерея'],['files','▤','Файлы'],['queue','↕','Передача']] as const).map(([target,icon,label])=><Pressable key={target} accessibilityRole="tab" accessibilityState={{selected:screen===target}} onPress={()=>go(target)} style={({pressed})=>[styles.navItem,{backgroundColor:pressed?color.surface:color.bg}]}><Text style={{fontSize:23,color:screen===target?color.accent:color.muted,fontWeight:screen===target?'700':'400'}}>{icon}</Text><Text style={{fontSize:12,color:screen===target?color.accent:color.muted,marginTop:4}}>{label}</Text></Pressable>)}</View>:null}<ActionSheet sheet={sheet} color={color} onClose={()=>setSheet(null)}/></View>;
}

const styles=StyleSheet.create({
  fill:{flex:1,minHeight:0},content:{padding:16},header:{flexDirection:'row',alignItems:'center',gap:8,paddingHorizontal:16,paddingVertical:12},title:{fontSize:24,fontWeight:'600',flex:1,minWidth:0},iconButton:{minWidth:48,minHeight:48,borderWidth:1,borderRadius:5,alignItems:'center',justifyContent:'center'},icon:{fontSize:27},text:{fontSize:15},small:{fontSize:12},input:{borderWidth:1,borderRadius:5,padding:12,marginHorizontal:16,marginVertical:8,fontSize:14},button:{minHeight:49,padding:13,borderRadius:5,alignItems:'center',justifyContent:'center',marginVertical:0},actions:{paddingHorizontal:16,paddingVertical:12},selectionActions:{flexDirection:'row',alignItems:'center',gap:8},toolbar:{flexDirection:'row',alignItems:'center',flexWrap:'wrap',gap:8},filters:{flexDirection:'row',gap:8,paddingHorizontal:16,paddingBottom:8},filter:{minHeight:44,alignItems:'center',justifyContent:'center',paddingHorizontal:8,borderWidth:1,borderRadius:6,minWidth:0},dateButton:{minHeight:44,paddingHorizontal:12,marginHorizontal:16,marginVertical:4,flexDirection:'row',alignItems:'center',gap:8,borderWidth:1,borderRadius:6},dateTitle:{fontSize:17,fontWeight:'600',marginTop:18,marginBottom:10},mediaRow:{flexDirection:'row'},videoLabel:{position:'absolute',right:7,bottom:5,color:'#fff',backgroundColor:'#0008',paddingHorizontal:4},row:{flexDirection:'row',alignItems:'center',minHeight:70,paddingVertical:12,borderBottomWidth:StyleSheet.hairlineWidth},navigation:{flexDirection:'row',borderTopWidth:StyleSheet.hairlineWidth},navItem:{flex:1,minHeight:66,alignItems:'center',justifyContent:'center'},queueItem:{paddingVertical:18,borderBottomWidth:1},error:{color:'#d95151',fontSize:13,lineHeight:20,marginVertical:8},loginTitle:{fontSize:35,fontWeight:'600',lineHeight:40,marginVertical:35},info:{padding:20,marginTop:20},code:{fontSize:32,letterSpacing:6,marginVertical:16},viewerImage:{position:'absolute',top:0,right:0,bottom:0,left:0},viewerTop:{position:'absolute',top:0,left:0,right:0,flexDirection:'row',justifyContent:'space-between',alignItems:'center',paddingHorizontal:12,backgroundColor:'#0007'},viewerBottom:{position:'absolute',bottom:0,left:0,right:0,padding:20,backgroundColor:'#0009'},
});
