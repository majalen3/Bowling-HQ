import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.bowlinghq.app',
  appName: 'Bowling HQ',
  webDir: 'dist',
  server: {
    // Use HTTPS scheme on Android; iOS always uses https
    androidScheme: 'https',
  },
};

export default config;
