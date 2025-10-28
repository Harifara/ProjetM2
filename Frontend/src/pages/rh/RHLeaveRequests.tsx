import { useState, useEffect } from 'react';
import { Plus, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';
import { LeaveRequestModal } from '@/components/rh/LeaveRequestModal';
import { StatusBadge } from '@/components/rh/StatusBadge';
import { useAuth } from '@/contexts/AuthContext';

export default function RHLeaveRequests() {
  const { user } = useAuth();
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [requestsData, employeesData] = await Promise.all([
        rhApi.getLeaveRequests(),
        rhApi.getEmployees(),
      ]);
      setLeaveRequests(requestsData);
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

  const handleValidate = async (id: string, status: string) => {
    try {
      await rhApi.validateLeaveRequest(id, status);
      toast({ title: `Demande ${status === 'approved' ? 'approuvée' : 'rejetée'}` });
      fetchData();
    } catch (error: any) {
      toast({ title: 'Erreur', description: error.message, variant: 'destructive' });
    }
  };

  const canValidate = user?.role === 'admin' || user?.role === 'responsable_rh';

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
          <h1 className="text-3xl font-bold text-foreground">Demandes de Congé</h1>
          <p className="text-muted-foreground mt-1">Gérez les demandes de congé du personnel</p>
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
                <TableHead>Date début</TableHead>
                <TableHead>Date fin</TableHead>
                <TableHead>Motif</TableHead>
                <TableHead>Statut</TableHead>
                {canValidate && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {leaveRequests.map((request: any) => (
                <TableRow key={request.id}>
                  <TableCell className="font-medium">
                    {request.employee?.employee_number}
                  </TableCell>
                  <TableCell className="capitalize">{request.leave_type}</TableCell>
                  <TableCell>{new Date(request.start_date).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell>{new Date(request.end_date).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell className="max-w-xs truncate">{request.reason}</TableCell>
                  <TableCell>
                    <StatusBadge status={request.status} type="leave" />
                  </TableCell>
                  {canValidate && request.status === 'pending' && (
                    <TableCell className="text-right space-x-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleValidate(request.id, 'approved')}
                      >
                        <Check className="w-4 h-4 text-success" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleValidate(request.id, 'rejected')}
                      >
                        <X className="w-4 h-4 text-destructive" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <LeaveRequestModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={fetchData}
        employees={employees}
      />
    </div>
  );
}
