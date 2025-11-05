import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bell, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/hooks/use-toast';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'warning' | 'error' | 'info';
  read: boolean;
  createdAt: string;
}

export const NotificationDropdown = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { toast } = useToast();

  useEffect(() => {
    fetchNotifications();
    // Set up real-time notifications if needed
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/v1/notifications/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.results || []);
        setUnreadCount(data.results?.filter((n: Notification) => !n.read).length || 0);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(`/api/v1/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-destructive" />;
      default:
        return <Info className="w-4 h-4 text-info" />;
    }
  };

  // Function to show toast notifications
  const showNotification = (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => {
    toast({
      title,
      description: message,
      variant: type === 'error' ? 'destructive' : 'default',
    });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {notifications.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            Aucune notification
          </div>
        ) : (
          notifications.slice(0, 5).map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className="flex items-start space-x-3 p-3 cursor-pointer"
              onClick={() => markAsRead(notification.id)}
            >
              {getNotificationIcon(notification.type)}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {notification.title}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {notification.message}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(notification.createdAt).toLocaleDateString('fr-FR')}
                </p>
              </div>
              {!notification.read && (
                <div className="w-2 h-2 bg-primary rounded-full mt-1" />
              )}
            </DropdownMenuItem>
          ))
        )}
        
        {notifications.length > 5 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-center text-primary">
              Voir toutes les notifications
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

// Utility function to show toast notifications
export const showNotification = (type: 'success' | 'warning' | 'error' | 'info', title: string, message: string) => {
  // This will be implemented with the toast system
};