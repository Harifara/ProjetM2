import { useState, useEffect } from 'react';
import { Plus, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';
import { AssignmentModal } from '@/components/rh/AssignmentModal';
import { StatusBadge } from '@/components/rh/StatusBadge';
import { useAuth } from '@/contexts/AuthContext';

export default function RHAssignments() {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [assignmentsData, employeesData, districtsData] = await Promise.all([
        rhApi.getAssignments(),
        rhApi.getEmployees(),
        rhApi.getDistricts(),
      ]);
      setAssignments(assignmentsData);
      setEmployees(employeesData);
      setDistricts(districtsData);
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
      await rhApi.validateAssignment(id, status);
      toast({ title: `Affectation ${status === 'approved' ? 'approuvée' : 'rejetée'}` });
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
          <h1 className="text-3xl font-bold text-foreground">Affectations</h1>
          <p className="text-muted-foreground mt-1">Gérez les affectations et mutations du personnel</p>
        </div>
        <Button onClick={() => setModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle affectation
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des Affectations</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employé</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Nouveau district</TableHead>
                <TableHead>Date début</TableHead>
                <TableHead>Date fin</TableHead>
                <TableHead>Statut</TableHead>
                {canValidate && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {assignments.map((assignment: any) => (
                <TableRow key={assignment.id}>
                  <TableCell className="font-medium">
                    {assignment.employee?.employee_number}
                  </TableCell>
                  <TableCell className="capitalize">{assignment.assignment_type}</TableCell>
                  <TableCell>{assignment.new_district?.name || '-'}</TableCell>
                  <TableCell>{new Date(assignment.start_date).toLocaleDateString('fr-FR')}</TableCell>
                  <TableCell>
                    {assignment.end_date ? new Date(assignment.end_date).toLocaleDateString('fr-FR') : 'Permanent'}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={assignment.status} type="assignment" />
                  </TableCell>
                  {canValidate && assignment.status === 'pending' && (
                    <TableCell className="text-right space-x-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleValidate(assignment.id, 'approved')}
                      >
                        <Check className="w-4 h-4 text-success" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleValidate(assignment.id, 'rejected')}
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

      <AssignmentModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={fetchData}
        employees={employees}
        districts={districts}
      />
    </div>
  );
}
