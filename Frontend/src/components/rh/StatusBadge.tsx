import { Badge } from '@/components/ui/badge';

interface StatusBadgeProps {
  status: string;
  type?: 'employee' | 'contract' | 'leave' | 'assignment' | 'payment' | 'purchase';
}

export const StatusBadge = ({ status, type = 'employee' }: StatusBadgeProps) => {
  const getVariant = () => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'approved':
      case 'validated':
      case 'paid':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'rejected':
      case 'terminated':
      case 'expired':
      case 'cancelled':
        return 'destructive';
      case 'on_leave':
      case 'suspended':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const getLabel = () => {
    const labels: Record<string, string> = {
      active: 'Actif',
      on_leave: 'En congé',
      suspended: 'Suspendu',
      terminated: 'Terminé',
      pending: 'En attente',
      approved: 'Approuvé',
      rejected: 'Rejeté',
      validated: 'Validé',
      paid: 'Payé',
      expired: 'Expiré',
      cancelled: 'Annulé',
    };
    return labels[status.toLowerCase()] || status;
  };

  return <Badge variant={getVariant()}>{getLabel()}</Badge>;
};
