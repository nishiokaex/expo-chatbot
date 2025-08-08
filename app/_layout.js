import React from 'react';
import { Tabs } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import { MaterialIcons } from '@expo/vector-icons';

// Material Design 3のテーマ設定
const theme = {
  colors: {
    primary: '#2196F3',
    onPrimary: '#FFFFFF',
    primaryContainer: '#E3F2FD',
    onPrimaryContainer: '#0D47A1',
    secondary: '#03DAC6',
    onSecondary: '#000000',
    secondaryContainer: '#B2DFDB',
    onSecondaryContainer: '#004D40',
    tertiary: '#FF9800',
    onTertiary: '#FFFFFF',
    tertiaryContainer: '#FFE0B2',
    onTertiaryContainer: '#E65100',
    error: '#F44336',
    onError: '#FFFFFF',
    errorContainer: '#FFEBEE',
    onErrorContainer: '#C62828',
    background: '#FFFFFF',
    onBackground: '#000000',
    surface: '#FFFFFF',
    onSurface: '#000000',
    surfaceVariant: '#F5F5F5',
    onSurfaceVariant: '#424242',
    outline: '#757575',
    outlineVariant: '#E0E0E0',
    shadow: '#000000',
    scrim: '#000000',
    inverseSurface: '#121212',
    inverseOnSurface: '#FFFFFF',
    inversePrimary: '#90CAF9',
    surfaceDisabled: '#F5F5F5',
    onSurfaceDisabled: '#BDBDBD',
  },
};

export default function RootLayout() {
  return (
    <PaperProvider theme={theme}>
      <StatusBar style="light" backgroundColor={theme.colors.primary} />
      <Tabs
        screenOptions={{
          headerStyle: {
            backgroundColor: theme.colors.primary,
          },
          headerTintColor: theme.colors.onPrimary,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.outline,
          tabBarStyle: {
            backgroundColor: theme.colors.surface,
          },
        }}
      >
        <Tabs.Screen 
          name='index' 
          options={{
            title: 'チャット',
            tabBarIcon: ({ color, size }) => (
              <MaterialIcons name="chat" size={size} color={color} />
            ),
          }} 
        />
        <Tabs.Screen 
          name='settings' 
          options={{
            title: 'URL設定',
            tabBarIcon: ({ color, size }) => (
              <MaterialIcons name="settings" size={size} color={color} />
            ),
          }} 
        />
      </Tabs>
    </PaperProvider>
  );
}