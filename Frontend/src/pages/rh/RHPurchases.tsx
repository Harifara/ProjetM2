import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';
import { PurchaseRequestModal } from '@/components/rh/PurchaseRequestModal';
import { StatusBadge } from '@/components/rh/StatusBadge';

export default function RHPurchases() {
  const [purchaseRequests, setPurchaseRequests] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [purchasesData, employeesData] = await Promise.all([
        rhApi.getPurchaseRequests(),
        rhApi.getEmployees(),
      ]);
      setPurchaseRequests(purchasesData);
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
          <h1 className="text-3xl font-bold text-foreground">Demandes d'Achat</h1>
          <p className="text-muted-foreground mt-1">Gérez les demandes d'achat du personnel</p>
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
                <TableHead>Article</TableHead>
                <TableHead>Quantité</TableHead>
                <TableHead>Coût estimé</TableHead>
                <TableHead>Département</TableHead>
                <TableHead>Justification</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Statut</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {purchaseRequests.map((purchase: any) => (
                <TableRow key={purchase.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {purchase.item_description}
                  </TableCell>
                  <TableCell>{purchase.quantity}</TableCell>
                  <TableCell>{parseFloat(purchase.estimated_cost).toLocaleString('fr-FR')} MGA</TableCell>
                  <TableCell>{purchase.department}</TableCell>
                  <TableCell className="max-w-xs truncate">{purchase.justification}</TableCell>
                  <TableCell>{new Date(purchase.created_at).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell>
                    <StatusBadge status={purchase.status} type="purchase" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <PurchaseRequestModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={fetchData}
        employees={employees}
      />
    </div>
  );
}
