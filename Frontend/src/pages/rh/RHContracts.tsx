import { useState, useEffect } from 'react';
import { Plus, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';
import { ContractModal } from '@/components/rh/ContractModal';
import { StatusBadge } from '@/components/rh/StatusBadge';
import { useAuth } from '@/contexts/AuthContext';

export default function RHContracts() {
  const { user } = useAuth();
  const [contracts, setContracts] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [contractsData, employeesData] = await Promise.all([
        rhApi.getContracts(),
        rhApi.getEmployees(),
      ]);
      setContracts(contractsData);
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

  const canEdit = user?.role === 'admin' || user?.role === 'responsable_rh';

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
          <h1 className="text-3xl font-bold text-foreground">Gestion des Contrats</h1>
          <p className="text-muted-foreground mt-1">Gérez les contrats du personnel</p>
        </div>
        {canEdit && (
          <Button onClick={() => { setSelectedContract(null); setModalOpen(true); }}>
            <Plus className="w-4 h-4 mr-2" />
            Nouveau contrat
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des Contrats</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employé</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Date début</TableHead>
                <TableHead>Date fin</TableHead>
                <TableHead>Salaire</TableHead>
                <TableHead>Statut</TableHead>
                {canEdit && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {contracts.map((contract: any) => (
                <TableRow key={contract.id}>
                  <TableCell className="font-medium">
                    {contract.employee?.employee_number} - {contract.employee?.position}
                  </TableCell>
                  <TableCell>{contract.contract_type}</TableCell>
                  <TableCell>{new Date(contract.start_date).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell>
                    {contract.end_date ? new Date(contract.end_date).toLocaleDateString('fr-FR') : 'Indéterminé'}
                  </TableCell>
                  <TableCell>{parseFloat(contract.salary).toLocaleString('fr-FR')} MGA</TableCell>
                  <TableCell>
                    <StatusBadge status={contract.status} type="contract" />
                  </TableCell>
                  {canEdit && (
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => { setSelectedContract(contract); setModalOpen(true); }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <ContractModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={fetchData}
        employees={employees}
        contract={selectedContract}
      />
    </div>
  );
}
