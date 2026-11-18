import React, {memo} from 'react';
import {ActivityIndicator, Pressable, StyleSheet, Text, View, requireNativeComponent, type NativeSyntheticEvent, type ViewProps} from 'react-native';

export interface GridPalette {bg:string;surface:string;ink:string;muted:string;line:string;accent:string;buttonInk:string}
export interface MediaGridItem {id:string;label:string;uri?:string;video?:boolean;heading?:boolean}
export interface GridAnchor {id:string;offset:number}
interface NativeGridProps extends ViewProps {
  items:readonly MediaGridItem[];columns:number;palette:GridPalette;selectedIds?:readonly string[];
  selectable:boolean;selectionAvailable:boolean;selectionLocked:boolean;hasMore:boolean;refreshing:boolean;
  anchor?:GridAnchor;catalogKey?:string;onPositionChange?:(event:NativeSyntheticEvent<GridAnchor>)=>void;
  onOpen?:(event:NativeSyntheticEvent<{id:string}>)=>void;
  onColumnsChange:(event:NativeSyntheticEvent<{columns:number}>)=>void;
  onSelectionChange?:(event:NativeSyntheticEvent<{ids:string[]}>)=>void;
  onLoadMore:()=>void;onRefresh:()=>void;
}
const NativeGrid=requireNativeComponent<NativeGridProps>('StorageMediaGrid');

export const MediaGrid=memo(function MediaGrid({items,columns,color,selectedIds,onSelectionChange,selectionMode,selectionLocked=false,onColumnsChange,onOpen,hasMore,loading,onLoadMore,onRefresh,anchor,onPositionChange,catalogKey,emptyText='Нет фото и видео.'}: {
  items:readonly MediaGridItem[];columns:number;color:GridPalette;selectedIds?:readonly string[];
  onSelectionChange?:(ids:string[])=>void;onColumnsChange:(columns:number)=>void;onOpen?:(id:string)=>void;
  selectionMode?:boolean;
  selectionLocked?:boolean;
  hasMore:boolean;loading:boolean;onLoadMore:()=>void;onRefresh:()=>void;emptyText?:string;
  anchor?:GridAnchor;onPositionChange?:(anchor:GridAnchor)=>void;catalogKey?:string;
}) {
  return <View style={styles.fill}>
    <NativeGrid style={styles.fill} items={items} columns={columns} palette={color}
      anchor={anchor} catalogKey={catalogKey} onPositionChange={event=>onPositionChange?.(event.nativeEvent)}
      selectedIds={selectedIds} selectable={selectionMode??!!onSelectionChange} selectionAvailable={!!onSelectionChange} selectionLocked={selectionLocked} hasMore={hasMore} refreshing={loading&&items.length===0}
      onColumnsChange={event=>onColumnsChange(event.nativeEvent.columns)}
      onSelectionChange={event=>onSelectionChange?.(event.nativeEvent.ids)} onOpen={event=>onOpen?.(event.nativeEvent.id)}
      onLoadMore={onLoadMore} onRefresh={onRefresh}/>
    {!items.length?<View pointerEvents="none" style={styles.empty}>{loading?<ActivityIndicator color={color.accent}/>:<Text style={{color:color.muted,textAlign:'center'}}>{emptyText}</Text>}</View>:null}
  </View>;
});

export function GridControls({columns,onChange,color}: {columns:number;onChange:(value:number)=>void;color:GridPalette}) {
  return <View style={styles.controls}>
    <Text style={{color:color.muted,flex:1,flexShrink:1}}>Сетка · {columns} в ряд</Text>
    {([-1,1] as const).map(direction=>{
      const disabled=direction<0?columns<=2:columns>=6;
      return <Pressable key={direction} accessibilityRole="button" accessibilityLabel={direction<0?'Увеличить миниатюры':'Уменьшить миниатюры'} disabled={disabled}
        onPress={()=>onChange(columns+direction)} style={({pressed})=>[styles.control,{backgroundColor:color.surface,borderColor:color.line,opacity:disabled?0.35:pressed?0.65:1}]}>
        <Text style={{color:color.ink,fontSize:22}}>{direction<0?'−':'＋'}</Text>
      </Pressable>;
    })}
  </View>;
}
const styles=StyleSheet.create({
  fill:{flex:1,minHeight:0},empty:{position:'absolute',top:0,bottom:0,left:0,right:0,alignItems:'center',justifyContent:'center',padding:24},
  controls:{flexDirection:'row',alignItems:'center',gap:8,paddingHorizontal:16,paddingVertical:8},
  control:{width:44,height:44,borderWidth:1,borderRadius:6,alignItems:'center',justifyContent:'center'},
});
