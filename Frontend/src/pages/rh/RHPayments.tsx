import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';
import { PaymentRequestModal } from '@/components/rh/PaymentRequestModal';
import { StatusBadge } from '@/components/rh/StatusBadge';

export default function RHPayments() {
  const [paymentRequests, setPaymentRequests] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [paymentsData, employeesData] = await Promise.all([
        rhApi.getPaymentRequests(),
        rhApi.getEmployees(),
      ]);
      setPaymentRequests(paymentsData);
      setEmployees(employeesData);
    } catch (error: any) {
      toast({ title: 'Erreur', description: error.message, variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Demandes de Paiement</h1>
          <p className="text-muted-foreground mt-1">Gérez les demandes de paiement du personnel</p>
        </div>
        <Button onClick={() => setModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle demande
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des Demandes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employé</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Montant</TableHead>
                <TableHead>Motif</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Statut</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paymentRequests.map((payment: any) => (
                <TableRow key={payment.id}>
                  <TableCell className="font-medium">
                    {payment.employee?.employee_number}
                  </TableCell>
                  <TableCell className="capitalize">{payment.payment_type}</TableCell>
                  <TableCell>{parseFloat(payment.amount).toLocaleString('fr-FR')} MGA</TableCell>
                  <TableCell className="max-w-xs truncate">{payment.reason}</TableCell>
                  <TableCell>{new Date(payment.created_at).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell>
                    <StatusBadge status={payment.status} type="payment" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PaymentRequestModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={fetchData}
        employees={employees}
      />
    </div>
  );
}
