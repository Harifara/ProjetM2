import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import { rhApi } from '@/lib/api';

interface EmployeeModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  employee?: any;
  districts: any[];
}

export const EmployeeModal = ({ open, onClose, onSuccess, employee, districts }: EmployeeModalProps) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    employee_number: '',
    position: '',
    department: '',
    hire_date: '',
    status: 'active',
    district: '',
  });

  useEffect(() => {
    if (employee) {
      setFormData({
        employee_number: employee.employee_number || '',
        position: employee.position || '',
        department: employee.department || '',
        hire_date: employee.hire_date || '',
        status: employee.status || 'active',
        district: employee.district?.id || '',
      });
    } else {
      setFormData({
        employee_number: '',
        position: '',
        department: '',
        hire_date: '',
        status: 'active',
        district: '',
      });
    }
  }, [employee, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (employee) {
        await rhApi.updateEmployee(employee.id, formData);
        toast({ title: 'Employé modifié avec succès' });
      } else {
        await rhApi.createEmployee(formData);
        toast({ title: 'Employé créé avec succès' });
      }
      onSuccess();
      onClose();
    } catch (error: any) {
      toast({ title: 'Erreur', description: error.message, variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{employee ? 'Modifier l\'employé' : 'Nouvel employé'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="employee_number">Matricule</Label>
            <Input
              id="employee_number"
              value={formData.employee_number}
              onChange={(e) => setFormData({ ...formData, employee_number: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="position">Poste</Label>
            <Input
              id="position"
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="department">Département</Label>
            <Input
              id="department"
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="hire_date">Date d'embauche</Label>
            <Input
              id="hire_date"
              type="date"
              value={formData.hire_date}
              onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Statut</Label>
            <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Actif</SelectItem>
                <SelectItem value="on_leave">En congé</SelectItem>
                <SelectItem value="suspended">Suspendu</SelectItem>
                <SelectItem value="terminated">Terminé</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="district">District</Label>
            <Select value={formData.district} onValueChange={(value) => setFormData({ ...formData, district: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner un district" />
              </SelectTrigger>
              <SelectContent>
                {districts.map((d) => (
                  <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Annuler</Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
