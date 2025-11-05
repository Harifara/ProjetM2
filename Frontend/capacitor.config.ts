import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'app.lovable.296a2c1b513048ac926b0023bec7642a',
  appName: 'colorease-dashboard',
  webDir: 'dist',
  server: {
    url: 'https://296a2c1b-5130-48ac-926b-0023bec7642a.lovableproject.com?forceHideBadge=true',
    cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#228B22',
      showSpinner: false,
      androidSpinnerStyle: 'small',
      iosSpinnerStyle: 'small',
      spinnerColor: '#ffffff'
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#228B22'
    }
  }
};

export default config;