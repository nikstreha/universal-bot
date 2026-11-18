import React, {useEffect, useRef} from 'react';
import {Animated, Modal, Pressable, ScrollView, StyleSheet, Text, View} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import type {GridPalette} from './MediaGrid';

export interface ActionSheetModel {title:string;items:{label:string;action?:()=>void}[]}

export function ActionSheet({sheet,color,onClose}: {sheet:ActionSheetModel|null;color:GridPalette;onClose:()=>void}) {
  const insets=useSafeAreaInsets(),progress=useRef(new Animated.Value(0)).current,closing=useRef(false);
  const visible=sheet!==null;
  useEffect(()=>{
    if(!visible){progress.setValue(0);return;}
    closing.current=false;
    Animated.timing(progress,{toValue:1,duration:160,useNativeDriver:true}).start();
    return()=>progress.stopAnimation();
  },[visible,progress]);
  const close=(action?:()=>void)=>{
    if(closing.current)return;closing.current=true;
    Animated.timing(progress,{toValue:0,duration:120,useNativeDriver:true}).start(({finished})=>{
      if(!finished)return;
      onClose();
      if(action)requestAnimationFrame(action);
    });
  };
  return <Modal transparent visible={visible} animationType="none" onRequestClose={()=>close()} statusBarTranslucent>
    <View style={[styles.overlay,{paddingTop:insets.top+24}]}>
      <Animated.View pointerEvents="none" style={[StyleSheet.absoluteFill,{backgroundColor:'#0008',opacity:progress}]}/>
      <Pressable accessibilityRole="button" accessibilityLabel="Закрыть меню" onPress={()=>close()} style={StyleSheet.absoluteFill}/>
      <Animated.View style={[styles.sheet,{backgroundColor:color.bg,paddingBottom:Math.max(16,insets.bottom),opacity:progress,transform:[{translateY:progress.interpolate({inputRange:[0,1],outputRange:[16,0]})}]}]}>
        <Text numberOfLines={2} style={[styles.title,{color:color.ink}]}>{sheet?.title}</Text>
        <ScrollView style={styles.list} contentContainerStyle={{paddingBottom:8}}>{sheet?.items.map((item,index)=>item.action?
          <Pressable key={index} accessibilityRole="button" onPress={()=>close(item.action)} style={({pressed})=>[styles.item,{borderColor:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]}>
            <Text style={{color:color.ink,flex:1,flexShrink:1,lineHeight:22}}>{item.label}</Text><Text style={{color:color.muted,fontSize:20}}>›</Text>
          </Pressable>:<Text key={index} style={{color:color.muted,lineHeight:22,paddingVertical:12}}>{item.label}</Text>
        )}</ScrollView>
        <Pressable accessibilityRole="button" onPress={()=>close()} style={({pressed})=>[styles.close,{borderColor:color.line,backgroundColor:color.surface,opacity:pressed?0.65:1}]}><Text style={{color:color.ink,fontWeight:'600'}}>Закрыть</Text></Pressable>
      </Animated.View>
    </View>
  </Modal>;
}
const styles=StyleSheet.create({
  overlay:{flex:1,justifyContent:'flex-end'},sheet:{maxHeight:'100%',flexShrink:1,padding:16,borderTopLeftRadius:16,borderTopRightRadius:16},
  title:{fontSize:22,fontWeight:'600',lineHeight:28,marginBottom:16},list:{flexGrow:0,flexShrink:1},
  item:{minHeight:52,flexDirection:'row',gap:12,alignItems:'center',padding:12,borderWidth:1,borderRadius:6,marginBottom:8},
  close:{minHeight:48,borderWidth:1,borderRadius:6,alignItems:'center',justifyContent:'center'},
});
